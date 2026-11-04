import base64
import os
import time
import wave

import requests
from dotenv import load_dotenv

from veille_ia.llm import LLMError, _wait_for_slot

TTS_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
TTS_RPM = 3
SAMPLE_RATE = 24000
DEFAULT_TIMEOUT = 600
OVERLOAD_WAITS = (30, 60)

_exhausted = set()


def parse_list(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def list_from_env(name):
    value = os.environ.get(name)
    if not value:
        raise LLMError(f"Missing environment variable {name}")
    return parse_list(value)


def synthesize(text, voice, models):
    load_dotenv()
    key = os.environ.get("LLM_API_KEY")
    if not key:
        raise LLMError("Missing environment variable LLM_API_KEY")
    body = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }

    errors = []
    for wait in (0, *OVERLOAD_WAITS):
        if wait:
            print(f"TTS : tous les modèles surchargés, nouvelle tentative dans {wait} s")
            time.sleep(wait)
        overloaded = False
        for model in models:
            if model in _exhausted:
                continue
            _wait_for_slot(model, TTS_RPM)
            response = requests.post(
                TTS_URL.format(model=model),
                headers={"x-goog-api-key": key},
                json=body,
                timeout=DEFAULT_TIMEOUT,
            )
            if response.status_code in (404, 429, 503):
                if response.status_code == 503:
                    overloaded = True
                else:
                    _exhausted.add(model)
                print(f"TTS : {model} indisponible (HTTP {response.status_code})")
                errors.append(f"{model}: {response.text}")
                continue
            if not response.ok:
                raise LLMError(f"{model}: HTTP {response.status_code}: {response.text}")
            try:
                data = response.json()["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            except (KeyError, IndexError):
                print(f"TTS : {model} n'a pas renvoyé d'audio")
                errors.append(f"{model}: no audio in response")
                continue
            print(f"TTS : {model} ({voice})")
            return base64.b64decode(data)
        if not overloaded:
            break
    raise LLMError("All TTS models exhausted. " + " | ".join(errors))


def write_wav(path, pcm):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(SAMPLE_RATE)
        file.writeframes(pcm)


def read_wav(path):
    with wave.open(path, "rb") as file:
        return file.readframes(file.getnframes())
