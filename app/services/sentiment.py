from dataclasses import dataclass

POSITIVE_WEIGHTS: dict[str, float] = {
    "рост": 1.0, "прибыль": 1.5, "успех": 1.0, "развитие": 1.0,
    "инвестиции": 1.0, "выручка": 1.0, "расширение": 1.0,
    "партнёрство": 1.0, "сделка": 1.0, "победа": 1.5,
    "лидер": 1.0, "рекорд": 2.0, "улучшение": 1.0, "повышение": 1.0,
    "открытие": 1.0, "запуск": 1.0, "соглашение": 1.0,
    "стабильность": 1.0, "доход": 1.0, "достижение": 1.5,
}

NEGATIVE_WEIGHTS: dict[str, float] = {
    "убыток": 1.5, "банкротство": 3.0, "штраф": 2.0, "санкции": 2.0,
    "скандал": 1.5, "мошенничество": 2.5, "задолженность": 1.5,
    "иск": 1.5, "арест": 2.0, "обвинение": 2.0, "потери": 1.5,
    "кризис": 2.0, "снижение": 1.0, "падение": 1.5, "ущерб": 1.5,
    "нарушение": 1.5, "уголовный": 2.5, "коррупция": 2.5,
    "дефолт": 3.0, "ликвидация": 2.0, "конфликт": 1.5, "угроза": 1.5,
}

NEGATIONS = {"не", "нет", "без", "никакого", "никакой", "никаких"}


@dataclass
class ScoredNews:
    id: str
    title: str
    text: str
    score: float = 0.0
    label: str = "neutral"


def _score_tokens(tokens: list[str]) -> float:
    positive_score = 0.0
    negative_score = 0.0

    for i, token in enumerate(tokens):
        is_negated = any(tokens[j] in NEGATIONS for j in range(max(0, i - 2), i))

        for keyword, weight in POSITIVE_WEIGHTS.items():
            if keyword in token:
                if is_negated:
                    negative_score += weight
                else:
                    positive_score += weight

        for keyword, weight in NEGATIVE_WEIGHTS.items():
            if keyword in token:
                if is_negated:
                    positive_score += weight * 0.5
                else:
                    negative_score += weight

    total = positive_score + negative_score
    if total == 0:
        return 0.0
    return round((positive_score - negative_score) / total, 3)


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


def score_text(text: str) -> float:
    tokens = text.lower().split()
    return _score_tokens(tokens)


def rank_news(news: list[dict]) -> list[ScoredNews]:
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
        {"id": "6", "title": "Компания не получила убытков в этом квартале", "text": ""},
    ]

    results = rank_news(sample)
    print(f"{'Score':>8}  {'Label':<20}  Title")
    print("-" * 70)
    for item in results:
        print(f"{item.score:>8.3f}  {item.label:<20}  {item.title[:50]}")
