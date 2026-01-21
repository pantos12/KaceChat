"""Export KB articles to SharePoint (placeholder)."""

from __future__ import annotations

import argparse
import json
import os

import pandas as pd


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_payload(frame: pd.DataFrame, field_map: dict) -> list[dict]:
    payload = []
    for _, row in frame.iterrows():
        record = {}
        for key, sharepoint_field in field_map.items():
            record[sharepoint_field] = row.get(key)
        payload.append(record)
    return payload


def export_to_sharepoint(payload: list[dict], config: dict) -> None:
    """Placeholder for SharePoint upload logic."""
    tenant_id = os.environ.get(config["auth"]["tenant_id_env"], "")
    client_id = os.environ.get(config["auth"]["client_id_env"], "")
    client_secret = os.environ.get(config["auth"]["client_secret_env"], "")

    if not all([tenant_id, client_id, client_secret]):
        raise RuntimeError("SharePoint credentials are missing")

    print(
        f"Prepared {len(payload)} records for SharePoint list "
        f"{config['list_name']} at {config['site_url']}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export KB to SharePoint")
    parser.add_argument("--input", required=True, help="Path to KB JSON")
    parser.add_argument(
        "--config",
        default="config/sharepoint_config.json",
        help="Path to SharePoint config JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = pd.read_json(args.input)
    config = load_config(args.config)
    payload = build_payload(frame, config["fields"])
    export_to_sharepoint(payload, config)


if __name__ == "__main__":
    main()
