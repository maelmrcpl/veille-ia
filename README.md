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

## Ajouter une catégorie
Une catégorie se déclare uniquement dans `src/veille_ia/categories.py`, le reste du code est commun.

1. Ajouter une entrée au dictionnaire `CATEGORIES` (la clé est l'identifiant, en minuscules sans accent) :
   ```python
   "data": Category(
       id="data",
       label="données et bases de données",
       topic_count=3,
       hn_keywords=["PostgreSQL", "data engineering"],
       blog_feeds={"Nom du site": "https://exemple.com/rss.xml"},
       reddit_feeds={"Reddit r/dataengineering": "https://www.reddit.com/r/dataengineering/.rss"},
   ),
   ```
   - `label` est inséré dans les prompts (« domaine « label » ») et lu à voix haute dans l'audio : une courte expression naturelle à l'oral.
   - `topic_count` : nombre de sujets par jour.
   - `hn_keywords` : mots-clés précis (les mots trop génériques ramènent du bruit). `blog_feeds` : sites et blogs de référence, classés avant les articles Hacker News et Reddit. `reddit_feeds` peut rester vide (`{}`).
2. Tester la catégorie seule : `python scripts\run_agent.py data`. Contrôler le nombre d'articles collectés et la pertinence des sujets, puis ajuster mots-clés et flux.
3. Rien d'autre à configurer : la catégorie est lancée par défaut par `python scripts\run_agent.py` et par la tâche `VeilleIA`.

Conséquences à connaître :
- **Ordre** : celui de `CATEGORIES`. Un article déjà repris par une catégorie plus haut dans la liste n'est pas repris par les suivantes.
- **Audio** : la catégorie produit son propre `data/<id>/AAAA-MM-JJ.wav` et entre dans l'audio global. Sa voix est la `VOICES[position % nombre de voix]` : à partir de la 5e catégorie, les voix de `.env` se répètent (ajouter des voix dans `VOICES` pour garder une voix par catégorie).
- **Quota TTS** : une requête de plus par jour (limite de 10 requêtes par jour et par modèle de `TTS_MODELS`).
- **Tests** : `python -m pytest` doit rester vert (`tests/test_categories.py`) et la section catégories de `memoire/categories.md` est à mettre à jour.

## Documentation
La mémoire du projet (architecture, choix, commandes) est dans `memoire/`.

## Workflow

Voici le workflow suivie par l'app, avant l'implémentation de l'audio

<img width="1266" height="1591" alt="image" src="https://github.com/user-attachments/assets/ea5e14bb-22dd-4335-b210-5025a155f54a" />
