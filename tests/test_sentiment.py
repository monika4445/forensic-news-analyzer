import pytest
from app.services.sentiment import score_text, label_score, rank_news


def test_positive_news_scores_positive():
    score = score_text("Сбербанк показал рекордную прибыль и рост выручки")
    assert score > 0


def test_negative_news_scores_negative():
    score = score_text("Компания получила штраф за нарушение и понесла убытки")
    assert score < 0


def test_neutral_news_scores_zero():
    score = score_text("Компания провела пресс-конференцию")
    assert score == 0.0


def test_negation_flips_negative_word():
    score_with_negation = score_text("Компания не получила убыток")
    score_without_negation = score_text("Компания получила убыток")
    assert score_with_negation > score_without_negation


def test_bankruptcy_weighted_higher_than_single_loss():
    score_bankruptcy = score_text("банкротство снижение убыток")
    score_loss = score_text("снижение убыток")
    assert score_bankruptcy <= score_loss


def test_label_positive():
    assert label_score(0.8) == "positive"
    assert label_score(0.2) == "slightly_positive"


def test_label_negative():
    assert label_score(-0.8) == "negative"
    assert label_score(-0.2) == "slightly_negative"


def test_label_neutral():
    assert label_score(0.0) == "neutral"


def test_rank_news_sorted_ascending():
    news = [
        {"id": "1", "title": "рекордная прибыль", "text": ""},
        {"id": "2", "title": "банкротство штраф", "text": ""},
        {"id": "3", "title": "пресс-конференция", "text": ""},
    ]
    ranked = rank_news(news)
    scores = [r.score for r in ranked]
    assert scores == sorted(scores)


def test_rank_news_empty():
    assert rank_news([]) == []
