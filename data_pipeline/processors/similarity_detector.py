"""Detect similar ticket issues using TF-IDF cosine similarity."""

from __future__ import annotations

from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def cluster_by_similarity(texts: List[str], threshold: float = 0.75) -> list[list[int]]:
    if not texts:
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(texts)
    similarity = cosine_similarity(vectors)

    visited = set()
    clusters = []

    for idx in range(len(texts)):
        if idx in visited:
            continue
        cluster = [idx]
        visited.add(idx)
        for other in range(len(texts)):
            if other in visited:
                continue
            if similarity[idx, other] >= threshold:
                cluster.append(other)
                visited.add(other)
        clusters.append(cluster)

    return clusters
