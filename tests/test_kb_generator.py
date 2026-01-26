import pandas as pd

from data_pipeline.processors.kb_generator import build_articles


def test_build_articles_clusters_similar():
    frame = pd.DataFrame(
        [
            {
                "ticket_id": "1",
                "title": "VPN issue",
                "description": "VPN drops",
                "resolution": "Reinstall VPN client",
                "category": "network",
                "confidence_score": 0.6,
            },
            {
                "ticket_id": "2",
                "title": "VPN issue",
                "description": "VPN disconnects",
                "resolution": "Reinstall VPN client",
                "category": "network",
                "confidence_score": 0.7,
            },
        ]
    )
    articles = build_articles(frame)
    assert len(articles) == 1
    assert set(articles[0]["related_tickets"]) == {"1", "2"}
