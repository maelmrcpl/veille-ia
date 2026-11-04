---
quand_lire: Tu ajoutes ou modifies une catégorie de veille (IA, cyber, réseau, cloud), ses sources, son libellé ou son nombre de sujets
couvre: src/veille_ia/categories.py, tests/test_categories.py
verifie: 2026-11-04
---
# Catégories de veille

- `src/veille_ia/categories.py` : `Category(id, label, topic_count, hn_keywords, blog_feeds, reddit_feeds)` et le dictionnaire `CATEGORIES` (clé = `id`). Une catégorie regroupe tout ce qui change d'un sujet de veille à l'autre ; le reste du code est commun.
- `label` est inséré dans les prompts du regroupement et du résumé (« domaine « {label} » »). `topic_count` est le nombre de sujets du JSON du jour.
- Catégories présentes :
  - `ia` (`topic_count` = 5) : mots-clés HN, blogs OpenAI, Hugging Face, Google AI et Anthropic, subreddits r/MachineLearning et r/LocalLLaMA.
  - `cyber` (`topic_count` = 4, libellé « cybersécurité ») : sites BleepingComputer, The Hacker News, SecurityWeek, Dark Reading, Krebs on Security, Schneier on Security ; mots-clés HN `security`, `cybersecurity`, `vulnerability`, `ransomware`, `breach`, `malware`, `exploit`, `zero-day`, `phishing`, `hackers` ; subreddits r/netsec et r/cybersecurity. Les sites cyber sont dans `blog_feeds`, donc comptés comme « blogs officiels » dans le classement de `summary.rank_key`.
  - Prévues, pas encore écrites : `reseau` (4), `cloud` (2).
- Essai réel cyber (2026-11-04) : 48 articles collectés, 4 sujets, 661 mots. Reddit répond 429 (r/netsec une fois sur deux, r/cybersecurity jamais) et est sauté. CISA (`cisa.gov/cybersecurity-advisories/all.xml`) répond 403 et n'est pas utilisé ; le flux CERT-FR des alertes était vide sur 7 jours. Le mot-clé HN `CVE` est écarté : 20 résultats presque tous hors sujet.
- Ajouter une catégorie : une entrée de `CATEGORIES`, sans autre changement de code. Elle est alors lancée par défaut par `python scripts\run_agent.py` (sans argument : toutes les catégories ; avec arguments : `python scripts\run_agent.py cyber ia`).
- Sortie : `data/<id>/AAAA-MM-JJ.json`. L'historique des articles vus (`data/seen_urls.json`) est partagé entre catégories.
