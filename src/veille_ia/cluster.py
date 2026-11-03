import json
import re

from veille_ia import llm
from veille_ia.models import Topic

SNIPPET_CHARS = 300

SYSTEM = (
    "Tu es un assistant de veille sur l'intelligence artificielle. "
    "Tu réponds uniquement par un objet JSON, sans texte autour."
)

PROMPT = """Voici des articles numérotés. Regroupe ceux qui parlent du même événement ou du même sujet précis.
Écarte (off_topic) ceux qui ne concernent pas l'intelligence artificielle.

Réponds avec ce JSON :
{{"topics": [{{"title": "titre court en français", "ids": [0, 3]}}], "off_topic": [5]}}

Chaque numéro apparaît au plus une fois.

Articles :
{articles}"""


def build_prompt(articles):
    lines = []
    for index, article in enumerate(articles):
        snippet = article.text[:SNIPPET_CHARS].replace("\n", " ")
        lines.append(f"[{index}] {article.title} ({article.source}) {snippet}".strip())
    return PROMPT.format(articles="\n".join(lines))


def parse_response(content):
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    try:
        data = json.loads(content)
        return data["topics"], data.get("off_topic", [])
    except (ValueError, KeyError, TypeError) as error:
        raise llm.LLMError(f"Invalid clustering response: {error}") from error


def cluster(articles, models):
    if not articles:
        return []
    topics_data, off_topic = parse_response(
        llm.complete(build_prompt(articles), models, system=SYSTEM)
    )
    used = {i for i in off_topic if isinstance(i, int)}
    topics = []
    for item in topics_data:
        ids = []
        for i in item.get("ids", []):
            if isinstance(i, int) and 0 <= i < len(articles) and i not in used:
                used.add(i)
                ids.append(i)
        if ids:
            topics.append(
                Topic(
                    title=item.get("title") or articles[ids[0]].title,
                    articles=[articles[i] for i in ids],
                )
            )
    for i, article in enumerate(articles):
        if i not in used:
            topics.append(Topic(title=article.title, articles=[article]))
    return topics
