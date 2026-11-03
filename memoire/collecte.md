---
quand_lire: Tu ajoutes ou modifies un collecteur de news, le type Article, la recherche Hacker News ou la lecture complète des pages
couvre: src/veille_ia/models.py, src/veille_ia/fulltext.py, src/veille_ia/collectors/, tests/test_hn.py, tests/test_fulltext.py, scripts/try_hn.py
verifie: 2026-11-03
---
# Collecte des articles

## Type commun (`src/veille_ia/models.py`)
- `Article(title, url, source, published, score=0, text="")` : `published` est un timestamp Unix. Tous les collecteurs doivent renvoyer des `Article`.

## Hacker News (`src/veille_ia/collectors/hn.py`)
- `collect(now=None)` interroge l'API Algolia `search_by_date` (sans clé) pour chaque mot-clé de `KEYWORDS` (`AI`, `LLM`, `GPT`, `OpenAI`, `Anthropic`, `Claude`, `Gemini`, `machine learning`), avec `tags=story`, 50 résultats par requête, dernières 24 h (`WINDOW_SECONDS`) et au moins `MIN_POINTS` = 20 points.
- Dédoublonnage par `objectID`, tri par score décroissant. Sans URL externe, l'URL de l'article est la page de discussion `https://news.ycombinator.com/item?id=…`. Source : `"Hacker News"`.
- `enrich(articles)` remplit `text` avec `fetch_text`, sauf pour les URL contenant `news.ycombinator.com/item`.
- Un essai réel (`scripts/try_hn.py`) a renvoyé 36 articles, dont du bruit hors IA (le mot-clé `AI` est large) et des articles repris sur plusieurs sites.

## Lecture complète (`src/veille_ia/fulltext.py`)
- `fetch_text(url)` télécharge la page (User-Agent `Mozilla/5.0 (veille-ia)`, délai 20 s), extrait le texte avec `trafilatura` et le tronque à `MAX_CHARS` = 8000.
- Il renvoie `""` en cas d'erreur réseau ou HTTP, ou si rien n'est extrait. Sites payants ou bloqués : texte vide, seul le titre reste exploitable.

## Tests
- `tests/test_hn.py` et `tests/test_fulltext.py` remplacent `requests.get` et `trafilatura.extract` par de faux objets.
