"""Analyze tickets for categories and resolution quality."""

from __future__ import annotations

import json
from dataclasses import dataclass

import pandas as pd


@dataclass
class CategoryConfig:
    category_keywords: dict[str, list[str]]


def load_categories(path: str) -> CategoryConfig:
    with open(path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return CategoryConfig(category_keywords=raw)


def infer_category(text: str, config: CategoryConfig) -> str:
    lowered = text.lower()
    for category, keywords in config.category_keywords.items():
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return "general"


def apply_categories(frame: pd.DataFrame, config: CategoryConfig) -> pd.DataFrame:
    combined = (
        frame["title"].fillna("") + " " + frame["description"].fillna("")
    )
    frame = frame.copy()
    frame["category"] = combined.apply(lambda text: infer_category(text, config))
    return frame


def score_resolution_quality(resolution: str) -> float:
    length_score = min(len(resolution) / 400, 1.0)
    return round(length_score, 2)


def add_resolution_quality(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["resolution_quality"] = frame["resolution"].fillna("").apply(
        score_resolution_quality
    )
    return frame
