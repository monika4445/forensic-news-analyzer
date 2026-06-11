from dataclasses import dataclass
from collections import defaultdict


@dataclass
class NewsItem:
    id: str
    title: str
    text: str
    company: str | None = None
    location: str | None = None
    industry: str | None = None


@dataclass
class NewsCluster:
    key: tuple
    company: str | None
    location: str | None
    industry: str | None
    items: list[NewsItem]


def cluster_news(news: list[NewsItem]) -> list[NewsCluster]:
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
