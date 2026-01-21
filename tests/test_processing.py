import pandas as pd

from data_pipeline.processors.ticket_processor import ProcessConfig, process_tickets


def test_process_filters_short_resolution(tmp_path):
    frame = pd.DataFrame(
        [
            {
                "ticket_id": "1",
                "title": "Test",
                "description": "desc",
                "resolution": "short",
                "status": "Resolved",
                "created_date": "2024-01-01",
                "resolved_date": "2024-01-02",
                "category": "software",
            }
        ]
    )
    categories_path = tmp_path / "categories.json"
    categories_path.write_text("{}")
    config = ProcessConfig(
        min_resolution_length=10,
        max_title_length=140,
        categories_path=str(categories_path),
    )
    processed = process_tickets(frame, config)
    assert processed.empty


def test_process_adds_confidence_score(tmp_path):
    frame = pd.DataFrame(
        [
            {
                "ticket_id": "2",
                "title": "Long title",
                "description": "desc",
                "resolution": "This is a sufficiently long resolution text.",
                "status": "Resolved",
                "created_date": "2024-01-01",
                "resolved_date": "2024-01-02",
                "category": "software",
            }
        ]
    )
    categories_path = tmp_path / "categories.json"
    categories_path.write_text("{\"software\": [\"desc\"]}")
    config = ProcessConfig(
        min_resolution_length=10,
        max_title_length=140,
        categories_path=str(categories_path),
    )
    processed = process_tickets(frame, config)
    assert "confidence_score" in processed.columns
    assert processed.iloc[0]["confidence_score"] >= 0.5
    assert processed.iloc[0]["category"] == "software"
