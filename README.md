# New Babel Revolution

## Dev

### Prérequis

- [Node.js](https://nodejs.org/en/) Environnement d'exécution JavaScript (version > 20)
- [pnpm](https://pnpm.io/) : Gestionnaire de paquets
- [Git](https://git-scm.com/) : Gestionnaire de versions

### Optionnel

- [Docker](https://www.docker.com/) : Conteneurisation & Déploiement (nécessaire pour lancer PocketBase en local)
  - [Docker Desktop](https://www.docker.com/products/docker-desktop) : Version Desktop
  - [Docker Compose](https://docs.docker.com/compose/) : Outil de gestion de conteneurs
- [Go](https://go.dev/) : Nécessaire pour le serveur IA

### Installation

Clone du projet :
`git clone https://github.com/KoroSensei10/svelte-revolution.git`

```sh
pnpm install
```

### Variables d'environnement

Le fichier `.env` contient les URLs de production (valeurs par défaut). Pour le développement local, créez un fichier `.env.local` à la racine du projet pour surcharger ces valeurs :

```env
PUBLIC_DB_URL=http://localhost:8090
DB_URL=http://localhost:8090
```

> Note : `.env.local` est ignoré par git. Il est chargé en priorité sur `.env` grâce à la configuration dans `svelte.config.js`.

### Base de données locale (PocketBase)

Pour développer sans toucher à la base de production, lancez PocketBase en local avec Docker :

```sh
# Option 1 : Docker Compose
docker compose up pocketbase

# Option 2 : Build et run manuellement
docker build -t pocketbase ./db
docker run -p 8090:8090 pocketbase
```

L'interface admin est accessible sur `http://localhost:8090/_/`.

#### Import du schéma

1. Accédez à l'interface admin (`http://localhost:8090/_/`)
2. Créez un compte administrateur
3. Allez dans **Settings → Import collections**
4. Collez le contenu de `db/schema.json`
5. Confirmez l'import — toutes les collections seront créées

#### Partie IA

Voir [AI_README#setup](./README.ai.md#mise-en-place)

### Lancer le projet

Lancer le serveur de développement :

```sh
pnpm dev
```

#### Lancer l'IA

Voir le [AI_README#launch](./README.ai.md#lancer-lia)

## Tester la production

Lancer le serveur de production :

```sh
pnpm run build &&
pnpm run preview
```

## Structure du projet

- `src/` : code source
  - `lib/` : fonctions utilitaires
  - `components/` : composants
  - `routes/` : Toutes les routes de l'application
    - `admin/` : pages d'administration
- `db/` : Dockerfile et schéma PocketBase
- `ia_server/` : serveur IA en Go
- `public/` : fichiers statiques
- `build/` : fichiers générés
- `node_modules/` : dépendances

## Technologies utilisées

### Frontend

- [Svelte](https://svelte.dev/) : Framework JavaScript
- [Vite](https://vitejs.dev/) : Bundler et Runner pour le développement
- [Tailwind CSS](https://tailwindcss.com/) : Framework CSS

### Backend

- [SvelteKit](https://kit.svelte.dev/) : Meta-Framework pour Svelte
- [PocketBase](https://pocketbase.io/) : Base de données et API auto-hébergée
- [Go](https://go.dev/) : Serveur IA (modération, word2vec, dictionnaire)
- [Docker](https://www.docker.com/) : Conteneurisation & Déploiement

### Outils

- [TypeScript](https://www.typescriptlang.org/) : Langage de programmation apportant des types à JavaScript
- [ESLint](https://eslint.org/) : Linter de code
