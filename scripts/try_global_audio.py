import sys

sys.path.insert(0, "src")

from dotenv import load_dotenv

from veille_ia import audio, tts

load_dotenv()
date = sys.argv[1] if len(sys.argv) > 1 else "2026-11-04"
print(audio.global_audio(date, tts.list_from_env("TTS_MODELS"), tts.list_from_env("VOICES")))
