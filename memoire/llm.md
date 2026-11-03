---
quand_lire: Tu modifies ou appelles le client LLM ; tu changes les modèles, leurs quotas ou les variables d'environnement LLM
couvre: src/veille_ia/llm.py, tests/test_llm.py, scripts/try_llm.py, .env.example
verifie: 2026-11-03
---
# Client LLM

## Fonctionnement (`src/veille_ia/llm.py`)
- `complete(prompt, models, system=None)` envoie une requête POST chat completions (format OpenAI) et renvoie le texte de `choices[0].message.content`. `models` est une liste de `(nom, rpm)`.
- `parse_models("a:15,b:5")` convertit la valeur d'une variable en liste de `(nom, rpm)` ; `LLMError` si une entrée n'a pas de `:rpm` entier positif.
- Limiteur par modèle : attente d'au moins `60 / rpm` secondes entre deux appels du même modèle (état dans `_last_call`).
- Repli : sur HTTP 429, le modèle est marqué épuisé (`_exhausted`, pour la durée du processus) et le suivant est essayé. Tout autre code d'erreur lève `LLMError` immédiatement. Si tous les modèles sont épuisés : `LLMError("All models exhausted. …")` avec le texte des réponses 429.
- Délai d'attente HTTP : 60 secondes. Le fichier `.env` est chargé par `python-dotenv` à chaque appel de `complete`.

## Variables d'environnement (`.env.example`, valeurs réelles dans `.env`)
| Variable | Rôle |
|---|---|
| `LLM_API_URL` | Endpoint chat completions, par défaut celui de Google AI Studio compatible OpenAI. |
| `LLM_API_KEY` | Clé API (secret, jamais dans `.env.example`). |
| `LLM_MODELS_CLUSTER` | Modèles pour le regroupement (phase 5, non implémentée), `nom:rpm` séparés par des virgules. |
| `LLM_MODELS_SUMMARY` | Modèles pour le résumé final (phase 6, non implémentée). |

`scripts/try_llm.py` envoie un appel au premier modèle de `LLM_MODELS_CLUSTER`.

## Modèles et quotas (déclarés par l'utilisateur, offre gratuite Google AI Studio)
| Modèle | RPM | Requêtes par jour |
|---|---|---|
| `gemini-3.5-flash-lite` | 15 | 500 |
| `gemini-3.1-flash-lite` | 15 | 500 |
| `gemini-2.5-flash-lite` | 10 | 20 |
| `gemini-2.5-flash` | 5 | 20 |
| `gemini-3.6-flash` | 5 | 20 |
| `gemini-3.8-flash` | 3 | 20 |

Répartition prévue (inféré du plan) : modèles Lite pour le regroupement, Flash pour le résumé. Si un modèle reste en 429 plusieurs jours (quota mensuel éventuel), c'est à confirmer par l'usage.
