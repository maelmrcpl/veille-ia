---
quand_lire: Tu modifies le dédoublonnage des articles déjà vus, le regroupement LLM des articles en sujets ou le type Topic
couvre: src/veille_ia/dedup.py, src/veille_ia/cluster.py, tests/test_dedup.py, tests/test_cluster.py, scripts/try_cluster.py
verifie: 2026-11-03
---
# Dédoublonnage et regroupement

## Articles déjà vus (`src/veille_ia/dedup.py`)
- Historique : fichier `data/seen_urls.json` (`SEEN_PATH`), dictionnaire URL → timestamp Unix de la première prise en compte. Choisi plutôt que la relecture des JSON quotidiens pour ne pas dépendre de leur schéma.
- `filter_new(articles, path)` écarte les URL déjà dans l'historique et les doublons d'URL dans le lot. Elle ne modifie pas le fichier.
- `mark_seen(articles, now, path)` ajoute les URL, supprime les entrées de plus de `RETENTION_SECONDS` (14 jours) et écrit le fichier (dossier créé si besoin). À appeler à la fin d'un run réussi (pas encore branché : point d'entrée prévu en phase 6).
- `data/` est dans `.gitignore` (hypothèse de travail de la phase 6, à confirmer par l'utilisateur).

## Regroupement (`src/veille_ia/cluster.py`)
- `Topic(title, articles)` est défini dans `src/veille_ia/models.py`.
- `cluster(articles, models)` fait un seul appel `llm.complete` (`models` = liste `(nom, rpm)`, prévue pour `LLM_MODELS_CLUSTER`). Le prompt numérote les articles (`[i] titre (source) 300 premiers caractères du texte`) et demande `{"topics": [{"title", "ids"}], "off_topic": [ids]}`.
- Les articles de `off_topic` (hors IA) sont écartés. Un article absent de la réponse devient un sujet seul. Les numéros inconnus, non entiers ou répétés sont ignorés. Un bloc ```` ```json ```` autour de la réponse est toléré.
- Réponse non JSON ou sans clé `topics` : `LLMError`. Liste vide : aucun appel LLM.
- Essai réel (`scripts/try_cluster.py`, 2026-11-03) : le prompt « même événement précis » donnait 4 à 37 sujets selon l'appel et reconstituait au mieux 4 articles sur 7 de l'IPO d'Anthropic. Mesure sur jeu fixe (10 articles connus d'hier + 48 du jour, 8 appels) : le prompt actuel (même affaire, angles différents acceptés, exemple de l'IPO, consigne « la plupart restent seuls ») retrouve toujours le groupe de 3 et 5 articles sur 7 pour l'IPO (7 appels sur 8), 25 à 39 sujets. Écartés : bruit hors IA. Défauts restants : 2 articles de l'IPO restent isolés ; doublon HN et blog OpenAI non regroupé auparavant, non remesuré ; les discussions `[D]` de Reddit sont gardées. Un effondrement à environ 4 sujets est apparu 2 fois sur une vingtaine d'appels, cause inconnue : `src/veille_ia/main.py` relance le regroupement une fois si moins de `MIN_TOPICS` candidats.
- La température n'a que peu d'effet sur la stabilité mesurée, elle est quand même fixée à 0 dans `llm.complete`.
- Le script `scripts/try_cluster.py` consomme 1 appel LLM et affiche sujets et articles écartés.
