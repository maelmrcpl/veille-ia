---
quand_lire: Tu reprends le développement de l'agent de veille IA dans une nouvelle session, ou tu commences ou termines une phase du plan
couvre:
---
# Plan de développement de l'agent de veille IA

Fichier temporaire de reprise de session : à supprimer en phase 8, une fois la mémoire remplie par `/onboard create`. Dernière mise à jour : 2026-11-03.

## Règles de travail (convenues avec l'utilisateur)
- Exécution **step by step** : rappeler le plan global au début de chaque phase, détailler la phase, attendre l'accord avant la suivante.
- **Git : jamais de commit, push, ni changement de branche par l'IA.** L'IA donne à l'utilisateur la branche à créer, les commits (message en anglais, Conventional Commits : `feat:`, `chore:`, `docs:`, `test:`), la PR (titre et description proposés), le *Squash and merge* sur GitHub, puis `git switch main` et `git pull`.
- Une branche par phase, créée depuis `main` à jour. `main` ne reçoit que des PR. CI `memoire` verte avant fusion.
- Phase importante = sous-tâches : s'arrêter après chacune pour demander à l'utilisateur de commiter.
- Avant de coder, demander à l'utilisateur de confirmer qu'il est sur la bonne branche (`git branch --show-current`).
- Fin de phase : lancer `python -m pytest` et `.\scripts\routeur.ps1 -Verifier`, et dire ce qui a été lancé.
- Après `git add -N .` le vérificateur voit les nouveaux fichiers (il lit `git ls-files`).
- Tout nouveau fichier de code doit être cité dans le `couvre` d'un fichier de mémoire (`memoire/llm.md`, `memoire/collecte.md`, `memoire/principes.md`, ou un nouveau fichier) : `memoire/_ignore.txt` ne contient plus de ligne temporaire.
- Ne jamais lire `.env` ni afficher une clé. `git diff` peut en révéler : vérifier que `.env.example` ne contient aucune valeur secrète avant chaque commit (la clé API y a déjà été écrite par erreur une fois, puis remise à vide).
- Langue : français pour les échanges, anglais pour le code et les noms de fichiers.
- Python (3.13) pour tout le code. `pytest` installé dans le Python global (pas de venv créé).

## Objectif
Un agent Python qui chaque jour vers 8h collecte les actualités IA, les regroupe et les résume en français (5 à 7 sujets classés par importance, environ 1 000 mots, soit 5 minutes de lecture), et écrit un JSON du jour. Objectifs suivants hors périmètre actuel : web GUI multi-sujets et audio lisant les nouvelles par catégorie (le texte doit donc être rédigé pour l'oral : sans liens ni mise en forme dans le texte parlé).

## État d'avancement
| Phase | Branche | État |
|---|---|---|
| 1. Squelette Python | `chore/project-skeleton` | Fait, fusionnée |
| 2. Client LLM | `feat/llm-client` | Fait, fusionnée |
| 3. Collecte HN avec lecture complète | `feat/hn-collector` | Fait, fusionnée |
| 4. Collecte blogs et Reddit (arXiv abandonné) | `feat/other-collectors` | Fait (4a blogs, 4b Reddit, 4c `scripts/try_all.py`), à fusionner |
| 5. Déduplication et regroupement | `feat/dedup-clustering` | 5a, 5b et 5c faits (essai réel fait, regroupement à affiner, voir `memoire/traitement.md`) |
| 6. Sélection et résumé | `feat/daily-summary` | Code et tests faits (49 tests, `memoire/resume.md`) ; essai réel Flash : 6 sujets, 849 mots (regroupement instable, voir `memoire/resume.md`) |
| 7. Planification Windows 8h | `feat/scheduling` | À faire |
| 8. Mémoire finale | `docs/memory` | `/onboard create` fait (4 fichiers) ; reste `/onboard update` et suppression de `PLAN.md` à la fin |

## Code existant (vérifié en session)
- `src/veille_ia/models.py` : `Article(title, url, source, published, score=0, text="")` (`published` en timestamp Unix).
- `src/veille_ia/llm.py` : `complete(prompt, models, system=None)` avec `models` = liste de `(nom, rpm)` (voir `parse_models`). Endpoint chat completions compatible OpenAI (Google AI Studio). Limiteur par modèle (60 / rpm secondes), repli sur erreur 429 vers le modèle suivant, modèle épuisé non retenté pendant l'exécution, `LLMError` si tous épuisés. Lit `LLM_API_URL` et `LLM_API_KEY` (chargés par `python-dotenv`).
- `src/veille_ia/fulltext.py` : `fetch_text(url)` (requests + trafilatura, 8 000 caractères max, texte vide en cas d'erreur).
- `src/veille_ia/collectors/hn.py` : `collect()` (API Algolia, 8 mots-clés, 24 h, 20 points minimum, dédoublonné, trié par score) et `enrich(articles)` (remplit `text`, saute les liens `news.ycombinator.com/item`).
- `src/veille_ia/collectors/rss.py` : `collect_feed(url, source, now)` (requests + feedparser, 24 h, texte = résumé nettoyé, flux en erreur sauté). `blogs.py` (OpenAI, Hugging Face, Google AI, Anthropic via relais `Olshansk/rss-feeds`) et `reddit.py` (r/MachineLearning ; r/LocalLLaMA répond 429, sauté) : `collect(now=None)`. arXiv abandonné (environ 2 000 articles par jour sans score). `scripts/try_all.py` lance les trois collecteurs. 23 tests passent.
- Scripts d'essai : `scripts/try_llm.py` (un appel), `scripts/try_hn.py` (affiche les articles du jour). Ils font `sys.path.insert(0, "src")`.
- Tests : `tests/` avec de faux appels HTTP, aucun réseau ; `pytest.ini` règle `pythonpath = src`. 23 tests passent à la fin de la phase 4.
- `.env.example` : `LLM_API_URL`, `LLM_API_KEY` (vide), `LLM_MODELS_CLUSTER`, `LLM_MODELS_SUMMARY` au format `modèle:rpm`.

## Contraintes LLM (Google AI Studio, offre gratuite, clé API dans `.env`)
Quotas par modèle (RPM, requêtes par jour) : `gemini-3.5-flash-lite` 15 RPM / 500 ; `gemini-3.1-flash-lite` 15 / 500 ; `gemini-2.5-flash-lite` 10 / 20 ; `gemini-2.5-flash` 5 / 20 ; `gemini-3.6-flash` 5 / 20 ; `gemini-3.8-flash` 3 / 20. Les quotas journaliers se remettent à zéro chaque jour (l'utilisateur a hésité sur un blocage mensuel, non confirmé : à vérifier si un modèle reste en 429 plusieurs jours).
- Regroupement et petits traitements : `LLM_MODELS_CLUSTER` (Lite, 500 par jour). Résumé final : `LLM_MODELS_SUMMARY` (Flash, 20 par jour, qualité).
- Le reset quotidien Google serait à minuit heure du Pacifique, environ 9h à Paris (non vérifié). Un run à 8h pourrait consommer le quota de la veille.
- Budget visé : environ 3 à 6 appels LLM par run.

## Phases à faire

### Phase 4 : arXiv, blogs, Reddit (`feat/other-collectors`)
- Sous-tâches suggérées : 4a arXiv, 4b blogs d'éditeurs, 4c Reddit, 4d script d'essai `scripts/try_all.py` (ou équivalent) ; un commit par sous-tâche.
- Un module par source dans `src/veille_ia/collectors/`, chacun renvoie des `Article` (champ `text` = extrait fourni par le flux, pas de lecture complète pour le POC).
- Sources : arXiv (cs.AI, cs.LG, cs.CL, flux RSS ou API), blogs OpenAI, Anthropic, Google DeepMind, Hugging Face (flux RSS), Reddit r/MachineLearning et r/LocalLLaMA (flux RSS).
- Filtre sur les dernières 24 h. Parser les flux RSS (bibliothèque à choisir, par exemple `feedparser`, à ajouter à `requirements.txt`).
- Risque : Reddit et certains sites bloquent les scripts (User-Agent). Tester en réel et signaler.
- Vérification : tests sur flux simulés, plus un lancement réel par source.
- Commit final type : `feat: collect arxiv, blogs and reddit`.

### Phase 5 : déduplication et regroupement (`feat/dedup-clustering`)
- Exclure les articles déjà traités les jours précédents (historique à lire dans les JSON passés de `data/ia/`, ou dans un fichier d'URL déjà vues : choisir la solution la plus simple et la justifier).
- Regroupement LLM des articles qui parlent du même événement (exemple observé en phase 3 : plusieurs articles sur l'introduction en bourse d'Anthropic). Un groupe devient un seul sujet qui garde toutes ses sources. Utiliser `LLM_MODELS_CLUSTER`, en un seul appel si possible (sortie JSON), avec validation de la réponse.
- Le bruit hors sujet IA vu en phase 3 (Ubuntu 0day, Intel, jeux) peut être écarté ici ou en phase 6.
- Vérification : test avec deux articles sur le même événement qui donnent un seul sujet ; faux client LLM.

### Phase 6 : sélection et résumé (`feat/daily-summary`)
- Classer les sujets par importance (un sujet repris par plusieurs sources compte plus) et en garder 5 à 7.
- Résumé en français, texte rédigé pour l'oral (pas de liens ni de Markdown dans le texte), environ 1 000 mots au total. Ne rien inventer : s'appuyer uniquement sur les textes collectés. Utiliser `LLM_MODELS_SUMMARY`.
- Écrire `data/ia/AAAA-MM-JJ.json` : par sujet, titre, texte parlé, sources (nom, titre, URL), rang. Pas de fichier Markdown (décision de l'utilisateur). Format réutilisable pour les futurs sujets (cyber, réseau).
- Demander à l'utilisateur si `data/` est versionné ou ajouté à `.gitignore`.
- Point d'entrée unique de l'agent (par exemple `python -m veille_ia` ou `src/veille_ia/main.py`) qui enchaîne collecte, dédoublonnage, regroupement, résumé, écriture.
- Vérification : JSON conforme au schéma, total d'environ 1 000 mots, tests avec faux LLM, un run réel.

### Phase 7 : planification Windows (`feat/scheduling`)
- Une commande de lancement unique (script `.ps1` ou `.bat` dans `scripts/` appelant Python avec l'environnement voulu).
- Tâche du Planificateur de tâches Windows chaque jour vers 8h, avec « exécuter dès que possible si l'heure de démarrage est manquée » (rattrapage si la machine était éteinte). L'utilisateur a refusé GitHub Actions pour l'instant.
- Contrainte PowerShell : mode restreint (Constrained Language Mode), uniquement des cmdlets. Fournir la commande de création de tâche à l'utilisateur ou un script dans `scripts/`.
- Vérification : exécution manuelle de la tâche, JSON du jour créé.

### Phase 8 : mémoire finale (`docs/memory`)
- `/onboard create` a été lancé après la phase 3 : `memoire/architecture.md`, `memoire/principes.md`, `memoire/llm.md` et `memoire/collecte.md` existent. À chaque phase, mettre à jour les fichiers concernés (ou lancer `/onboard update`) et couvrir tout nouveau fichier de code dans un `couvre`.
- En phase 8 : lancer `/onboard update`, supprimer `memoire/PLAN.md` (ce fichier), puis `.\scripts\routeur.ps1` et `.\scripts\routeur.ps1 -Verifier`.

## Points ouverts
- La clé API Google a été affichée une fois dans une session : l'utilisateur a été invité à la régénérer (non confirmé).
- Mots-clés HN à resserrer si le bruit gêne (`AI` est large).
- Articles HN à texte vide (sites payants, « Ask HN », certains sites) : acceptés pour le POC, seul le titre est utilisé.
- Quota mensuel éventuel sur les modèles Flash : à confirmer par l'usage.
