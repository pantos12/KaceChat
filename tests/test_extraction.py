import pandas as pd

from data_pipeline.extractors.kace_connector import (
    filter_quality,
    filter_resolved,
    normalize_columns,
)


def test_filter_resolved():
    frame = pd.DataFrame(
        [
            {"status": "Resolved", "resolution": "ok"},
            {"status": "Open", "resolution": "ok"},
        ]
    )
    result = filter_resolved(frame, ["Resolved"])
    assert len(result) == 1


def test_filter_quality():
    frame = pd.DataFrame(
        [
            {"resolution": "short"},
            {"resolution": "long enough"},
        ]
    )
    result = filter_quality(frame, min_resolution_length=8)
    assert len(result) == 1


def test_normalize_columns():
    frame = pd.DataFrame(
        [{"id": "1", "title": "Issue", "status": "Resolved"}]
    )
    fields = {"ticket_id": "id", "title": "title", "status": "status"}
    normalized = normalize_columns(frame, fields)
    assert list(normalized.columns) == ["ticket_id", "title", "status"]
