import json
import sys

sys.path.insert(0, "src")

from dotenv import load_dotenv

from veille_ia import audio, tts
from veille_ia.categories import CATEGORIES

load_dotenv()
category = CATEGORIES[sys.argv[1] if len(sys.argv) > 1 else "cyber"]
path = sys.argv[2] if len(sys.argv) > 2 else f"data\\{category.id}\\2026-11-04.json"
with open(path, encoding="utf-8") as file:
    report = json.load(file)
models, voices = tts.list_from_env("TTS_MODELS"), tts.list_from_env("VOICES")
print(audio.category_audio(report, category, models, voices))
