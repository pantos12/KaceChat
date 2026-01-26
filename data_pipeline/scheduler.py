"""Run scheduled extraction and processing jobs."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from data_pipeline.extractors.kace_connector import run_extraction
from data_pipeline.processors.kb_generator import build_articles
from data_pipeline.processors.ticket_processor import load_config, process_tickets


logger = logging.getLogger(__name__)


def run_pipeline(kace_config: str, processor_config: str, output_dir: str) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    extracted = run_extraction(kace_config)
    processor_settings = load_config(processor_config)
    processed = process_tickets(extracted, processor_settings)
    processed_path = output_path / "processed.json"
    processed.to_json(processed_path, orient="records", indent=2)

    articles = build_articles(processed)
    articles_path = output_path / "articles.json"
    articles_path.write_text(
        json.dumps(articles, indent=2), encoding="utf-8"
    )

    logger.info("Wrote %s articles to %s", len(articles), articles_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run scheduled KB pipeline")
    parser.add_argument("--kace-config", default="config/kace_config.json")
    parser.add_argument("--processor-config", default="config/processor_config.json")
    parser.add_argument("--output-dir", default="knowledge_base")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    run_pipeline(args.kace_config, args.processor_config, args.output_dir)


if __name__ == "__main__":
    main()
