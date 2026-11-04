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
  - `cloud` (`topic_count` = 2, libellé « cloud, DevOps et infrastructure informatique ») : AWS News Blog, Google Cloud, Azure, Kubernetes, CNCF, Cloudflare, Docker, GitHub, The New Stack, InfoQ ; mots-clés HN `kubernetes`, `devops`, `cloud`, `Docker`, `Terraform`, `outage`, `infrastructure`, `Cloudflare`, `Azure`, `serverless` ; subreddits r/devops et r/kubernetes (429 la plupart du temps).
  - Prévue, pas encore écrite : `reseau` (4).
- Essai réel cyber (2026-11-04) : 48 articles collectés, 4 sujets, 661 mots. Reddit répond 429 (r/netsec une fois sur deux, r/cybersecurity jamais) et est sauté. CISA (`cisa.gov/cybersecurity-advisories/all.xml`) répond 403 et n'est pas utilisé ; le flux CERT-FR des alertes était vide sur 7 jours. Le mot-clé HN `CVE` est écarté : 20 résultats presque tous hors sujet.
- Essai réel cloud (2026-11-04) : 30 articles collectés (peu de nouvelles cloud, beaucoup de bruit IA), 2 sujets. DevOps.com répond 403 et n'est pas utilisé. Le mot-clé HN `AWS` est écarté (21 résultats sans rapport avec AWS). Avec l'ancienne consigne de `cluster.py`, le modèle classait presque tout en `off_topic` (0 puis 1 sujet) ; la consigne précise maintenant qu'un article du domaine sans équivalent n'est pas hors sujet et reste seul dans son sujet (voir `memoire/traitement.md`).
- Longueur : les textes sortent à 134-170 mots par sujet quand Flash répond, 60-78 quand le repli Lite semble avoir rédigé (non confirmé : le modèle utilisé n'est pas journalisé).
- Ajouter une catégorie : une entrée de `CATEGORIES`, sans autre changement de code. Elle est alors lancée par défaut par `python scripts\run_agent.py` (sans argument : toutes les catégories ; avec arguments : `python scripts\run_agent.py cyber ia`).
- Sortie : `data/<id>/AAAA-MM-JJ.json`. L'historique des articles vus (`data/seen_urls.json`) est partagé entre catégories.
