import os

from veille_ia import tts
from veille_ia.categories import CATEGORIES

DATA_DIR = "data"
MONTHS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def spoken_date(date):
    year, month, day = date.split("-")
    return f"{int(day)} {MONTHS[int(month) - 1]} {year}"


def category_script(report, label):
    parts = [f"Veille {label} du {spoken_date(report['date'])}."]
    for topic in report["topics"]:
        parts.append(f"Sujet {topic['rank']} : {topic['title']}. {topic['text']}")
    return "\n\n".join(parts)


def global_intro(date, labels):
    return (
        f"Bonjour, voici votre veille du {spoken_date(date)}. "
        f"Au programme : {', '.join(labels)}."
    )


def voice_for(category_id, voices):
    return voices[list(CATEGORIES).index(category_id) % len(voices)]


def category_audio(report, category, models, voices, data_dir=DATA_DIR):
    pcm = tts.synthesize(
        category_script(report, category.label), voice_for(category.id, voices), models
    )
    path = os.path.join(data_dir, category.id, f"{report['date']}.wav")
    tts.write_wav(path, pcm)
    return path


def global_audio(date, models, voices, data_dir=DATA_DIR):
    available = [
        c for c in CATEGORIES.values()
        if os.path.exists(os.path.join(data_dir, c.id, f"{date}.wav"))
    ]
    if not available:
        return None
    intro = tts.synthesize(global_intro(date, [c.label for c in available]), voices[0], models)
    pcm = intro + b"".join(
        tts.read_wav(os.path.join(data_dir, c.id, f"{date}.wav")) for c in available
    )
    path = os.path.join(data_dir, f"{date}.wav")
    tts.write_wav(path, pcm)
    return path
