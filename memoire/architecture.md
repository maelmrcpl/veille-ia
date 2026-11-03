---
quand_lire: Tu découvres le projet ; tu modifies sa structure ou sa configuration (opencode.json, .gitignore, CI) ; tu ajoutes ou modifies un skill, un agent ou une commande ; tu ajoutes un fichier de mémoire
couvre: opencode.json, .gitignore, .github/workflows/memoire.yml, .opencode/, README.md, src/veille_ia/__init__.py
verifie: 2026-11-03
---
# Architecture

## Projet
- Objectif final (déclaré par l'utilisateur) : une web GUI regroupant les news du jour sur plusieurs sujets (cyber, réseau, IA…), puis un audio qui les lit par catégorie.
- Étape actuelle : un agent Python de veille IA, prévu pour tourner chaque jour vers 8h (Planificateur de tâches Windows, pas encore en place). Le plan de développement est dans `memoire/PLAN.md`.
- Code présent : collecte Hacker News avec lecture complète des pages et client LLM. Absents : autres sources, regroupement, résumé, JSON du jour, point d'entrée unique, planification (voir `memoire/PLAN.md`).

## Structure du dépôt
| Dossier ou fichier | Rôle |
|---|---|
| `src/veille_ia/` | Package Python de l'agent. Détails dans `memoire/collecte.md` et `memoire/llm.md`. |
| `tests/` | Tests `pytest`, sans appel réseau. |
| `scripts/` | `routeur.ps1` (mémoire), `try_llm.py` et `try_hn.py` (essais réels lancés à la main). |
| `memoire/` | Mémoire du projet et `PLAN.md` (plan de reprise de session, temporaire). |
| `README.md` | Installation et lancement des tests. |

## Fichiers de harness
| Fichier | Rôle |
|---|---|
| `opencode.json` | Charge `memoire/ROUTEUR.md` à chaque session. Bloque la lecture et l'édition des `.env`, demande confirmation avant `git push`, `git reset --hard`, `git clean` et les suppressions. |
| `.github/workflows/memoire.yml` | Lance `scripts/routeur.ps1 -Verifier` à chaque push et pull request (historique Git complet, nécessaire à la détection de péremption). |
| `.opencode/skills/` | Skills `onboard` (créer ou mettre à jour la mémoire : `/onboard create` ou `/onboard update`), `plan` (cadrer avant de coder), `review` (relecture), `save-session`. |
| `.opencode/agents/reviewer.md` | Sous-agent relecteur en lecture seule, utilisé par `/review`. |
| `.opencode/commands/` | Commandes `/onboard` (arguments : mode puis contexte), `/plan`, `/review`, `/save-session`. Chacune charge le skill du même nom. |
| `.harness-base` | Marqueur de la version de harness-base installée (source, version, date). Écrit par le script d'installation de la base, lu par son script de mise à jour des projets. Ne pas modifier à la main. |

## Configuration
- `.gitignore` : fichiers exclus du dépôt (`.env`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `node_modules/`).
- `memoire/_ignore.txt` : fichiers suivis par Git exemptés de la vérification « couvert par la mémoire ».
- `scripts/routeur.ps1` : seuils de budget de contexte en tête de script (`$maxChargeEnPermanence`, `$maxFichierMemoire`). Détection de péremption : champ `verifie: AAAA-MM-JJ` de l'en-tête d'un fichier de mémoire.
- Variables d'environnement du client LLM : voir `memoire/llm.md`.
