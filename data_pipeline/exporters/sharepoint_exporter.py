"""Export KB articles to SharePoint-friendly payloads."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_payload(frame: pd.DataFrame, field_map: dict) -> list[dict]:
    payload: list[dict] = []
    for _, row in frame.iterrows():
        record = {}
        for key, sharepoint_field in field_map.items():
            record[sharepoint_field] = row.get(key)
        payload.append(record)
    return payload


def export_to_sharepoint(
    payload: list[dict], config: dict, output_path: Path
) -> None:
    """Write SharePoint payloads to disk for ingestion."""
    tenant_id = os.environ.get(config["auth"]["tenant_id_env"], "")
    client_id = os.environ.get(config["auth"]["client_id_env"], "")
    client_secret = os.environ.get(config["auth"]["client_secret_env"], "")

    if not all([tenant_id, client_id, client_secret]):
        logger.warning(
            "SharePoint credentials are missing; writing payload for manual upload."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    csv_path = output_path.with_suffix(".csv")
    pd.DataFrame(payload).to_csv(csv_path, index=False)

    logger.info(
        "Prepared %s records for SharePoint list %s at %s",
        len(payload),
        config["list_name"],
        config["site_url"],
    )
    logger.info("Wrote payload JSON to %s and CSV to %s", output_path, csv_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export KB to SharePoint")
    parser.add_argument("--input", required=True, help="Path to KB JSON")
    parser.add_argument(
        "--output",
        default="knowledge_base/sharepoint_payload.json",
        help="Path to write SharePoint payload JSON",
    )
    parser.add_argument(
        "--config",
        default="config/sharepoint_config.json",
        help="Path to SharePoint config JSON",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    frame = pd.read_json(args.input)
    config = load_config(args.config)
    payload = build_payload(frame, config["fields"])
    export_to_sharepoint(payload, config, Path(args.output))


if __name__ == "__main__":
    main()
