---
quand_lire: Tu ajoutes ou modifies un collecteur de news, le type Article, la recherche Hacker News ou la lecture complète des pages
couvre: src/veille_ia/models.py, src/veille_ia/fulltext.py, src/veille_ia/collectors/, tests/test_hn.py, tests/test_fulltext.py, tests/test_blogs.py, tests/test_reddit.py, scripts/try_hn.py, scripts/try_all.py
verifie: 2026-11-04
---
# Collecte des articles

## Type commun (`src/veille_ia/models.py`)
- `Article(title, url, source, published, score=0, text="")` : `published` est un timestamp Unix. Tous les collecteurs doivent renvoyer des `Article`.

## Hacker News (`src/veille_ia/collectors/hn.py`)
- `collect(now=None)` interroge l'API Algolia `search_by_date` (sans clé) pour chaque mot-clé de `KEYWORDS` (`AI`, `LLM`, `GPT`, `OpenAI`, `Anthropic`, `Claude`, `Gemini`, `machine learning`), avec `tags=story`, 50 résultats par requête, dernières 24 h (`WINDOW_SECONDS`) et au moins `MIN_POINTS` = 20 points.
- Dédoublonnage par `objectID`, tri par score décroissant. Sans URL externe, l'URL de l'article est la page de discussion `https://news.ycombinator.com/item?id=…`. Source : `"Hacker News"`.
- `enrich(articles)` remplit `text` avec `fetch_text`, sauf pour les URL contenant `news.ycombinator.com/item`.
- Un essai réel (`scripts/try_hn.py`) a renvoyé 36 articles, dont du bruit hors IA (le mot-clé `AI` est large) et des articles repris sur plusieurs sites.

## Flux RSS (`src/veille_ia/collectors/rss.py`)
- `collect_feed(url, source, now=None)` télécharge le flux avec `requests` (User-Agent `veille-ia/0.1`, délai 30 s), l'analyse avec `feedparser` et garde les entrées des dernières 24 h (date `published` sinon `updated`, entrées sans date ignorées).
- `text` = résumé du flux sans balises HTML, tronqué à `MAX_TEXT` = 2000 (pas de lecture complète). `score` reste à 0.
- Erreur réseau ou HTTP : avertissement dans le journal et liste vide, les autres flux continuent.

## Blogs d'éditeurs (`src/veille_ia/collectors/blogs.py`)
- `collect(now=None)` parcourt `FEEDS` : OpenAI, Hugging Face, Google AI (flux IA global de blog.google, pas seulement DeepMind) et Anthropic (relais communautaire `Olshansk/rss-feeds`, Anthropic n'a pas de flux natif ; le relais peut prendre du retard).
- arXiv est abandonné (décision utilisateur) : environ 2 000 articles par jour sans score, trop pour le regroupement LLM.

## Reddit (`src/veille_ia/collectors/reddit.py`)
- `collect(now=None)` lit le flux Atom `.rss` de r/MachineLearning et r/LocalLLaMA via `collect_feed`. Pas de score (`score` = 0).
- Essai réel du 2026-11-03 : r/MachineLearning répond (14 articles sur 24 h, surtout des discussions `[D]` peu liées à l'actualité) ; r/LocalLLaMA répond 429 (403 sur `old.reddit.com`) et est donc sauté. À retester plus tard.

## Lecture complète (`src/veille_ia/fulltext.py`)
- `fetch_text(url)` télécharge la page (User-Agent `Mozilla/5.0 (veille-ia)`, délai 20 s), extrait le texte avec `trafilatura` et le tronque à `MAX_CHARS` = 8000.
- Il renvoie `""` en cas d'erreur réseau ou HTTP, ou si rien n'est extrait. Sites payants ou bloqués : texte vide, seul le titre reste exploitable.

## Tests
- `tests/test_hn.py` et `tests/test_fulltext.py` remplacent `requests.get` et `trafilatura.extract` par de faux objets.
