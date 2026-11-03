---
quand_lire: Tu modifies le dédoublonnage des articles déjà vus, le regroupement LLM des articles en sujets ou le type Topic
couvre: src/veille_ia/dedup.py, src/veille_ia/cluster.py, tests/test_dedup.py, tests/test_cluster.py
verifie: 2026-11-03
---
# Dédoublonnage et regroupement

## Articles déjà vus (`src/veille_ia/dedup.py`)
- Historique : fichier `data/seen_urls.json` (`SEEN_PATH`), dictionnaire URL → timestamp Unix de la première prise en compte. Choisi plutôt que la relecture des JSON quotidiens pour ne pas dépendre de leur schéma.
- `filter_new(articles, path)` écarte les URL déjà dans l'historique et les doublons d'URL dans le lot. Elle ne modifie pas le fichier.
- `mark_seen(articles, now, path)` ajoute les URL, supprime les entrées de plus de `RETENTION_SECONDS` (14 jours) et écrit le fichier (dossier créé si besoin). À appeler à la fin d'un run réussi (pas encore branché : point d'entrée prévu en phase 6).
- `data/` n'est pas dans `.gitignore` : décision de versionnement à prendre en phase 6.

## Regroupement (`src/veille_ia/cluster.py`)
- `Topic(title, articles)` est défini dans `src/veille_ia/models.py`.
- `cluster(articles, models)` fait un seul appel `llm.complete` (`models` = liste `(nom, rpm)`, prévue pour `LLM_MODELS_CLUSTER`). Le prompt numérote les articles (`[i] titre (source) 300 premiers caractères du texte`) et demande `{"topics": [{"title", "ids"}], "off_topic": [ids]}`.
- Les articles de `off_topic` (hors IA) sont écartés. Un article absent de la réponse devient un sujet seul. Les numéros inconnus, non entiers ou répétés sont ignorés. Un bloc ```` ```json ```` autour de la réponse est toléré.
- Réponse non JSON ou sans clé `topics` : `LLMError`. Liste vide : aucun appel LLM.
- Pas encore testé avec le vrai LLM (tests avec faux `llm.complete`).
