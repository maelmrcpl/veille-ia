# ROUTEUR DE MÉMOIRE

> Fichier généré par `scripts/routeur.ps1` : ne pas le modifier à la main. Modifier l'en-tête `quand_lire` du fichier concerné, puis relancer le script.

Index de `memoire/` : une ligne par fichier, avec le moment où le lire. Ce fichier ne contient aucune connaissance du projet. Chemins relatifs à la racine.

## 1. Fichiers de mémoire
Lis un fichier quand la tâche correspond à sa colonne « Quand le lire ». Plusieurs peuvent s'appliquer. Un fichier déjà lu dans la session et non modifié depuis ne se relit pas.

| Fichier | Quand le lire |
|---|---|
| `memoire/architecture.md` | Tu découvres le projet ; tu modifies sa structure ou sa configuration (opencode.json, .gitignore, CI) ; tu ajoutes ou modifies un skill, un agent ou une commande ; tu ajoutes un fichier de mémoire |
| `memoire/principes.md` | Tu écris ou modifies du code ; tu dois lancer les tests, le lint ou le build ; tu hésites sur un choix de conception ou de nommage |

Aucune ligne ne correspond : lis `memoire/architecture.md`, avertis l'utilisateur que la tâche n'est pas couverte par le routeur et n'invente rien.

## 2. Cohérence
- Un fait de la mémoire qui contredit le code est une erreur de la mémoire : corrige-la et signale-la à l'utilisateur.
- Un chemin listé ici qui n'existe pas : signale-le à l'utilisateur.
