# Mettre en forme le projet

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

Détails des classes :

- `px-4` : padding horizontal de 4
- `py-2` : padding vertical de 2
- `font-bold` : texte en gras
- `text-white` : texte blanc
- `bg-blue-500` : fond bleu avec intensité 500
- `rounded` : bord arrondi
- `hover:bg-blue-700` : fond bleu avec intensité 700 au survol
  - `hover:` est un préfixe pour les classes qui s'appliquent au survol

## Documentation

- [Tailwind CSS](https://tailwindcss.com/)
