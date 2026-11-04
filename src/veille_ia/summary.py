import json
import re

from veille_ia import llm
from veille_ia.fulltext import fetch_text

MAX_CANDIDATES = 10
ARTICLES_PER_TOPIC = 3
SNIPPET_CHARS = 300
TEXT_CHARS = 4000

SYSTEM = (
    "Tu es un journaliste spécialisé dans le domaine « {label} ». "
    "Tu réponds uniquement par un objet JSON, sans texte autour."
)

SELECT_PROMPT = """Tu prépares le bulletin quotidien de veille sur le domaine « {label} ».

Voici {count} sujets candidats. Choisis exactement {topic_count} sujets, les plus importants pour l'actualité de ce domaine, et classe-les du plus important au moins important.
- Un sujet repris par plusieurs sources compte plus.
- Évite les discussions, questions personnelles et offres d'emploi.
- Si plusieurs candidats traitent de la même affaire, fusionne-les : mets tous leurs numéros dans le même "ids".

Réponds avec ce JSON :
{{"topics": [{{"ids": [0]}}, {{"ids": [3, 5]}}]}}

Sujets candidats :
{topics}"""

WRITE_PROMPT = """Tu rédiges le bulletin quotidien de veille sur le domaine « {label} ». Il sera lu à voix haute.

Voici {count} sujets déjà choisis et classés, avec le texte de leurs articles. Pour chaque sujet, écris un texte en français, en prose, de 160 à 180 mots.
Règles :
- Appuie-toi uniquement sur les textes fournis. N'invente rien : si une information manque, reste prudent.
- Texte fait pour l'oral : phrases courtes, aucun lien, aucune mise en forme Markdown, aucune liste, aucune parenthèse.
- Le titre est court et en français.

Réponds avec ce JSON, un élément par sujet :
{{"topics": [{{"id": 0, "title": "titre court", "text": "texte à lire"}}]}}

Sujets :
{topics}"""


def is_discussion(topic):
    return all("[D]" in a.title for a in topic.articles)


def rank_key(topic, official_sources):
    return (
        not is_discussion(topic),
        len({a.source for a in topic.articles}),
        any(a.source in official_sources for a in topic.articles),
        sum(a.score for a in topic.articles),
        len(topic.articles),
    )


def select_candidates(topics, category):
    official = set(category.blog_feeds)
    return sorted(topics, key=lambda t: rank_key(t, official), reverse=True)[:MAX_CANDIDATES]


def describe(index, title, articles, chars):
    lines = [f"[{index}] {title}"]
    for article in articles[:ARTICLES_PER_TOPIC]:
        lines.append(f"- ({article.source}) {article.title} : {article.text[:chars]}".rstrip(" :"))
    return "\n".join(lines)


def build_select_prompt(candidates, category):
    blocks = [describe(i, t.title, t.articles, SNIPPET_CHARS) for i, t in enumerate(candidates)]
    return SELECT_PROMPT.format(
        label=category.label,
        count=len(candidates),
        topic_count=category.topic_count,
        topics="\n\n".join(blocks),
    )


def build_write_prompt(groups, category):
    blocks = [describe(i, articles[0].title, articles, TEXT_CHARS) for i, articles in enumerate(groups)]
    return WRITE_PROMPT.format(label=category.label, count=len(groups), topics="\n\n".join(blocks))


def parse_topics(content):
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    try:
        return json.loads(content)["topics"]
    except (ValueError, KeyError, TypeError) as error:
        raise llm.LLMError(f"Invalid summary response: {error}") from error


def clean_spoken(text):
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*#_`>\[\]]", "", text)
    return " ".join(text.split())


def choose(candidates, models, category):
    items = parse_topics(
        llm.complete(
            build_select_prompt(candidates, category),
            models,
            system=SYSTEM.format(label=category.label),
        )
    )
    chosen = []
    used = set()
    for item in items:
        ids = item.get("ids") if isinstance(item, dict) else None
        indexes = []
        for index in ids if isinstance(ids, list) else []:
            if isinstance(index, int) and 0 <= index < len(candidates):
                if index not in used and index not in indexes:
                    indexes.append(index)
        if indexes:
            used.update(indexes)
            chosen.append(indexes)
        if len(chosen) == category.topic_count:
            return chosen
    for index in range(len(candidates)):
        if len(chosen) == category.topic_count:
            break
        if index not in used:
            chosen.append([index])
    return chosen


def fetch_full_texts(articles):
    for article in articles:
        if "news.ycombinator.com/item" in article.url:
            continue
        text = fetch_text(article.url)
        if len(text) > len(article.text):
            article.text = text


def write(groups, models, category):
    items = parse_topics(
        llm.complete(
            build_write_prompt(groups, category),
            models,
            system=SYSTEM.format(label=category.label),
        )
    )
    written = {}
    for item in items:
        index = item.get("id") if isinstance(item, dict) else None
        if not isinstance(index, int) or not 0 <= index < len(groups) or index in written:
            continue
        text = clean_spoken(str(item.get("text", "")))
        if text:
            written[index] = (clean_spoken(str(item.get("title") or "")), text)
    result = []
    for index, articles in enumerate(groups):
        if index not in written:
            continue
        title, text = written[index]
        result.append(
            {
                "rank": len(result) + 1,
                "title": title or articles[0].title,
                "text": text,
                "sources": [{"name": a.source, "title": a.title, "url": a.url} for a in articles],
            }
        )
    if not result:
        raise llm.LLMError("Summary response contains no usable topic")
    return result


def summarize(candidates, category, select_models, write_models):
    if not candidates:
        return []
    groups = [
        [a for index in indexes for a in candidates[index].articles]
        for indexes in choose(candidates, select_models, category)
    ]
    fetch_full_texts([a for articles in groups for a in articles[:ARTICLES_PER_TOPIC]])
    return write(groups, write_models, category)
