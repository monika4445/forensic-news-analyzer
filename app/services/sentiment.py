from dataclasses import dataclass, field
from typing import List

POSITIVE_WORDS = [
    "рост", "прибыль", "успех", "развитие", "инвестиции", "выручка",
    "прибыльный", "расширение", "партнёрство", "сделка", "победа",
    "лидер", "рекорд", "улучшение", "повышение", "открытие", "запуск",
    "поддержка", "соглашение", "стабильность", "доход", "достижение",
]

NEGATIVE_WORDS = [
    "убыток", "банкротство", "штраф", "санкции", "скандал", "мошенничество",
    "задолженность", "иск", "арест", "обвинение", "потери", "кризис",
    "снижение", "падение", "ущерб", "нарушение", "уголовный", "коррупция",
    "дефолт", "отзыв", "ликвидация", "конфликт", "угроза", "риск",
]


@dataclass
class ScoredNews:
    id: str
    title: str
    text: str
    score: float = 0.0
    label: str = "neutral"


def score_text(text: str) -> float:
    words = text.lower().split()
    positive = sum(1 for w in words if any(p in w for p in POSITIVE_WORDS))
    negative = sum(1 for w in words if any(n in w for n in NEGATIVE_WORDS))
    total = positive + negative
    if total == 0:
        return 0.0
    return round((positive - negative) / total, 3)


def label_score(score: float) -> str:
    if score >= 0.5:
        return "positive"
    if score >= 0.1:
        return "slightly_positive"
    if score <= -0.5:
        return "negative"
    if score <= -0.1:
        return "slightly_negative"
    return "neutral"


def rank_news(news: List[dict]) -> List[ScoredNews]:
    scored = []
    for item in news:
        combined = f"{item.get('title', '')} {item.get('text', '')}"
        score = score_text(combined)
        scored.append(
            ScoredNews(
                id=item.get("id", ""),
                title=item.get("title", ""),
                text=item.get("text", ""),
                score=score,
                label=label_score(score),
            )
        )
    return sorted(scored, key=lambda x: x.score)


if __name__ == "__main__":
    sample = [
        {"id": "1", "title": "Сбербанк показал рекордную прибыль и рост выручки", "text": ""},
        {"id": "2", "title": "Компания получила штраф за нарушение и понесла убытки", "text": ""},
        {"id": "3", "title": "Лукойл открыл новое партнёрство и заключил сделку", "text": ""},
        {"id": "4", "title": "Против директора возбуждено уголовное дело о мошенничестве", "text": ""},
        {"id": "5", "title": "Компания провела пресс-конференцию", "text": ""},
    ]

    results = rank_news(sample)
    print(f"{'Score':>8}  {'Label':<20}  Title")
    print("-" * 70)
    for item in results:
        print(f"{item.score:>8.3f}  {item.label:<20}  {item.title[:50]}")
