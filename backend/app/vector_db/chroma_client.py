from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from app.core.config import settings


class ChromaStore:
    def __init__(self) -> None:
        self.client = self._create_client()
        self.collection = self._get_or_create_collection()

    @staticmethod
    def _create_client() -> chromadb.ClientAPI:
        if settings.chroma_host:
            return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
        return chromadb.PersistentClient(path=settings.chroma_persist_dir)

    def _get_or_create_collection(self) -> Collection:
        return self.client.get_or_create_collection(name=settings.chroma_collection_name, metadata={"hnsw:space": "cosine"})

    def upsert_feedback(self, feedback_id: int, message: str, embedding: list[float], metadata: dict[str, Any]) -> str:
        vector_id = f"feedback-{feedback_id}"
        payload = self._normalize_metadata({**metadata, "feedback_id": feedback_id})
        self.collection.upsert(
            ids=[vector_id],
            documents=[message],
            embeddings=[embedding],
            metadatas=[payload],
        )
        return vector_id

    def query(self, embedding: list[float], top_k: int = 8) -> dict[str, Any]:
        return self.collection.query(query_embeddings=[embedding], n_results=top_k)

    @staticmethod
    def _normalize_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
        """
        Chroma metadata only supports scalar values.
        Convert complex values (lists/dicts) to JSON strings.
        """
        normalized: dict[str, str | int | float | bool] = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                normalized[key] = value
            elif value is None:
                normalized[key] = ""
            else:
                normalized[key] = json.dumps(value, ensure_ascii=True)
        return normalized


@lru_cache(maxsize=1)
def get_chroma_store() -> ChromaStore:
    return ChromaStore()
