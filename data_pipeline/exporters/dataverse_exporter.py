"""Export KB articles to Microsoft Dataverse payloads."""

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


def export_to_dataverse(frame: pd.DataFrame, config: dict, output_path: Path) -> None:
    tenant_id = os.environ.get(config["auth"]["tenant_id_env"], "")
    client_id = os.environ.get(config["auth"]["client_id_env"], "")
    client_secret = os.environ.get(config["auth"]["client_secret_env"], "")

    if not all([tenant_id, client_id, client_secret]):
        logger.warning(
            "Dataverse credentials are missing; writing payload for manual upload."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_json(output_path, orient="records", indent=2)

    logger.info(
        "Prepared %s records for Dataverse table %s in %s",
        len(frame),
        config["table_name"],
        config["environment_url"],
    )
    logger.info("Wrote payload JSON to %s", output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export KB to Dataverse")
    parser.add_argument("--input", required=True, help="Path to KB JSON")
    parser.add_argument(
        "--output",
        default="knowledge_base/dataverse_payload.json",
        help="Path to write Dataverse payload JSON",
    )
    parser.add_argument(
        "--config",
        default="config/dataverse_config.json",
        help="Path to Dataverse config JSON",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    frame = pd.read_json(args.input)
    config = load_config(args.config)
    export_to_dataverse(frame, config, Path(args.output))


if __name__ == "__main__":
    main()
