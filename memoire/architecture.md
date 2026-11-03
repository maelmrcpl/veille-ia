---
quand_lire: Tu découvres le projet ; tu modifies sa structure ou sa configuration (opencode.json, .gitignore, CI) ; tu ajoutes ou modifies un skill, un agent ou une commande ; tu ajoutes un fichier de mémoire
couvre: opencode.json, .gitignore, .github/workflows/memoire.yml, .opencode/
---
# Architecture

À compléter à la création du projet : ce que fait le projet, ses fichiers principaux et leur rôle, sa configuration.

## Fichiers du code
| Fichier | Rôle |
|---|---|
| `opencode.json` | Charge `memoire/ROUTEUR.md` à chaque session. Bloque la lecture et l'édition des `.env`, demande confirmation avant `git push`, `git reset --hard`, `git clean` et les suppressions. |
| `.github/workflows/memoire.yml` | Lance `scripts/routeur.ps1 -Verifier` à chaque push et pull request (historique Git complet, nécessaire à la détection de péremption). |
| `.opencode/skills/` | Skills `onboard` (créer ou mettre à jour la mémoire : `/onboard create` ou `/onboard update`), `plan` (cadrer avant de coder), `review` (relecture), `save-session`. |
| `.opencode/agents/reviewer.md` | Sous-agent relecteur en lecture seule, utilisé par `/review`. |
| `.opencode/commands/` | Commandes `/onboard` (arguments : mode puis contexte), `/plan`, `/review`, `/save-session`. Chacune charge le skill du même nom. |
| `.harness-base` | Marqueur de la version de harness-base installée (source, version, date). Écrit par le script d'installation de la base, lu par son script de mise à jour des projets. Ne pas modifier à la main. |

## Configuration
- `.gitignore` : fichiers exclus du dépôt.
- `memoire/_ignore.txt` : fichiers suivis par Git exemptés de la vérification « couvert par la mémoire ».
- `scripts/routeur.ps1` : seuils de budget de contexte en tête de script (`$maxChargeEnPermanence`, `$maxFichierMemoire`). Détection de péremption : champ `verifie: AAAA-MM-JJ` de l'en-tête d'un fichier de mémoire.
