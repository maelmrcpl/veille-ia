import requests
import trafilatura

MAX_CHARS = 8000
TIMEOUT = 20
HEADERS = {"User-Agent": "Mozilla/5.0 (veille-ia)"}


def fetch_text(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return ""
    text = trafilatura.extract(response.text)
    return (text or "")[:MAX_CHARS]
