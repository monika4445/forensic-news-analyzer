from dataclasses import dataclass
from typing import List, Optional
from collections import defaultdict


@dataclass
class NewsItem:
    id: str
    title: str
    text: str
    company: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None


@dataclass
class NewsCluster:
    key: tuple
    company: Optional[str]
    location: Optional[str]
    industry: Optional[str]
    items: List[NewsItem]


def cluster_news(news: List[NewsItem]) -> List[NewsCluster]:
    groups: dict[tuple, List[NewsItem]] = defaultdict(list)

    for item in news:
        key = (
            (item.company or "").lower().strip(),
            (item.location or "").lower().strip(),
            (item.industry or "").lower().strip(),
        )
        groups[key].append(item)

    clusters = []
    for key, items in groups.items():
        company, location, industry = key
        clusters.append(
            NewsCluster(
                key=key,
                company=company or None,
                location=location or None,
                industry=industry or None,
                items=items,
            )
        )

    clusters.sort(key=lambda c: len(c.items), reverse=True)
    return clusters


if __name__ == "__main__":
    sample = [
        NewsItem("1", "Сбербанк открыл офис", "", company="Сбербанк", location="Москва", industry="Финансы"),
        NewsItem("2", "Сбербанк запустил продукт", "", company="Сбербанк", location="Москва", industry="Финансы"),
        NewsItem("3", "Лукойл отчитался", "", company="Лукойл", location="Москва", industry="Нефть"),
        NewsItem("4", "Газпром в Сибири", "", company="Газпром", location="Сибирь", industry="Газ"),
        NewsItem("5", "Сбербанк в СПб", "", company="Сбербанк", location="Санкт-Петербург", industry="Финансы"),
    ]

    result = cluster_news(sample)
    for cluster in result:
        print(f"[{cluster.company} / {cluster.location} / {cluster.industry}] — {len(cluster.items)} news")
