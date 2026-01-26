"""Extraction utilities for KACE Quest ticket data."""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from data_pipeline.extractors.file_parser import parse_csv


logger = logging.getLogger(__name__)


@dataclass
class KaceConfig:
    source: str
    api_base_url: str
    api_token_env: str
    api_timeout_seconds: int
    file_path: str
    file_delimiter: str
    file_encoding: str
    fields: dict[str, str]
    resolved_status_values: list[str]
    min_resolution_length: int


def load_config(path: str) -> KaceConfig:
    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

    api = raw.get("api", {})
    file_export = raw.get("file_export", {})

    return KaceConfig(
        source=raw.get("source", "csv"),
        api_base_url=api.get("base_url", ""),
        api_token_env=api.get("token_env", "KACE_API_TOKEN"),
        api_timeout_seconds=int(api.get("timeout_seconds", 30)),
        file_path=file_export.get("path", ""),
        file_delimiter=file_export.get("delimiter", ","),
        file_encoding=file_export.get("encoding", "utf-8"),
        fields=raw.get("fields", {}),
        resolved_status_values=raw.get("resolved_status_values", ["Resolved", "Closed"]),
        min_resolution_length=int(raw.get("min_resolution_length", 40)),
    )


def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def extract_from_csv(path: str, delimiter: str, encoding: str) -> pd.DataFrame:
    logger.info("Parsing CSV export at %s", path)
    return parse_csv(path, delimiter=delimiter, encoding=encoding)


def extract_from_api(base_url: str, token: str, timeout_seconds: int) -> pd.DataFrame:
    """Placeholder for KACE API extraction logic."""
    session = build_session()
    headers = {"Authorization": f"Bearer {token}"}
    response = session.get(
        f"{base_url}/tickets", headers=headers, timeout=timeout_seconds
    )
    response.raise_for_status()
    payload = response.json()
    return pd.DataFrame(payload.get("data", []))


def normalize_columns(frame: pd.DataFrame, fields: dict[str, str]) -> pd.DataFrame:
    rename_map = {value: key for key, value in fields.items()}
    normalized = frame.rename(columns=rename_map)
    missing = set(fields.keys()) - set(normalized.columns)
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")
    return normalized[list(fields.keys())]


def filter_resolved(frame: pd.DataFrame, resolved_status_values: Iterable[str]) -> pd.DataFrame:
    return frame[frame["status"].isin(resolved_status_values)].copy()


def filter_quality(frame: pd.DataFrame, min_resolution_length: int) -> pd.DataFrame:
    resolution_lengths = frame["resolution"].fillna("").str.len()
    return frame[resolution_lengths >= min_resolution_length].copy()


def run_extraction(config_path: str) -> pd.DataFrame:
    config = load_config(config_path)

    if config.source == "api":
        token = os.environ.get(config.api_token_env, "")
        if not token:
            raise RuntimeError("KACE API token is missing")
        extracted = extract_from_api(
            config.api_base_url, token, config.api_timeout_seconds
        )
    else:
        extracted = extract_from_csv(
            config.file_path, config.file_delimiter, config.file_encoding
        )

    normalized = normalize_columns(extracted, config.fields)
    resolved = filter_resolved(normalized, config.resolved_status_values)
    return filter_quality(resolved, config.min_resolution_length)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract KACE tickets")
    parser.add_argument(
        "--config",
        default="config/kace_config.json",
        help="Path to KACE config JSON",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()
    tickets = run_extraction(args.config)
    logger.info("Extracted %s tickets", len(tickets))
    print(tickets.head().to_string(index=False))


if __name__ == "__main__":
    main()
