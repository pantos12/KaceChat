"""Generate KB articles from processed tickets."""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from data_pipeline.processors.similarity_detector import cluster_by_similarity


def extract_keywords(texts: list[str], max_features: int = 5) -> list[list[str]]:
    if not texts:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", max_features=max_features)
    vectors = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    keywords = []
    for row in vectors.toarray():
        ranked = sorted(
            zip(feature_names, row), key=lambda pair: pair[1], reverse=True
        )
        keywords.append([word for word, score in ranked if score > 0])
    return keywords


def build_article_from_cluster(
    frame: pd.DataFrame, cluster: list[int], keywords: list[list[str]]
) -> dict:
    cluster_frame = frame.iloc[cluster]
    first = cluster_frame.iloc[0]
    longest_resolution = cluster_frame.loc[
        cluster_frame["resolution"].str.len().idxmax()
    ]["resolution"]
    now = datetime.now(timezone.utc).isoformat()

    combined_keywords = []
    for idx in cluster:
        combined_keywords.extend(keywords[idx])

    confidence = float(cluster_frame["confidence_score"].mean())
    confidence = round(min(1.0, confidence + min(len(cluster) / 10, 0.3)), 2)

    return {
        "article_id": f"kb-{uuid.uuid4().hex[:8]}",
        "title": first.get("title", "").strip(),
        "category": first.get("category", "general"),
        "symptoms": cluster_frame["description"].fillna("").tolist(),
        "resolution": longest_resolution.strip(),
        "related_tickets": cluster_frame["ticket_id"].astype(str).tolist(),
        "confidence_score": confidence,
        "last_updated": now,
        "keywords": sorted(set(combined_keywords)),
    }


def build_articles(frame: pd.DataFrame) -> list[dict]:
    descriptions = frame["description"].fillna("").tolist()
    resolutions = frame["resolution"].fillna("").tolist()
    combined_texts = [
        f"{desc} {res}".strip() for desc, res in zip(descriptions, resolutions)
    ]
    keywords = extract_keywords(combined_texts)

    clusters = cluster_by_similarity(combined_texts)
    articles = [
        build_article_from_cluster(frame, cluster, keywords) for cluster in clusters
    ]
    return articles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate KB articles")
    parser.add_argument("--input", required=True, help="Path to processed JSON")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = pd.read_json(args.input)
    articles = build_articles(frame)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(articles, handle, indent=2)


if __name__ == "__main__":
    main()
