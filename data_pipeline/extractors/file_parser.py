"""Parse KACE ticket exports."""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {
    "ticket_id",
    "title",
    "description",
    "resolution",
    "status",
    "created_date",
    "resolved_date",
    "category",
}


def parse_csv(path: str, delimiter: str = ",", encoding: str = "utf-8") -> pd.DataFrame:
    frame = pd.read_csv(path, delimiter=delimiter, encoding=encoding)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return frame
