"""Export KB articles to Microsoft Dataverse (placeholder)."""

from __future__ import annotations

import argparse
import json
import os

import pandas as pd


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def export_to_dataverse(frame: pd.DataFrame, config: dict) -> None:
    tenant_id = os.environ.get(config["auth"]["tenant_id_env"], "")
    client_id = os.environ.get(config["auth"]["client_id_env"], "")
    client_secret = os.environ.get(config["auth"]["client_secret_env"], "")

    if not all([tenant_id, client_id, client_secret]):
        raise RuntimeError("Dataverse credentials are missing")

    print(
        f"Prepared {len(frame)} records for Dataverse table "
        f"{config['table_name']} in {config['environment_url']}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export KB to Dataverse")
    parser.add_argument("--input", required=True, help="Path to KB JSON")
    parser.add_argument(
        "--config",
        default="config/dataverse_config.json",
        help="Path to Dataverse config JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = pd.read_json(args.input)
    config = load_config(args.config)
    export_to_dataverse(frame, config)


if __name__ == "__main__":
    main()
