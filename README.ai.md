# L'intelligence artificielle dans Babel

## Mise en place

Pour la partie IA, il faut ajouter les variables suivantes dans le fichier `.env.local` (ou `.env.production`) pour qu'il puisse communiquer avec votre serveur IA.

```env
IA_SERVER_URL=http://localhost:8000
```

> Note: Cela permet de tester quand on a son serveur en local sur sa machine sans passer par docker.

## Lancer l'ia

Le serveur IA est écrit en **Go** et se trouve dans `./ia_server/`. On peut le lancer avec la commande suivante :

```sh
pnpm run ia
```

> Note: Il faut avoir installé [Go](https://go.dev/) sur sa machine pour pouvoir lancer l'IA.

## Tester l'IA

Si tout est bien configuré, vous devriez voir une popup s'afficher sur les sessions qui ont un scénario avec IA que l'ai est bien connectée.
