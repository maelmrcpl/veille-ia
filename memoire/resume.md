---
quand_lire: Tu modifies la sélection des sujets, le résumé en français, le JSON du jour, le point d'entrée de l'agent ou sa planification quotidienne Windows
couvre: src/veille_ia/summary.py, src/veille_ia/main.py, scripts/run_agent.py, scripts/run_daily.ps1, scripts/register_task.ps1, tests/test_summary.py, tests/test_main.py
verifie: 2026-11-04
---
# Résumé et point d'entrée

## Sélection et résumé (`src/veille_ia/summary.py`)
- `select_candidates(topics, category)` trie par `rank_key` et garde les `MAX_CANDIDATES` = 10 premiers. Ordre : sujets non-discussion d'abord (discussion = tous les titres contiennent `[D]`), puis nombre de sources distinctes, puis présence d'un blog officiel (clés de `category.blog_feeds`), puis somme des scores, puis nombre d'articles. Décision utilisateur du 2026-11-04 (blogs officiels avant les articles HN à une source, discussions Reddit en dernier).
- `summarize(candidates, category, select_models, write_models)` enchaîne 3 étapes :
  1. `choose` : un appel (`select_models` = `LLM_MODELS_CLUSTER`, Lite) choisit et classe exactement `category.topic_count` sujets, avec titre et 300 caractères par article. Réponse `{"topics": [{"ids": [...]}]}` ; plusieurs numéros = candidats fusionnés (même affaire). Numéros invalides ou déjà pris ignorés. S'il manque des sujets, le code complète avec les candidats suivants dans l'ordre de `rank_key`.
  2. `fetch_full_texts` : `fetch_text` sur les `ARTICLES_PER_TOPIC` = 3 premiers articles de chaque sujet retenu (sauf pages `news.ycombinator.com/item`) ; le texte complet remplace l'extrait seulement s'il est plus long (pages Reddit bloquées : extrait gardé).
  3. `write` : un appel (`write_models` = `LLM_MODELS_SUMMARY`, Flash) écrit un texte de 160 à 180 mots par sujet (oral, sans lien ni Markdown) à partir de `TEXT_CHARS` = 4000 caractères par article. Réponse `{"topics": [{"id", "title", "text"}]}`. Le rang suit l'ordre de `choose`.
- Validation de `write` : id inconnu, répété ou texte vide ignorés ; `clean_spoken` retire URL et caractères Markdown ; titre vide : titre du premier article ; aucun sujet utilisable ou JSON invalide : `LLMError`. Les sources d'un sujet sont tous ses articles (candidats fusionnés compris), pas seulement les 3 lus.

## Point d'entrée (`src/veille_ia/main.py`)
- `run(category, now, report_dir, seen_path)` : `collect_all(category)` (HN enrichi, blogs, Reddit), `dedup.filter_new`, `cluster.cluster` (`LLM_MODELS_CLUSTER`, relancé une fois si moins de `category.topic_count` candidats), `summary.select_candidates`, `summary.summarize`, écriture de `data/<category.id>/AAAA-MM-JJ.json`, puis `dedup.mark_seen` sur les articles des sujets retenus uniquement. Renvoie le chemin, ou `None` s'il n'y a rien à écrire. Un second run le même jour écrase le fichier du jour.
- Appels LLM par run : 2 Lite (regroupement, choix), 3 si relance ; 1 Flash (rédaction).
- Format du JSON : `{"date", "category": <id de la catégorie>, "topics": [{"rank", "title", "text", "sources": [{"name", "title", "url"}]}]}`.
- `main(ids=None)` charge `.env`, lance `run()` pour chaque catégorie demandée (toutes par défaut, voir `memoire/categories.md`) et affiche le nombre de sujets et de mots. Une exception sur une catégorie est affichée (`<id> : échec : …`) sans arrêter les suivantes ; si au moins une a échoué, le processus se termine avec le code 1. Lancement : `python scripts\run_agent.py [id ...]` (appelle `main(sys.argv[1:])` après `sys.path.insert(0, "src")`).
- Variable absente : `LLMError("Missing environment variable …")`.

## Planification Windows
- `scripts\run_daily.ps1` : se place à la racine du projet, force `PYTHONUTF8=1`, lance `python scripts\run_agent.py` (toutes les catégories, l'une après l'autre : environ 5 minutes) et ajoute la sortie (début, fin, code de sortie) à `data\logs\AAAA-MM-JJ.log` (`data/` est ignoré par Git). Code de sortie 1 si une catégorie a échoué. Lançable à la main.
- `scripts\register_task.ps1 [-Heure 08:00]` : crée ou remplace la tâche `VeilleIA` (quotidienne, `powershell.exe -File run_daily.ps1`) avec `StartWhenAvailable` (rattrapage si la machine était éteinte), lancement sur batterie autorisé et réseau requis. Supprimer la tâche : `Unregister-ScheduledTask -TaskName VeilleIA -Confirm:$false`.
- Le reset du quota Google (environ 9h à Paris, non vérifié) peut faire consommer le quota de la veille à 8h.

## Essais réels
- 2026-11-03, ancien déroulé (un seul appel qui choisissait et écrivait) : 2 sujets et 320 mots, puis 6 sujets et 849 mots après durcissement du prompt.
- 2026-11-04, déroulé actuel, 2 runs : un run en échec (tous les modèles Flash en 503, avant l'ajout de `gemini-3.5-flash-lite` en repli), un run à 6 sujets et 934 mots (150 à 167 mots par sujet), dont un sujet fusionné à 5 sources et un blog OpenAI.
- 2026-11-04, après ajout du repli Lite : un run avec historique vide a redonné les mêmes 6 sujets dans le même ordre que le run précédent (889 mots, 141 à 157 mots par sujet ; titres sans accents et très courts, peut-être écrits par le modèle de repli). Un run avec l'historique du run précédent a écarté ces 6 sujets et en a choisi 6 autres (1 024 mots, 161 à 177 mots par sujet), comme un run du lendemain.
- 2026-11-04, 4 catégories par la tâche `VeilleIA` (`Start-ScheduledTask`, 5 minutes) : `cyber` 4 sujets et 589 mots, `reseau` 2 sujets et 329 mots, `cloud` « aucun nouvel article » (cause trouvée ensuite : le regroupement classait les 32 articles en `off_topic`, corrigé dans `cluster.py`, voir `memoire/traitement.md` ; le message « aucun nouvel article » est aussi affiché dans ce cas), `ia` en échec (tous les modèles Lite en 503 « high demand ») ; code de sortie 1, le JSON `ia` du matin est resté intact. Un 503 sur tous les modèles d'une liste fait échouer la catégorie (pas de nouvelle tentative).
- Tests : `tests/test_summary.py` et `tests/test_main.py` avec faux `llm.complete` et faux `fetch_text`.
