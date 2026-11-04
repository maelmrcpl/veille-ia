import base64
import wave

import pytest

from veille_ia import audio, tts
from veille_ia.categories import CATEGORIES
from veille_ia.llm import LLMError

PCM = b"\x01\x00" * 100


class FakeResponse:
    def __init__(self, status_code=200, pcm=PCM, text="", body=None):
        self.status_code = status_code
        self.ok = status_code < 400
        self.text = text
        self._body = body or {
            "candidates": [
                {"content": {"parts": [{"inlineData": {"data": base64.b64encode(pcm).decode()}}]}}
            ]
        }

    def json(self):
        return self._body


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setattr(tts, "load_dotenv", lambda: None)
    monkeypatch.setenv("LLM_API_KEY", "secret")
    monkeypatch.setattr(tts.time, "sleep", lambda s: None)
    monkeypatch.setattr(tts, "_wait_for_slot", lambda model, rpm: None)
    tts._exhausted.clear()


def test_parse_list():
    assert tts.parse_list("a, b,,c") == ["a", "b", "c"]


def test_synthesize_builds_request_and_decodes_audio(monkeypatch):
    calls = []

    def fake_post(url, headers, json, timeout):
        calls.append((url, headers, json))
        return FakeResponse()

    monkeypatch.setattr(tts.requests, "post", fake_post)
    assert tts.synthesize("Bonjour", "Puck", ["m1"]) == PCM
    url, headers, body = calls[0]
    assert url.endswith("/models/m1:generateContent")
    assert headers == {"x-goog-api-key": "secret"}
    assert body["contents"][0]["parts"][0]["text"] == "Bonjour"
    voice = body["generationConfig"]["speechConfig"]["voiceConfig"]["prebuiltVoiceConfig"]
    assert voice["voiceName"] == "Puck"


def test_synthesize_falls_back_on_quota_and_missing_audio(monkeypatch):
    replies = {
        "m1": FakeResponse(429),
        "m2": FakeResponse(body={"candidates": [{"finishReason": "OTHER"}]}),
        "m3": FakeResponse(),
    }
    monkeypatch.setattr(
        tts.requests, "post", lambda url, headers, json, timeout: replies[url.split("/")[-1].split(":")[0]]
    )
    assert tts.synthesize("x", "Puck", ["m1", "m2", "m3"]) == PCM
    assert tts._exhausted == {"m1"}


def test_synthesize_raises_when_all_exhausted(monkeypatch):
    monkeypatch.setattr(tts.requests, "post", lambda url, headers, json, timeout: FakeResponse(429))
    with pytest.raises(LLMError, match="exhausted"):
        tts.synthesize("x", "Puck", ["m1"])


def test_synthesize_raises_on_other_error(monkeypatch):
    monkeypatch.setattr(tts.requests, "post", lambda url, headers, json, timeout: FakeResponse(400))
    with pytest.raises(LLMError, match="HTTP 400"):
        tts.synthesize("x", "Puck", ["m1"])


def test_write_and_read_wav(tmp_path):
    path = str(tmp_path / "sub" / "a.wav")
    tts.write_wav(path, PCM)
    with wave.open(path, "rb") as file:
        assert (file.getnchannels(), file.getsampwidth(), file.getframerate()) == (1, 2, 24000)
    assert tts.read_wav(path) == PCM


REPORT = {
    "date": "2026-11-04",
    "category": "cyber",
    "topics": [{"rank": 1, "title": "Faille", "text": "Texte parlé."}],
}


def test_category_script():
    script = audio.category_script(REPORT, "cybersécurité")
    assert script == "Veille cybersécurité du 4 novembre 2026.\n\nSujet 1 : Faille. Texte parlé."


def test_voice_for_varies_by_category():
    voices = ["A", "B", "C", "D"]
    assert [audio.voice_for(i, voices) for i in CATEGORIES] == voices


def test_category_audio_uses_category_voice(monkeypatch, tmp_path):
    used = []
    monkeypatch.setattr(audio.tts, "synthesize", lambda text, voice, models: used.append(voice) or PCM)
    path = audio.category_audio(
        REPORT, CATEGORIES["cyber"], ["m"], ["A", "B", "C", "D"], data_dir=str(tmp_path)
    )
    assert used == ["B"]
    assert path == str(tmp_path / "cyber" / "2026-11-04.wav")
    assert tts.read_wav(path) == PCM


def test_global_audio_concatenates_intro_and_available_categories(monkeypatch, tmp_path):
    tts.write_wav(str(tmp_path / "ia" / "2026-11-04.wav"), b"\x02\x00" * 10)
    tts.write_wav(str(tmp_path / "reseau" / "2026-11-04.wav"), b"\x03\x00" * 10)
    spoken = []
    monkeypatch.setattr(
        audio.tts, "synthesize", lambda text, voice, models: spoken.append((text, voice)) or PCM
    )
    path = audio.global_audio("2026-11-04", ["m"], ["A", "B"], data_dir=str(tmp_path))
    assert spoken[0][1] == "A"
    assert "4 novembre 2026" in spoken[0][0]
    assert "intelligence artificielle" in spoken[0][0] and "cybersécurité" not in spoken[0][0]
    assert tts.read_wav(path) == PCM + b"\x02\x00" * 10 + b"\x03\x00" * 10


def test_global_audio_none_without_category_audio(tmp_path):
    assert audio.global_audio("2026-11-04", ["m"], ["A"], data_dir=str(tmp_path)) is None
