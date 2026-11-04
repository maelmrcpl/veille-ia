# ROUTEUR DE MÉMOIRE

> Fichier généré par `scripts/routeur.ps1` : ne pas le modifier à la main. Modifier l'en-tête `quand_lire` du fichier concerné, puis relancer le script.

Index de `memoire/` : une ligne par fichier, avec le moment où le lire. Ce fichier ne contient aucune connaissance du projet. Chemins relatifs à la racine.

## 1. Fichiers de mémoire
Lis un fichier quand la tâche correspond à sa colonne « Quand le lire ». Plusieurs peuvent s'appliquer. Un fichier déjà lu dans la session et non modifié depuis ne se relit pas.

| Fichier | Quand le lire |
|---|---|
| `memoire/architecture.md` | Tu découvres le projet ; tu modifies sa structure ou sa configuration (opencode.json, .gitignore, CI) ; tu ajoutes ou modifies un skill, un agent ou une commande ; tu ajoutes un fichier de mémoire |
| `memoire/categories.md` | Tu ajoutes ou modifies une catégorie de veille (IA, cyber, réseau, cloud), ses sources, son libellé ou son nombre de sujets |
| `memoire/collecte.md` | Tu ajoutes ou modifies un collecteur de news, le type Article, la recherche Hacker News ou la lecture complète des pages |
| `memoire/llm.md` | Tu modifies ou appelles le client LLM ; tu changes les modèles, leurs quotas ou les variables d'environnement LLM |
| `memoire/principes.md` | Tu écris ou modifies du code ; tu dois lancer les tests, le lint ou le build ; tu hésites sur un choix de conception ou de nommage |
| `memoire/resume.md` | Tu modifies la sélection des sujets, le résumé en français, le JSON du jour, le point d'entrée de l'agent ou sa planification quotidienne Windows |
| `memoire/traitement.md` | Tu modifies le dédoublonnage des articles déjà vus, le regroupement LLM des articles en sujets ou le type Topic |

Aucune ligne ne correspond : lis `memoire/architecture.md`, avertis l'utilisateur que la tâche n'est pas couverte par le routeur et n'invente rien.

## 2. Cohérence
- Un fait de la mémoire qui contredit le code est une erreur de la mémoire : corrige-la et signale-la à l'utilisateur.
- Un chemin listé ici qui n'existe pas : signale-le à l'utilisateur.
