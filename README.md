# New Babel Revolution

## Dev

### Prérequis

- [Bun](https://bun.sh/) : Gestionnaire de packet & Runtime \
- [Node.js](https://nodejs.org/en/) Environnement d'exécution JavaScript (version > 20)
- [Git](https://git-scm.com/) : Gestionnaire de versions

### Optionnel

Outils qui permettent de tester le projet en local dans des conditions similaires à la production (YUNOSHOST).

- [Docker](https://www.docker.com/) : Conteneurisation & Déploiement
  - [Docker Desktop](https://www.docker.com/products/docker-desktop) : Version Desktop
  - [Docker Compose](https://docs.docker.com/compose/) : Outil de gestion de conteneurs

### Installation

Clone du projet :
`git clone https://github.com/KoroSensei10/svelte-revolution.git`

```sh
bun install # ou bun i # Installe les dépendances du projet
```

### Variables d'environnement

Créer un fichier `.env` à la racine du projet avec les variables d'environnement suivantes :

```env
ENV_FILE=.env.local
```

Dans le fichier `.env.local` vous pouvez changer les variables `PUBLIC_DB_URL` et `DB_URL` pour qu'elle pointe vers votre (ou n'importe laquelle) base de données PocketBase.

```env
PUBLIC_DB_URL=http://localhost:8090
DB_URL=http://localhost:8090
```

#### Partie IA

Voir [AI_README#setup](./README.ai.md#mise-en-place)

### Lancer le projet

Lancer le serveur de développement :

```sh
bun dev
```

#### Lancer l'ia

voir le [AI_README#launch](./README.ai.md#lancer-lia)

## Tester la production

Lancer le serveur de production :

```sh
bun run build &&
bun run preview
```

## Structure du projet

- `src/` : code source
  - `lib/` : fonctions utilitaires
  - `components/` : composants
  - `routes/` : Toutes les routes de l'application
    - `admin/` : pages d'administration
- `public/` : fichiers statiques
- `build/` : fichiers générés
- `node_modules/` : dépendances

## (Re)Déploiement

Pour les curieux, un fichier [`deploy.old.sh`](./deploy.old.sh) est présent à la racine du projet. Il permettait de déployer le projet sur le serveur YUNOHOST, mais maintenant tout est automatisé.  
Cela "explique", les noms de domaines, les manips à faire et plein d'autres choses

### Actions Automatiques

#### *YUNOHOST*

J'ai configurer des actions github pour que le projet se déploie automatiquement sur le serveur YUNOHOST à chaque push sur la branche `staging`.  
Cela se fait aussi au redémarrage du serveur YUNOHOST, cela grâce à des services linux qui se lancent automatiquement (voir le fichier `/etc/systemd/system/new-babel.service` sur la machine).

##### Discord Webhook

Le fichier précédemment cité contient aussi un webhook discord pour notifier quand le serveur est redémarré.

#### *Vercel*

Le déploiement sur Vercel se fait automatiquement à chaque push sur la branche `staging` et `main`.

#### *GitHub*

Comme dit précédemment, le déploiement sur YUNOHOST se fait automatiquement à chaque push sur la branche `staging` grâce à des actions github.  
De plus, un Webhook Discord est configuré pour notifier quand le déploiement à réussi ou échoué (voir les secrets github).

### OLD! (mais peut servir un jour) Déploiment sur le serveur YUNOHOST

Pour réussir à déployer le projet sur le serveur YUNOHOST, il faut suivre les étapes suivantes :

- Cloner le projet sur le serveur
- Créer un fichier `.env` avec la viariable `ENV_FILE=.env.production` pour que le projet utilise les variables d'environnement de production
- Modifier le fichier `.env.production` pour ajouter les variables d'environnement
  - En utilisant cette méthode il faut seulement modifer la variable `PUBLIC_DB_URL` pour qu'elle pointe vers le serveur YUNOHOST vu de l'extérieur (ex: `https://svelte-db.babel-revolution.fr`)
  - les autres variables sont déjà configurées
  - [local preview uniquement] Modfier la variable `ORIGIN` et mettre `http://localhost:4173` sinon le serveur ne pourra pourra pas traiter les requêtes POST des formulaires
- Ensuite, simplement ajouter le reverse proxy sur le serveur YUNOHOST

## Technologies utilisées

### Frontend

- [Svelte](https://svelte.dev/) : Framework JavaScript
- [Vite](https://vitejs.dev/) : Bundler et Runner pour le développement
- [Tailwind CSS](https://tailwindcss.com/) : Framework CSS
  - [DaisyUI](https://daisyui.com/) : Composants Tailwind CSS

### Backend

- [SvelteKit](https://kit.svelte.dev/) : Meta-Framework pour Svelte
- [PocketBase](https://pocketbase.io/) : Base de données et API auto-hébergée
- [Docker](https://www.docker.com/) : Conteneurisation & Déploiement

### Outils

- [TypeScript](https://www.typescriptlang.org/) : Langage de programmation apportant des types à JavaScript
- [Prettier](https://prettier.io/) : Formateur de code
- [ESLint](https://eslint.org/) : Linter de code
