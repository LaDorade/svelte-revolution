# Mise en place du projet

## Dev

### Prérequis

- [Bun](https://bun.sh/) : Gestionnaire de packet & Runtime \
- [Node.js](https://nodejs.org/en/) Environnement d'exécution JavaScript (version > 20)
- [Git](https://git-scm.com/) : Gestionnaire de versions

### Optionnel

- [Docker](https://www.docker.com/) : Conteneurisation & Déploiement
  - [Docker Desktop](https://www.docker.com/products/docker-desktop) : Version Desktop
  - [Docker Compose](https://docs.docker.com/compose/) : Outil de gestion de conteneurs

### Installation

Clone du projet :
`git clone https://github.com/KoroSensei10/svelte-revolution.git`

```sh
bun install
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

Pour la partie IA, il faut ajouter les variables suivantes dans le fichier `.env.local` pour qu'il puisse communiquer avec votre serveur IA.

```env
IA_SERVER_URL=http://localhost:8000
```

### Lancer le projet

Lancer le serveur de développement :

```sh
bun dev
```

#### Lancer l'ia

Pour lancer le serveur IA, il faut se rendre dans le dossier `ia_server/` et lancer le serveur avec la commande suivante :

```sh  
XXX # Cela dépend de votre IA
```

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

## Technologies utilisées

### Frontend

- [Svelte](https://svelte.dev/) : Framework JavaScript
- [Tailwind CSS](https://tailwindcss.com/) : Framework CSS
  - [DaisyUI](https://daisyui.com/) : Composants Tailwind CSS

### Backend

- [Vite](https://vitejs.dev/) : Bundler et Runner pour le développement
- [SvelteKit](https://kit.svelte.dev/) : Meta-Framework pour Svelte
- [Docker](https://www.docker.com/) : Conteneurisation & Déploiement
- [PocketBase](https://pocketbase.io/) : Base de données et API auto-hébergée

### Outils

- [TypeScript](https://www.typescriptlang.org/) : Langage de programmation apportant des types à JavaScript
- [Prettier](https://prettier.io/) : Formateur de code
- [ESLint](https://eslint.org/) : Linter de code

## Styler avec Tailwind CSS

Tailwind CSS est un framework CSS qui permet de créer des interfaces rapidement en utilisant des classes utilitaires.
Similaire à Bootstrap, mais plus minimaliste. Simplemement ajouter des classes aux éléments HTML pour styliser.

### Exemple

La manière la plus simple est d'ajouter les classes directement dans le code HTML. C'est aussi la méthode recommandée.

```html
<button
 class="px-4 py-2 font-bold text-white bg-blue-500
 rounded hover:bg-blue-700"
>
 Button
</button>
```

## Déploiement

Déploiement automatique sur le serveur YUNOHOST à chaque push.

### OLD! Déploiment sur le serveur YUNOHOST

Pour réussir à déployer le projet sur le serveur YUNOHOST, il faut suivre les étapes suivantes :

- Cloner le projet sur le serveur
- Créer un fichier `.env` avec la viariable `ENV_FILE=.env.production` pour que le projet utilise les variables d'environnement de production
- Modifier le fichier `.env.production` pour ajouter les variables d'environnement
  - En utilisant cette méthode il faut seulement modifer la variable `PUBLIC_DB_URL` pour qu'elle pointe vers le serveur YUNOHOST vu de l'extérieur (ex: `https://svelte-db.babel-revolution.fr`)
  - les autres variables sont déjà configurées
  - [local preview uniquement] Modfier la variable `ORIGIN` et mettre `http://localhost:4173` sinon le serveur ne pourra pourra pas traiter les requêtes POST des formulaires
- Ensuite, simplement ajouter le reverse proxy sur le serveur YUNOHOST

### Adapter

Voir cette ligne dans ce fichier : [svelte.config.js:1](./svelte.config.js)

#### Docker

Utiliser l'adapter Bun.

```bash
docker-compose up --build
```

#### Vercel

Utiliser l'adapter auto (ou vercel).

**Auto déploiement sur Vercel à chaque push.**

La branche de déploiement est `main`.\
La branche de test est `staging`.

## Redéploiement

### Docker ou YUNOHOST

### Le redéploiement est automatique sur la branche staging

Sinon, simplement pull le projet et relancer le serveur.

```bash
docker-compose down # si nécessaire
```

```bash
docker-compose up --build
```

### Déploiement sur Vercel

Vercel redéploie automatiquement à chaque push.
