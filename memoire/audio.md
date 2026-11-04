---
quand_lire: Tu modifies la génération audio (TTS), les voix, les fichiers WAV ou l'audio global du jour
couvre: src/veille_ia/tts.py, src/veille_ia/audio.py, tests/test_tts.py, scripts/try_tts.py, scripts/try_global_audio.py
verifie: 2026-11-04
---
# Audio (TTS)

## Client (`src/veille_ia/tts.py`)
- `synthesize(text, voice, models)` : POST sur l'API native `https://generativelanguage.googleapis.com/v1beta/models/<modèle>:generateContent` (en-tête `x-goog-api-key` = `LLM_API_KEY`, `responseModalities` = `AUDIO`, voix = `prebuiltVoiceConfig`). Renvoie le PCM décodé (16 bits, mono, 24 kHz).
- Repli identique à `llm.complete` (voir `memoire/llm.md`) : 404 et 429 écartent le modèle pour le processus, 503 déclenche des tours après attente (30 puis 60 s). Une réponse 200 sans audio passe au modèle suivant. Le limiteur est `llm._wait_for_slot` avec `TTS_RPM` = 3.
- `write_wav` / `read_wav` : module `wave` de la bibliothèque standard.
- Variables : `TTS_MODELS` (noms séparés par des virgules, sans RPM) et `VOICES` (noms de voix). Clé : `LLM_API_KEY`.

## Quotas (déclarés par l'utilisateur, par modèle)
`gemini-3.8-flash-tts` et `gemini-3.8-flash-tts-lite` : 3 RPM, 10K TPM, 10 RPD chacun. Consommation : 1 requête par catégorie + 1 pour l'intro globale = 5 par jour (4 si une catégorie n'a rien).

## Orchestration (`src/veille_ia/audio.py`)
- `category_script` : « Veille <libellé> du <date> », puis « Sujet <rang> : <titre>. <texte> » pour chaque sujet. Une requête par catégorie.
- Voix : `voice_for` prend `VOICES[position de la catégorie dans CATEGORIES % nombre de voix]` ; une seule voix par audio généré. Intro globale : première voix.
- `category_audio` écrit `data/<id>/AAAA-MM-JJ.wav`. `global_audio` génère une intro (date et libellés des catégories dont le WAV du jour existe), puis concatène intro + WAV des catégories dans `data/AAAA-MM-JJ.wav` (ordre de `CATEGORIES`).
- `main.main` appelle l'audio après chaque JSON, puis l'audio global en fin de run. Un échec audio est affiché (`<id> : audio : échec : …`) sans arrêter le run ni changer le code de sortie.
- `scripts/try_tts.py [id] [chemin.json]` : essai réel d'un audio de catégorie (1 requête, quota consommé).
- Tests : `tests/test_tts.py` (fausse `requests`) et un test dans `tests/test_main.py`.
- Essais réels du 2026-11-04 : `cyber` (589 mots) = 205 s, 1 requête ; `cloud` = 5,1 Mo (environ 106 s) ; global = intro d'environ 10 s + `cyber` + `cloud`, 15,4 Mo. Une catégorie tient dans une seule réponse audio (testé jusqu'à 589 mots ; `ia`, plus longue, non testée). Écoute humaine non faite par l'agent.
- `scripts/try_global_audio.py [AAAA-MM-JJ]` : essai réel du global (1 requête pour l'intro) à partir des WAV de catégorie déjà présents.
