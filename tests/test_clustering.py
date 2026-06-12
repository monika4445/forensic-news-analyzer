import pytest
from app.services.clustering import NewsItem, cluster_news


def make_item(id, company=None, location=None, industry=None):
    return NewsItem(id=id, title="", text="", company=company, location=location, industry=industry)


def test_groups_by_all_attributes():
    news = [
        make_item("1", company="Сбербанк", location="Москва", industry="Финансы"),
        make_item("2", company="Сбербанк", location="Москва", industry="Финансы"),
        make_item("3", company="Лукойл", location="Москва", industry="Нефть"),
    ]
    clusters = cluster_news(news)
    assert len(clusters) == 2
    sber = next(c for c in clusters if c.company == "сбербанк")
    assert len(sber.items) == 2


def test_case_insensitive_grouping():
    news = [
        make_item("1", company="Сбербанк"),
        make_item("2", company="сбербанк"),
        make_item("3", company="СБЕРБАНК"),
    ]
    clusters = cluster_news(news)
    assert len(clusters) == 1
    assert len(clusters[0].items) == 3


def test_sorted_by_size_descending():
    news = [
        make_item("1", company="А"),
        make_item("2", company="Б"),
        make_item("3", company="Б"),
    ]
    clusters = cluster_news(news)
    assert len(clusters[0].items) >= len(clusters[1].items)


def test_empty_input():
    assert cluster_news([]) == []


def test_none_attributes_grouped_together():
    news = [make_item("1"), make_item("2")]
    clusters = cluster_news(news)
    assert len(clusters) == 1
    assert len(clusters[0].items) == 2
