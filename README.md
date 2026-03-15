# New Babel Revolution

## Dev

### Prérequis

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
pnpm install # pnpm i
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
pnpm dev
```

#### Lancer l'ia

voir le [AI_README#launch](./README.ai.md#lancer-lia)

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
- `public/` : fichiers statiques
- `build/` : fichiers générés
- `node_modules/` : dépendances

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
