"""Process resolved KACE tickets into KB-ready records."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd

from data_pipeline.processors.ticket_analyzer import (
    add_resolution_quality,
    apply_categories,
    load_categories,
)


logger = logging.getLogger(__name__)


@dataclass
class ProcessConfig:
    min_resolution_length: int
    max_title_length: int
    categories_path: str


def load_config(path: str) -> ProcessConfig:
    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return ProcessConfig(
        min_resolution_length=int(raw.get("min_resolution_length", 40)),
        max_title_length=int(raw.get("max_title_length", 140)),
        categories_path=raw.get("categories_path", "config/categories.json"),
    )


def normalize_title(title: str, max_length: int) -> str:
    normalized = " ".join(title.split())
    return normalized[:max_length]


def calculate_confidence(resolution_quality: float, similar_count: int) -> float:
    similarity_boost = min(similar_count / 10, 0.5)
    return round(min(0.5 + resolution_quality * 0.4 + similarity_boost, 1.0), 2)


def process_tickets(frame: pd.DataFrame, config: ProcessConfig) -> pd.DataFrame:
    processed = frame.copy()
    processed["title"] = processed["title"].fillna("").apply(
        lambda value: normalize_title(value, config.max_title_length)
    )
    processed["resolution"] = processed["resolution"].fillna("")

    categories = load_categories(config.categories_path)
    processed = apply_categories(processed, categories)
    processed = add_resolution_quality(processed)

    processed["last_updated"] = datetime.now(timezone.utc).isoformat()
    processed = processed[processed["resolution"].str.len() >= config.min_resolution_length]

    processed["confidence_score"] = processed["resolution_quality"].apply(
        lambda score: calculate_confidence(score, similar_count=1)
    )
    return processed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process KACE tickets")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    parser.add_argument(
        "--config",
        default="config/processor_config.json",
        help="Path to processor config JSON",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    frame = pd.read_csv(args.input)
    config = load_config(args.config)
    processed = process_tickets(frame, config)
    logger.info("Processed %s tickets", len(processed))
    processed.to_json(args.output, orient="records", indent=2)


if __name__ == "__main__":
    main()
