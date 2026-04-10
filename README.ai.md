# L'intelligence artificielle dans Babel

## Mise en place

Le service IA est écrit en **Python (FastAPI)** et se trouve dans `./ia_server/`. Il s'authentifie auprès de PocketBase avec un utilisateur dédié `ai-gamemaster` et utilise l'API Mistral pour évaluer les règles déclenchées par les joueurs.

Ajouter les variables suivantes dans `.env.local` :

```env
DB_URL=http://localhost:8090
PB_BOT_EMAIL=ai-gamemaster@babel-revolution.local
PB_BOT_PASSWORD=<mot de passe du compte créé dans PocketBase>
MISTRAL_API_KEY=<votre clé Mistral>
```

Créer dans l'interface admin de PocketBase (`http://localhost:8090/_/`) un utilisateur avec ces identifiants et le rôle `superAdmin` (nécessaire pour modifier les nœuds existants lors de la censure).

## Lancer l'IA

```sh
pnpm run ia
```

Cela démarre Uvicorn sur le port 8000 et lance la boucle de polling sur la collection `Node` de PocketBase.

## Comment ça marche

Le service IA n'est plus dans le chemin de la requête : il observe la collection `Node` en arrière-plan et, pour chaque nouvelle contribution dans une session dont le scénario a `ai = true`, il :

1. Charge `Scenario.aiConfig` (JSON validé par `aiConfigSchema`),
2. Applique les capacités cochées :
   - **canCensor** : remplace les mots interdits par `####` directement dans le nœud,
   - **canTriggerNodes** : envoie la contribution + les conditions à Mistral et publie un nœud `event` pré-écrit si une règle correspond,
   - **canEndSession** : demande à Mistral si la condition de fin est remplie et termine la session le cas échéant.

Chaque règle déclenchable et la condition de fin ne peuvent se déclencher qu'**une seule fois par session**.

## Tester l'IA

Avec un scénario de test ayant `ai = true` et une `aiConfig` complète, créer une session et poster une contribution. Selon la capacité activée, vous devriez observer dans les ~2 secondes :
- Le titre/texte du nœud remplacé par `####` (canCensor)
- Un nouveau nœud `event` créé en réponse (canTriggerNodes)
- La session marquée `completed` (canEndSession)

Voir aussi `ia_server/README.md` pour les détails de développement.
