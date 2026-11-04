import os
import time

import requests
from dotenv import load_dotenv

DEFAULT_TIMEOUT = 600
OVERLOAD_WAITS = (30, 60)

_last_call = {}
_exhausted = set()


class LLMError(Exception):
    pass


def parse_models(value):
    models = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        name, _, rpm = item.partition(":")
        if not rpm.isdigit() or int(rpm) <= 0:
            raise LLMError(f"Invalid model entry '{item}', expected 'name:rpm'")
        models.append((name, int(rpm)))
    return models


def _get_env(name):
    value = os.environ.get(name)
    if not value:
        raise LLMError(f"Missing environment variable {name}")
    return value


def _wait_for_slot(model, rpm):
    interval = 60 / rpm
    last = _last_call.get(model)
    if last is not None:
        delay = interval - (time.monotonic() - last)
        if delay > 0:
            time.sleep(delay)
    _last_call[model] = time.monotonic()


def complete(prompt, models, system=None):
    load_dotenv()
    url = _get_env("LLM_API_URL")
    key = _get_env("LLM_API_KEY")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    errors = []
    for wait in (0, *OVERLOAD_WAITS):
        if wait:
            print(f"LLM : tous les modèles surchargés, nouvelle tentative dans {wait} s")
            time.sleep(wait)
        overloaded = False
        for model, rpm in models:
            if model in _exhausted:
                continue
            _wait_for_slot(model, rpm)
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {key}"},
                json={"model": model, "messages": messages, "temperature": 0},
                timeout=DEFAULT_TIMEOUT,
            )
            if response.status_code in (404, 429, 503):
                if response.status_code == 503:
                    overloaded = True
                else:
                    _exhausted.add(model)
                print(f"LLM : {model} indisponible (HTTP {response.status_code})")
                errors.append(f"{model}: {response.text}")
                continue
            if not response.ok:
                raise LLMError(f"{model}: HTTP {response.status_code}: {response.text}")
            print(f"LLM : {model}")
            return response.json()["choices"][0]["message"]["content"]
        if not overloaded:
            break
    raise LLMError("All models exhausted. " + " | ".join(errors))
