---
quand_lire: Tu modifies ou appelles le client LLM ; tu changes les modèles, leurs quotas ou les variables d'environnement LLM
couvre: src/veille_ia/llm.py, tests/test_llm.py, scripts/try_llm.py, .env.example
verifie: 2026-11-03
---
# Client LLM

## Fonctionnement (`src/veille_ia/llm.py`)
- `complete(prompt, models, system=None)` envoie une requête POST chat completions (format OpenAI, `temperature` à 0) et renvoie le texte de `choices[0].message.content`. `models` est une liste de `(nom, rpm)`.
- `parse_models("a:15,b:5")` convertit la valeur d'une variable en liste de `(nom, rpm)` ; `LLMError` si une entrée n'a pas de `:rpm` entier positif.
- Limiteur par modèle : attente d'au moins `60 / rpm` secondes entre deux appels du même modèle (état dans `_last_call`).
- Repli : sur HTTP 429 ou 404 (quota épuisé, modèle retiré), le modèle est marqué épuisé (`_exhausted`, pour la durée du processus) et le suivant est essayé. Sur 503 (surcharge temporaire), le suivant est essayé sans marquer le modèle. Tout autre code d'erreur lève `LLMError` immédiatement. Si tous les modèles sont écartés : `LLMError("All models exhausted. …")` avec le texte des réponses. Un délai dépassé (`requests.ReadTimeout`) n'est pas rattrapé : il remonte tel quel.
- Délai d'attente HTTP : 600 secondes (60 puis 180 étaient trop courts pour le résumé de 1 000 mots). Le fichier `.env` est chargé par `python-dotenv` à chaque appel de `complete`.
- Constat du 2026-11-03 : `gemini-2.5-flash` répondait 404 (« plus disponible pour les nouveaux utilisateurs ») et `gemini-3.8-flash` répondait 503 plusieurs fois ; deux appels de résumé ont dépassé 180 s.

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

Répartition (`.env.example`, alignée sur le `.env` de l'utilisateur au 2026-11-04) : `LLM_MODELS_CLUSTER` = 2 modèles Lite (regroupement et choix des sujets) ; `LLM_MODELS_SUMMARY` = `gemini-3.8-flash`, `gemini-3.6-flash`, puis `gemini-3.5-flash-lite` en dernier repli (rédaction ; Flash souvent en 503). `gemini-2.5-flash` est retiré (404). Si un modèle reste en 429 plusieurs jours (quota mensuel éventuel), c'est à confirmer par l'usage.
