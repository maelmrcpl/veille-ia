from dataclasses import dataclass


@dataclass
class Article:
    title: str
    url: str
    source: str
    published: int
    score: int = 0
    text: str = ""


@dataclass
class Topic:
    title: str
    articles: list[Article]
