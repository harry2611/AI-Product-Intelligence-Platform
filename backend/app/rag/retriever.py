from app.services.embedding_service import get_embedding_service
from app.vector_db.chroma_client import get_chroma_store


class FeedbackRetriever:
    def __init__(self) -> None:
        self.embedding_service = get_embedding_service()
        self.vector_store = get_chroma_store()

    def retrieve(self, question: str, top_k: int = 8) -> list[dict]:
        query_embedding = self.embedding_service.embed_text(question)
        result = self.vector_store.query(query_embedding, top_k=top_k)

        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        entries: list[dict] = []
        for index, vector_id in enumerate(ids):
            metadata = metadatas[index] if index < len(metadatas) else {}
            entries.append(
                {
                    "vector_id": vector_id,
                    "message": docs[index] if index < len(docs) else "",
                    "metadata": metadata,
                    "score": 1 - float(distances[index]) if index < len(distances) else 0.0,
                }
            )
        return entries
