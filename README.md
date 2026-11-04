# veille-ia

Agent de veille : chaque jour, il collecte les actualités de 4 catégories sur Hacker News, des sites spécialisés et Reddit, les regroupe par sujet et écrit un résumé en français rédigé pour l'oral dans `data/<catégorie>/AAAA-MM-JJ.json`.

| Catégorie | Identifiant | Sujets par jour |
|---|---|---|
| Intelligence artificielle | `ia` | 5 |
| Cybersécurité | `cyber` | 4 |
| Cloud, DevOps, infrastructure | `cloud` | 2 |
| Réseaux et télécoms | `reseau` | 2 |

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
| Lancer l'agent une fois (toutes les catégories) | `python scripts\run_agent.py` |
| Lancer une ou plusieurs catégories | `python scripts\run_agent.py cyber reseau` |
| Lancer avec un log dans `data\logs\` | `.\scripts\run_daily.ps1` |
| Planifier chaque jour à 8h (Windows) | `.\scripts\register_task.ps1` (`-Heure "09:15"` pour changer) |
| Tests | `python -m pytest` |

La tâche planifiée `VeilleIA` rattrape le lancement si la machine était éteinte. Les articles déjà résumés ne sont pas repris les jours suivants.

## Documentation
La mémoire du projet (architecture, choix, commandes) est dans `memoire/`.
