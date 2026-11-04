# veille-ia

Agent de veille IA : chaque jour, il collecte les actualités IA (Hacker News, blogs d'éditeurs, Reddit), les regroupe par sujet et écrit un résumé en français (6 sujets, environ 1 000 mots, rédigés pour l'oral) dans `data/ia/AAAA-MM-JJ.json`.

## Installation
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```
Renseigner `LLM_API_KEY` dans `.env` (endpoint et modèles Google AI Studio par défaut, voir `.env.example`).

## Utilisation
| Action | Commande |
|---|---|
| Lancer l'agent une fois | `python scripts\run_agent.py` |
| Lancer avec un log dans `data\logs\` | `.\scripts\run_daily.ps1` |
| Planifier chaque jour à 8h (Windows) | `.\scripts\register_task.ps1` (`-Heure "09:15"` pour changer) |
| Tests | `python -m pytest` |

La tâche planifiée `VeilleIA` rattrape le lancement si la machine était éteinte. Les articles déjà résumés ne sont pas repris les jours suivants.

## Documentation
La mémoire du projet (architecture, choix, commandes) est dans `memoire/`.
