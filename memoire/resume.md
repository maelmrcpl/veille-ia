---
quand_lire: Tu modifies la sélection des sujets, le résumé en français, le JSON du jour ou le point d'entrée de l'agent
couvre: src/veille_ia/summary.py, src/veille_ia/main.py, scripts/run_agent.py, tests/test_summary.py, tests/test_main.py
verifie: 2026-11-04
---
# Résumé et point d'entrée

## Sélection et résumé (`src/veille_ia/summary.py`)
- `select_candidates(topics)` trie par `rank_key` et garde les `MAX_CANDIDATES` = 10 premiers. Ordre : sujets non-discussion d'abord (discussion = tous les titres contiennent `[D]`), puis nombre de sources distinctes, puis présence d'un blog officiel (`OFFICIAL_SOURCES` = clés de `blogs.FEEDS`), puis somme des scores, puis nombre d'articles. Décision utilisateur du 2026-11-04 (blogs officiels avant les articles HN à une source, discussions Reddit en dernier).
- `summarize(candidates, select_models, write_models)` enchaîne 3 étapes :
  1. `choose` : un appel (`select_models` = `LLM_MODELS_CLUSTER`, Lite) choisit et classe exactement `TOPIC_COUNT` = 6 sujets, avec titre et 300 caractères par article. Réponse `{"topics": [{"ids": [...]}]}` ; plusieurs numéros = candidats fusionnés (même affaire). Numéros invalides ou déjà pris ignorés. S'il manque des sujets, le code complète avec les candidats suivants dans l'ordre de `rank_key`.
  2. `fetch_full_texts` : `fetch_text` sur les `ARTICLES_PER_TOPIC` = 3 premiers articles de chaque sujet retenu (sauf pages `news.ycombinator.com/item`) ; le texte complet remplace l'extrait seulement s'il est plus long (pages Reddit bloquées : extrait gardé).
  3. `write` : un appel (`write_models` = `LLM_MODELS_SUMMARY`, Flash) écrit un texte de 160 à 180 mots par sujet (oral, sans lien ni Markdown) à partir de `TEXT_CHARS` = 4000 caractères par article. Réponse `{"topics": [{"id", "title", "text"}]}`. Le rang suit l'ordre de `choose`.
- Validation de `write` : id inconnu, répété ou texte vide ignorés ; `clean_spoken` retire URL et caractères Markdown ; titre vide : titre du premier article ; aucun sujet utilisable ou JSON invalide : `LLMError`. Les sources d'un sujet sont tous ses articles (candidats fusionnés compris), pas seulement les 3 lus.

## Point d'entrée (`src/veille_ia/main.py`)
- `run(now, report_dir, seen_path)` : `collect_all()` (HN enrichi, blogs, Reddit), `dedup.filter_new`, `cluster.cluster` (`LLM_MODELS_CLUSTER`, relancé une fois si moins de `TOPIC_COUNT` candidats), `summary.select_candidates`, `summary.summarize`, écriture de `data/ia/AAAA-MM-JJ.json`, puis `dedup.mark_seen` sur les articles des sujets retenus uniquement. Renvoie le chemin, ou `None` s'il n'y a rien à écrire. Un second run le même jour écrase le fichier du jour.
- Appels LLM par run : 2 Lite (regroupement, choix), 3 si relance ; 1 Flash (rédaction).
- Format du JSON : `{"date", "category": "ia", "topics": [{"rank", "title", "text", "sources": [{"name", "title", "url"}]}]}`.
- `main()` charge `.env`, lance `run()` et affiche le nombre de sujets et de mots. Lancement : `python scripts\run_agent.py` (appelle `main()` après `sys.path.insert(0, "src")`).
- Variable absente : `LLMError("Missing environment variable …")`.

## Essais réels
- 2026-11-03, ancien déroulé (un seul appel qui choisissait et écrivait) : 2 sujets et 320 mots, puis 6 sujets et 849 mots après durcissement du prompt.
- 2026-11-04, déroulé actuel, 2 runs : un run en échec (tous les modèles Flash en 503, avant l'ajout de `gemini-3.5-flash-lite` en repli), un run à 6 sujets et 934 mots (150 à 167 mots par sujet), dont un sujet fusionné à 5 sources et un blog OpenAI.
- 2026-11-04, après ajout du repli Lite : un run avec historique vide a redonné les mêmes 6 sujets dans le même ordre que le run précédent (889 mots, 141 à 157 mots par sujet ; titres sans accents et très courts, peut-être écrits par le modèle de repli). Un run avec l'historique du run précédent a écarté ces 6 sujets et en a choisi 6 autres (1 024 mots, 161 à 177 mots par sujet), comme un run du lendemain.
- Tests : `tests/test_summary.py` et `tests/test_main.py` avec faux `llm.complete` et faux `fetch_text`.
