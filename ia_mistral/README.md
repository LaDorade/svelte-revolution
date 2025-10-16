# Documentation du Système de Narration IA

## 📖 Vue d'ensemble

Ce système permet de créer des **récits interactifs pilotés par l'intelligence artificielle**. Il surveille en temps réel les contributions des joueurs dans une base de données PocketBase et déclenche automatiquement des événements narratifs (trigger nodes) en fonction du contenu de leurs messages.

Le système fonctionne avec **trois composants principaux** :

1. **`session_watcher.py`** - Le surveillant qui détecte l'activité dans les sessions
2. **`ai_session.py`** - Le gestionnaire de session qui orchestre le récit
3. **`mistral_client.py`** - Le client IA qui analyse et génère du contenu

---

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                     PocketBase Database                      │
│  Collections: Session, Node, Scenario, TriggerNodes          │
└──────────────────┬──────────────────────────────────────────┘
                   │ Real-time subscription
                   ▼
         ┌─────────────────────┐
         │ session_watcher.py  │  ← Point d'entrée principal
         │  (Surveillance)     │
         └──────────┬──────────┘
                    │ Détecte nouvelle activité
                    │ Crée et lance un thread pour chaque session
                    ▼
         ┌─────────────────────┐
         │   ai_session.py     │  ← Gestion du récit
         │  (Thread par        │
         │   session)          │
         └──────────┬──────────┘
                    │ Envoie les contributions
                    │ des joueurs pour analyse
                    ▼
         ┌─────────────────────┐
         │ mistral_client.py   │  ← Analyse IA
         │  (API Mistral AI)   │
         └──────────┬──────────┘
                    │ Retourne les triggers à déclencher
                    │ ou du texte de conclusion
                    ▼
         ┌─────────────────────┐
         │   ai_session.py     │
         │ Crée les nodes      │
         │ événements          │
         └─────────────────────┘
```

---

## 🔍 Composant 1 : `session_watcher.py`

### Rôle
C'est le **chef d'orchestre** du système. Il surveille en permanence la collection `Node` de PocketBase et gère le cycle de vie des sessions IA actives.

### Fonctionnement détaillé

#### 1. Initialisation
```python
def main():
    # Connexion à PocketBase
    client = PocketBase("https://db.babel-revolution.fr")
    client.admins.auth_with_password(PB_LOGIN, PB_PASSWORD)
    
    # Écoute les changements dans la collection Node
    client.collection("Node").subscribe(handler)
```

#### 2. Détection d'activité
Quand un nouveau `Node` est créé, la fonction `on_node_change()` :

1. **Vérifie que le node appartient à une session valide**
   ```python
   session = get_session_from_record(event.record, client)
   ```

2. **Vérifie que la session utilise un scénario IA**
   ```python
   if not session_has_ai_scenario(session, client):
       return  # Ignore les sessions sans IA
   ```

3. **Vérifie que la session n'est pas déjà complétée**
   ```python
   if getattr(session, 'completed', False):
       return  # Ne réactive pas une session terminée
   ```

#### 3. Gestion multi-threading
Le système maintient une liste de sessions actives avec protection thread-safe :

```python
active_ai_sessions: list[tuple[Record, AISession, int, threading.Thread]] = []
active_ai_sessions_lock = threading.Lock()  # Protection contre les accès concurrents
```

Chaque élément contient :
- `Record` : L'enregistrement de la session
- `AISession` : L'instance de gestion du récit
- `int` : Timestamp de la dernière activité
- `Thread` : Le thread d'exécution

#### 4. Création ou mise à jour de session
```python
with active_ai_sessions_lock:  # Verrouillage pour la sécurité thread
    # Si la session existe déjà, met à jour son timestamp
    for i, (sess_record, ai_sess, last_active, thread) in enumerate(active_ai_sessions):
        if getattr(sess_record, 'id', None) == session_id:
            active_ai_sessions[i] = (sess_record, ai_sess, int(time.time()), thread)
            return
    
    # Sinon, crée une nouvelle instance AISession dans son propre thread
    ai_session = AISession(session, client)
    thread = threading.Thread(target=ai_session.start, daemon=True)
    thread.start()
    active_ai_sessions.append((session, ai_session, int(time.time()), thread))
```

#### 5. Nettoyage automatique
Une boucle principale vérifie régulièrement les sessions :

- **Sessions complétées** : Détectées via `session.completed = True`
- **Sessions supprimées** : La session n'existe plus dans la base
- **Sessions inactives** : Aucune activité depuis `INACTIVE_TIMEOUT` secondes (600s par défaut)

```python
while True:
    with active_ai_sessions_lock:
        i = 0
        while i < len(active_ai_sessions):
            # Vérifie si complétée, supprimée ou inactive
            if should_remove:
                ai_session.stop()  # Arrête proprement l'instance
                active_ai_sessions.pop(i)  # Retire de la liste
            else:
                i += 1
    time.sleep(1)
```

### Configuration
- `INACTIVE_TIMEOUT = 600` : Temps d'inactivité avant désactivation (en secondes)
- `CHECK_INTERVAL = 30` : Intervalle d'affichage du statut des sessions (en secondes)

---

## 🎭 Composant 2 : `ai_session.py`

### Rôle
Gère le **déroulement narratif** d'une session de jeu. Chaque instance `AISession` fonctionne dans son propre thread et orchestre :
- La détection de nouvelles contributions des joueurs
- L'évaluation des triggers à activer
- La création d'événements narratifs
- La conclusion du récit

### Structure de données

#### Fichiers de persistance
Chaque session génère deux fichiers JSON dans `sessions_data/` :

1. **`session_{id}.json`** : Historique des nodes traités
   ```json
   {
     "node_xyz123": {
       "id": "node_xyz123",
       "title": "Une découverte",
       "text": "Nous avons trouvé une carte au trésor !",
       "author": "Alice",
       "parent": "node_abc456",
       "side": "activites"
     }
   }
   ```

2. **`triggered_nodes_{id}.json`** : Liste des triggers déjà déclenchés
   ```json
   ["trigger_1", "trigger_5", "trigger_12"]
   ```

#### Attributs de classe
```python
self.trigger_nodes           # Tous les triggers possibles du scénario
self.triggered_nodes         # Triggers déjà activés
self.available_trigger_nodes # Triggers actuellement disponibles (conditions OK)
self.processed_nodes         # Nodes des joueurs déjà traités
self.pending_batch           # Nodes en attente d'analyse par l'IA
```

### Cycle de vie d'une session

#### 1. Initialisation
```python
ai_session = AISession(session, pb_client)
```

Charge depuis PocketBase :
- Les informations de la session
- Le scénario associé
- Les trigger nodes du scénario

Charge depuis les fichiers locaux :
- Les nodes déjà traités
- Les triggers déjà activés

#### 2. Démarrage de la boucle de traitement
```python
def start_processing_loop(self):
    while self.active:
        # 1. Récupère les nouveaux nodes (contributions des joueurs)
        new_nodes = self.fetch_new_nodes()
        
        # 2. Les ajoute au batch en attente
        if new_nodes:
            self.pending_batch.extend(new_nodes)
        
        # 3. Traite le batch si non vide
        if self.pending_batch:
            self.process_pending_batch()
        
        # 4. Pause de 5 secondes avant la prochaine itération
        time.sleep(5)
```

#### 3. Récupération des nouveaux nodes
```python
def fetch_new_nodes(self) -> list[dict]:
    nodes_records = self.pb_client.collection("Node").get_list(
        query_params={'filter': f'session="{self.session_id}"', 'perPage': 50}
    )
    
    new_nodes = []
    for record in nodes_records.items:
        node_id = getattr(record, 'id', None)
        # Ignore les nodes déjà traités
        if node_id and node_id not in self.processed_nodes:
            # Ne garde que les contributions des joueurs (pas le Narrator)
            if getattr(record, 'type') == "contribution" and \
               getattr(record, 'author') != "Narrator":
                new_nodes.append({...})
    
    return new_nodes
```

#### 4. Traitement du batch avec Mistral
```python
def process_pending_batch(self):
    # Construit un objet JSON avec les nodes et les triggers disponibles
    nodes_dict = {}
    for node in self.pending_batch:
        nodes_dict[node_id] = {
            "title": node["title"],
            "text": node["text"],
            "available_triggers": {
                "trigger_1": ["démarrer le moteur"],
                "trigger_2": ["faire le petit train"]
            }
        }
    
    # Envoie à Mistral pour analyse
    result = ask_mistral(json.dumps(nodes_dict))
```

Mistral retourne une évaluation structurée (voir section Mistral Client).

#### 5. Déclenchement des triggers
Pour chaque trigger évalué comme `should_get_triggered: true` :

```python
def trigger_node(self, trigger_id: str, parent_node_id: str):
    # Récupère les données du trigger
    trigger_node = next((node for node in self.trigger_nodes 
                        if node.get("id") == trigger_id), None)
    
    # Crée un nouveau node "event" dans PocketBase
    new_node_data = {
        "title": trigger_node["title"],
        "text": trigger_node["text"],
        "author": trigger_node["author"],
        "session": self.session_id,
        "parent": parent_node_id,
        "type": "event"  # Type événement (vs contribution)
    }
    self.pb_client.collection("Node").create(new_node_data)
    
    # Si c'est un trigger final, lance la conclusion
    if trigger_node.get("is_final", False):
        self.handle_final_node()
```

#### 6. Gestion de la conclusion (`handle_final_node()`)

Quand un trigger final est déclenché :

1. **Collecte les derniers messages** pendant 60 secondes
   ```python
   wait_time = 60
   while iterations < max_iterations:
       time.sleep(30)
       new_nodes.extend(self.fetch_new_nodes())
   ```

2. **Prépare un prompt avec les derniers messages**
   ```python
   nodes_for_prompt = [
       {"author": node["author"], "text": node["text"], "side": node["side"]}
       for node in new_nodes
   ]
   prompt = json.dumps(nodes_for_prompt)
   ```

3. **Demande à Mistral de générer une conclusion**
   ```python
   final_message = ask_mistral(prompt, context_file=FINAL_PROMPT_CONTEXT_FILE)
   ```

4. **Crée le node final et marque la session comme complétée**
   ```python
   final_node_data = {
       "title": "The End",
       "text": final_message,
       "author": "Narrator",
       "type": "event"
   }
   self.pb_client.collection("Node").create(final_node_data)
   self.pb_client.collection("Session").update(self.session_id, {"completed": True})
   self.stop()
   ```

### Gestion des triggers disponibles

Les triggers ont des **conditions** qui déterminent quand ils deviennent disponibles :

```python
def get_available_trigger_nodes(self):
    available_triggers = []
    for trigger_node in self.trigger_nodes:
        trigger_id = trigger_node["id"]
        
        # Ignore si déjà déclenché
        if trigger_id in self.triggered_nodes:
            continue
        
        conditions = trigger_node.get("conditions", [])
        
        # Disponible si pas de conditions ou "first" dans conditions
        if not conditions or "first" in conditions:
            available_triggers.append((trigger_id, triggers))
            continue
        
        # Disponible si toutes les conditions (autres triggers) sont remplies
        if all(cond in self.triggered_nodes for cond in conditions):
            available_triggers.append((trigger_id, triggers))
    
    return available_triggers
```

**Exemple** : Un trigger "Révélation finale" pourrait avoir :
```json
{
  "id": "trigger_final",
  "conditions": ["trigger_1", "trigger_2", "trigger_3"],
  "triggers": ["révéler le secret"],
  "is_final": true
}
```
Il ne sera disponible qu'après activation des triggers 1, 2 et 3.

---

## 🤖 Composant 3 : `mistral_client.py`

### Rôle
Interface avec l'**API Mistral AI** pour :
1. **Analyser les contributions** des joueurs et déterminer quels triggers activer
2. **Générer la conclusion** narrative de la session

### Modèles Pydantic

Pour garantir la cohérence des données, le système utilise Pydantic :

```python
class TriggerEvaluation(BaseModel):
    trigger_node_id: str           # ID du trigger évalué
    should_get_triggered: bool     # Doit-il être déclenché ?
    justification: str             # Explication de la décision

class TriggerEvaluationBatch(RootModel):
    root: Dict[str, Dict[str, TriggerEvaluation]]
    # Structure: { "node_id": { "trigger_id": TriggerEvaluation } }
```

### Fonction principale : `ask_mistral()`

```python
def ask_mistral(prompt: str, context_file=BATCH_PROMPT_CONTEXT_FILE):
    """
    Envoie un prompt à Mistral AI avec un contexte d'instructions.
    
    Args:
        prompt: Les données à analyser (JSON des nodes ou messages)
        context_file: Fichier contenant les instructions pour l'IA
        
    Returns:
        - TriggerEvaluationBatch si context_file = BATCH_PROMPT_CONTEXT_FILE
        - str (texte narratif) si context_file = FINAL_PROMPT_CONTEXT_FILE
        - None en cas d'erreur
    """
```

### Mode 1 : Évaluation des triggers

**Entrée** : JSON avec nodes et triggers disponibles
```json
{
  "node_xyz": {
    "title": "Exploration du temple",
    "text": "Nous entrons dans un temple ancien...",
    "available_triggers": {
      "trigger_1": ["entrer dans le temple", "pénétrer dans le sanctuaire"],
      "trigger_2": ["trouver une clé", "découvrir un indice"]
    }
  }
}
```

**Contexte** : Chargé depuis `mistral_batch_prompt.txt`
- Instructions détaillées sur comment analyser les nodes
- Format de réponse attendu
- Exemples concrets

**Appel API** :
```python
chat_response = client.chat.complete(
    model="mistral-tiny",
    response_format={"type": "json_object"},  # Force une réponse JSON
    messages=[UserMessage(content=INSTRUCTION_CONTEXT + "\n" + prompt)]
)
```

**Sortie** : Objet `TriggerEvaluationBatch` validé
```json
{
  "node_xyz": {
    "trigger_1": {
      "trigger_node_id": "trigger_1",
      "should_get_triggered": true,
      "justification": "Le texte mentionne explicitement l'entrée dans un temple."
    },
    "trigger_2": {
      "trigger_node_id": "trigger_2",
      "should_get_triggered": false,
      "justification": "Aucune mention de clé ou d'indice dans le message."
    }
  }
}
```

**Validation** :
```python
response_content = chat_response.choices[0].message.content
evaluation_batch = TriggerEvaluationBatch.model_validate_json(response_content)
# Si la validation échoue, retourne None
```

### Mode 2 : Génération de conclusion

**Entrée** : JSON avec les derniers messages des joueurs
```json
[
  {
    "author": "Alice",
    "text": "Nous avons vaincu le dragon et récupéré le trésor !",
    "side": "activites"
  },
  {
    "author": "Bob",
    "text": "Rentrons au village célébrer notre victoire.",
    "side": "rocops"
  }
]
```

**Contexte** : Chargé depuis `mistral_final_prompt.txt`
- Description de l'univers narratif (Sun Wukong)
- Consignes pour la conclusion (ton, longueur, langue)
- Rappel que c'est la fin du récit

**Appel API** :
```python
chat_response = client.chat.complete(
    model="mistral-tiny",
    # Pas de response_format, on veut du texte libre
    messages=[UserMessage(content=INSTRUCTION_CONTEXT + "\n" + prompt)]
)
```

**Sortie** : Texte narratif (string)
```
The disciples return to their village, carrying not just the legendary 
treasure, but the bonds forged through their shared adventure. As they 
celebrate under the moonlight, Master Wukong watches from afar, proud 
of their growth and courage.
```

### Gestion des erreurs

Le système est robuste face aux erreurs :

```python
# Validation des entrées
if not MISTRAL_API_KEY:
    utils.log_message("[Mistral] Clé API manquante", LOG_FILE_NAME)
    return None

if not prompt or not prompt.strip():
    utils.log_message("[Mistral] Prompt vide", LOG_FILE_NAME)
    return None

# Gestion des réponses fragmentées
if isinstance(response_content, list):
    response_content = "".join(str(chunk) for chunk in response_content)

# Validation Pydantic
try:
    evaluation_batch = TriggerEvaluationBatch.model_validate_json(response_content)
    utils.log_message("[Mistral] Validation réussie", LOG_FILE_NAME)
    return evaluation_batch
except Exception as e:
    utils.log_message(f"[Mistral] Erreur de validation: {e}", LOG_FILE_NAME)
    return None
```

### Fichiers de contexte

#### `mistral_batch_prompt.txt`
Contient les instructions pour l'analyse des triggers :
- Format d'entrée attendu
- Critères d'évaluation (synonymes, références)
- Format de sortie avec schéma Pydantic
- Exemples concrets

#### `mistral_final_prompt.txt`
Contient les instructions pour la conclusion :
- Univers narratif (Sun Wukong et ses disciples)
- Objectif de la quête (Rúyì Jīngū Bàng)
- Consignes de rédaction (longueur, ton, langue)
- Importance de la fermeture narrative

---

## 📊 Flux de données complet

Voici un exemple de session complète :

### 1. Début de session
```
Joueur Alice → Crée Node "Partons à l'aventure !"
                    ↓
session_watcher détecte le changement
                    ↓
Crée AISession dans un thread dédié
                    ↓
AISession charge les trigger nodes du scénario
```

### 2. Contributions et triggers
```
Alice → "Nous entrons dans le temple"
           ↓
fetch_new_nodes() détecte le message
           ↓
Ajouté au pending_batch
           ↓
process_pending_batch() envoie à Mistral
           ↓
Mistral analyse: trigger "temple_entrance" = true
           ↓
trigger_node() crée un Node event: "Une porte s'ouvre..."
           ↓
available_triggers mis à jour (nouveaux triggers disponibles)
```

### 3. Conclusion
```
Trigger "final_battle" détecté (is_final: true)
           ↓
handle_final_node() attend 60s pour collecter les messages
           ↓
Récupère 5 derniers messages des joueurs
           ↓
ask_mistral(messages, FINAL_PROMPT_CONTEXT_FILE)
           ↓
Mistral génère une conclusion narrative
           ↓
Crée Node "The End" avec le texte généré
           ↓
Marque Session.completed = true
           ↓
AISession.stop() arrête la boucle
           ↓
session_watcher retire la session de la liste active
```

---

## 🔧 Configuration et déploiement

### Variables d'environnement requises

Créer un fichier `.env` :
```env
# Identifiants PocketBase
PB_LOGIN=admin@example.com
PB_PASSWORD=your_secure_password

# Clé API Mistral AI
MISTRAL_API_KEY=your_mistral_api_key
```

### Dépendances Python

```bash
pip install pocketbase
pip install mistralai
pip install python-dotenv
pip install pydantic
```

### Lancement du système

```bash
cd ia_mistral
python session_watcher.py
```

Le système :
1. Se connecte à PocketBase
2. S'abonne aux changements de la collection `Node`
3. Attend les nouvelles sessions avec scénario IA
4. Lance automatiquement les instances `AISession` dans des threads séparés

### Fichiers générés

```
ia_mistral/
├── logs/
│   ├── session_watcher2_20251016_143022.log
│   ├── ai_session2_20251016_143022.log
│   └── mistral_client.log
├── sessions_data/
│   ├── session_abc123.json
│   ├── triggered_nodes_abc123.json
│   ├── session_xyz789.json
│   └── triggered_nodes_xyz789.json
```

---

## 🎯 Cas d'usage : Scénario Sun Wukong

### Structure du scénario

**Objectif** : Les joueurs incarnent les disciples de Sun Wukong et doivent récupérer le bâton magique Rúyì Jīngū Bàng auprès du Roi Dragon Ao Guang.

**Trigger Nodes** :
```json
[
  {
    "id": "1",
    "condition" : "first",
    "trigger": "stick (as in, a wooden staff)",
    "title": "Atop the Mountain of Flowers and Fruits (Step 1/5)",
    "text": "“Perhaps, Great Sage, something as humble as a staff might yet prove matchless in the right hands.” suggested one of Sun Wukong's followers. The Monkey King's grin spread, while his tail curled with amusement. “A staff, you say…?” His gaze drifted to the untamed mountains. “Very well.” With a laugh that scatters blossoms, he left a wordless dare hanging in the air. Left to ponder, the disciples exchanged glances. “What now?” one asked. “We need to find the staff!” another exclaimed. “But where?” a third chimed in. The air was thick with anticipation, and the quest had only just begun.",
    "author": "Narrator"
  },
  {
    "id": "2",
    "condition": "1",
    "trigger": "explore mountain",
    "title": "The Celestial Cavern's entrance (Step 2/5)",
    "text": "Guided by whispers and the wisdom of legends, the disciples ventured around the Mountain of Flowers and Fruit. There, hidden deep within its rocky heart, lay the Celestial Cavern. What would the monkeys do next ?",
    "author": "Narrator"
  },
  {
    "id": "3",
    "condition": "2",
    "trigger": "explore cavern",
    "title": "The Old Monkey's Revelation (Step 3/5)",
    "text": "In the warm shadows of the cavern, an elder monkey with a misty beard spoke in riddles. He hinted that a sacred staff that was not of earth or sky rested beneath the waves on the other side of the Eastern Sea. Undeterred, the disciples gazed toward the horizon, ready to brave the depths and awaken the secrets of the ocean.",
    "author": "Narrator"
  },
  {
    "id": "4",
    "condition": "3",
    "trigger": "cross sea",
    "title": "The Dragon King's Court (Step 4/5)",
    "text": "After braving the swells of the Eastern Sea and plunging beneath its jade-green depths, the monkeys reached the shimmering halls of the Dragon King Ao Guang. Explaining their quest for a weapon worthy of their master, they watched as Ao Guang unveiled a succession of ancient arms. Yet only when a certain weapon's name left the disciples' lips did the palace itself seem to awaken. Which weapon will Sun Wukong choose?",
    "author": "Narrator"
  },
  {
    "id": "5",
    "condition": "4",
    "trigger": "Ruyi Jingu Bang (如意金箍棒)",
    "title": "The Mighty Staff (Step 5/5)",
    "text": "Before Wukong stood the colossal golden staff known as 如意金箍棒. As he reached out, it shrank in an instant, folding its grandeur into the palm of his hand. The disciples watched, awe-struck. Their quest had reached its ending. A silence settled: what would they choose to do next? (Hint: you have 5 minutes to write whatever you want!)",
    "author": "Narrator",
    "is_final": true
  },

  {
    "id": "7",
    "trigger": "take a nap",
    "title": "Laziness",
    "text": "The disciples, tired from their journey, decided to take a nap. They found a cozy spot under a tree and closed their eyes. But when they woke up, they realized they hadn't advanced at all.",
    "author": "Narrator"
  },
  {
    "id": "8",
    "trigger": "eat banana",
    "title": "Banana Feast",
    "text": "One of the disciples discovered a hidden grove filled with golden bananas. Unable to resist, they called everyone for a grand feast. Bellies full and spirits high, they forgot entirely what they were supposed to be doing. Ah well, at least they were happy.",
    "author": "Narrator"
  },
  {
    "id": "9",
    "trigger": "dance",
    "title": "The Monkey Dance",
    "text": "Someone played a flute, and without warning, the disciples broke into an impromptu monkey dance. Even Wukong tapped his foot for a moment before regaining his royal composure. Was it important? No. Was it magnificent? Absolutely.",
    "author": "Narrator"
  },
  {
    "id": "10",
    "trigger": "look at the sky",
    "title": "Philosophical Pause",
    "text": "As they marched onward, one disciple paused to look at the clouds. 'What if the weapon... is a metaphor?' they mused. Everyone stared at them in silence, unsure if they were wise or just sleep-deprived.",
    "author": "Narrator"
  }
]
```

### Déroulement type

1. **Alice** : "Master Wukong needs a powerful stick to fight his enemies!"
   - → Trigger `1` ("stick") activé
   - → Node event créé : "Atop the Mountain of Flowers and Fruits (Step 1/5)"
   - → Les disciples apprennent qu'ils doivent chercher un bâton

2. **Bob** : "Let's explore the mountain to find clues!"
   - → Trigger `2` ("explore mountain") activé
   - → Node event créé : "The Celestial Cavern's entrance (Step 2/5)"
   - → Découverte de la caverne céleste

3. **Alice** : "We should explore this mysterious cavern."
   - → Trigger `3` ("explore cavern") activé
   - → Node event créé : "The Old Monkey's Revelation (Step 3/5)"
   - → Le vieux singe révèle que le bâton se trouve sous la mer de l'Est

4. **Bob** : "Time to cross the Eastern Sea and find that legendary weapon!"
   - → Trigger `4` ("cross sea") activé
   - → Node event créé : "The Dragon King's Court (Step 4/5)"
   - → Arrivée au palais du Roi Dragon Ao Guang

5. **Alice** : "We seek the Ruyi Jingu Bang, the legendary staff!"
   - → Trigger `5` ("Ruyi Jingu Bang") activé (trigger final)
   - → Node event créé : "The Mighty Staff (Step 5/5)"
   - → `handle_final_node()` démarre

6. **Collecte finale** (60 secondes)
   - Alice : "The staff recognizes Sun Wukong as its true master!"
   - Bob : "Let's return triumphant with this legendary weapon!"
   - _(Triggers humoristiques possibles en parallèle : "dance", "eat banana", "take a nap", etc.)_

7. **Conclusion générée par Mistral** :
   ```
   With the 如意金箍棒 in hand, the disciples journey back to their master. 
   The golden staff, once wielded by the Great Sage himself, now shrinks 
   to fit perfectly in Wukong's palm. The quest complete, the disciples 
   celebrate their success, knowing they've proven themselves worthy of 
   the Monkey King's trust.
   ```

8. **Fin de session**
   - Node "The End" créé avec la conclusion
   - `Session.completed = true`
   - AISession arrêtée
   - Retirée de la liste active

---

## 📝 Logging et débogage

### Structure des logs

Tous les logs utilisent le format :
```
[Composant 'Identifiant'] Message descriptif
```

**Exemples** :
```
[AISession 'Epic Quest'] Initialisation terminée
[AISession 'Epic Quest'] 3 nouveaux nodes détectés
[AISession 'Epic Quest'] Déclenchement du trigger trigger_2 par le node node_xyz. Justification: ...
[Mistral] Réponse de Mistral validée avec succès
```

### Fichiers de log

- **`session_watcher2_*.log`** : Surveillance globale, création/destruction de sessions
- **`ai_session2_*.log`** : Détails de chaque session (triggers, nodes, batch)
- **`mistral_client.log`** : Appels API, validations, erreurs Mistral

### Debugging courant

**Problème** : Un trigger ne se déclenche pas

1. Vérifier les logs d'`AISession` :
   ```
   [AISession 'Ma Session'] Triggers disponibles pour le batch: [('trigger_1', ['entrer'])]
   ```

2. Vérifier la réponse de Mistral :
   ```
   [Mistral] Réponse de Mistral validée avec succès
   ```

3. Chercher l'évaluation dans les logs :
   ```
   [AISession 'Ma Session'] trigger_1: should_get_triggered=false - Justification: Le texte ne mentionne pas d'entrée
   ```

**Solution** : Les mots-clés du trigger ne correspondent pas au texte du joueur. Ajuster les triggers ou reformuler.

---

## 🚀 Extensions possibles

### 1. Support multi-langues
Ajouter des fichiers de contexte par langue :
- `mistral_batch_prompt_fr.txt`
- `mistral_final_prompt_fr.txt`
- Paramétrer selon `session.language`

### 2. Triggers conditionnels complexes
```json
{
  "conditions": {
    "type": "AND",
    "rules": [
      {"trigger": "trigger_1"},
      {"trigger": "trigger_2"},
      {"node_count": ">10"}
    ]
  }
}
```

### 3. Personnalités IA multiples
Différents `context_file` selon le type de narrateur :
- Humoristique
- Dramatique
- Mystérieux

### 4. Métriques et analytics
Logger dans PocketBase :
- Temps moyen avant trigger
- Nombre de tentatives avant activation
- Sentiment des contributions (via Mistral)

---

## 📚 Ressources

- **PocketBase** : https://pocketbase.io/docs/
- **Mistral AI** : https://docs.mistral.ai/
- **Pydantic** : https://docs.pydantic.dev/

---

## ⚠️ Notes importantes

1. **Thread safety** : Toujours utiliser `active_ai_sessions_lock` quand on modifie la liste des sessions actives

2. **Nettoyage** : Les sessions inactives sont automatiquement nettoyées après 600s pour libérer les ressources

3. **Persistance** : Les fichiers JSON dans `sessions_data/` permettent de reprendre une session après un redémarrage

4. **Rate limiting** : Mistral AI peut avoir des limites de requêtes. Le système attend 5s entre chaque itération pour éviter les surchauffes.

5. **Coûts** : Chaque appel à Mistral consomme des tokens. Surveiller l'usage via le dashboard Mistral.

---

**Bon développement ! 🎮✨**
