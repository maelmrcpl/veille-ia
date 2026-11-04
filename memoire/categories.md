---
quand_lire: Tu ajoutes ou modifies une catégorie de veille (IA, cyber, réseau, cloud), ses sources, son libellé ou son nombre de sujets
couvre: src/veille_ia/categories.py
verifie: 2026-11-04
---
# Catégories de veille

- `src/veille_ia/categories.py` : `Category(id, label, topic_count, hn_keywords, blog_feeds, reddit_feeds)` et le dictionnaire `CATEGORIES` (clé = `id`). Une catégorie regroupe tout ce qui change d'un sujet de veille à l'autre ; le reste du code est commun.
- `label` est inséré dans les prompts du regroupement et du résumé (« domaine « {label} » »). `topic_count` est le nombre de sujets du JSON du jour.
- Catégorie présente : `ia` (`topic_count` = 5, mots-clés HN, blogs OpenAI, Hugging Face, Google AI et Anthropic, subreddits r/MachineLearning et r/LocalLLaMA). Prévues, pas encore écrites : `cyber` (4 sujets), `reseau` (4), `cloud` (2).
- Ajouter une catégorie : une entrée de `CATEGORIES`, sans autre changement de code. Elle est alors lancée par défaut par `python scripts\run_agent.py` (sans argument : toutes les catégories ; avec arguments : `python scripts\run_agent.py cyber ia`).
- Sortie : `data/<id>/AAAA-MM-JJ.json`. L'historique des articles vus (`data/seen_urls.json`) est partagé entre catégories.
