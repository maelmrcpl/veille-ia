import json
import re

from veille_ia import llm
from veille_ia.models import Topic

SNIPPET_CHARS = 300

SYSTEM = (
    "Tu es un assistant de veille sur le domaine « {label} ». "
    "Tu réponds uniquement par un objet JSON, sans texte autour."
)

PROMPT = """Voici des articles numérotés. Regroupe ceux qui traitent de la même affaire d'actualité : même annonce, même publication, même dossier, même si chaque article en donne un angle différent (chiffres, réactions, critiques). Exemple : tous les articles sur le dépôt du dossier d'introduction en bourse d'une même entreprise forment un seul groupe.
Ne regroupe pas des affaires différentes sous un thème large (« recherche en IA », « entreprises et IA ») : un article sans équivalent reste seul dans son propre sujet. En général la plupart des articles restent seuls et quelques groupes comptent 2 à 8 articles.
Écarte (off_topic) ceux qui ne relèvent pas du domaine « {label} », ainsi que les questions personnelles ou discussions sans information.

Réponds avec ce JSON :
{{"topics": [{{"title": "titre court en français", "ids": [0, 3]}}], "off_topic": [5]}}

Chaque numéro apparaît au plus une fois.

Articles :
{articles}"""


def build_prompt(articles, category):
    lines = []
    for index, article in enumerate(articles):
        snippet = article.text[:SNIPPET_CHARS].replace("\n", " ")
        lines.append(f"[{index}] {article.title} ({article.source}) {snippet}".strip())
    return PROMPT.format(label=category.label, articles="\n".join(lines))


def parse_response(content):
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    try:
        data = json.loads(content)
        return data["topics"], data.get("off_topic", [])
    except (ValueError, KeyError, TypeError) as error:
        raise llm.LLMError(f"Invalid clustering response: {error}") from error


def cluster(articles, models, category):
    if not articles:
        return []
    topics_data, off_topic = parse_response(
        llm.complete(
            build_prompt(articles, category),
            models,
            system=SYSTEM.format(label=category.label),
        )
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
