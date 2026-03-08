from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self.model_name = settings.embedding_model_name
        self._model: SentenceTransformer | None = None
        self._fallback = False
        try:
            self._model = SentenceTransformer(self.model_name)
        except Exception as exc:  # pragma: no cover - model download/runtime issue
            logger.warning("Embedding model unavailable, using deterministic fallback embeddings. Error: %s", exc)
            self._fallback = True

    def embed_text(self, text: str) -> list[float]:
        if self._fallback or self._model is None:
            return self._fallback_embedding(text)

        vector = self._model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def _fallback_embedding(self, text: str) -> list[float]:
        dimensions = 384
        vector = np.zeros(dimensions, dtype=np.float32)
        for token in text.lower().split():
            index = hash(token) % dimensions
            vector[index] += 1.0

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.tolist()


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
