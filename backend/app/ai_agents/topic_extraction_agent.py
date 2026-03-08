from collections import defaultdict

from app.ai_agents.llm_client import LLMClient


TOPIC_KEYWORDS: dict[str, list[str]] = {
    "Performance": ["slow", "latency", "performance", "loading", "lag", "timeout"],
    "UX": ["ui", "ux", "design", "navigation", "layout", "experience"],
    "Payments": ["payment", "checkout", "card", "billing", "invoice", "refund"],
    "Login": ["login", "otp", "password", "authentication", "sign in", "2fa"],
    "Feature Request": ["feature", "add", "would like", "please include", "can you", "request"],
    "Bugs": ["bug", "error", "crash", "broken", "issue", "failed"],
}


class TopicExtractionAgent:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def analyze(self, text: str) -> list[dict[str, float]]:
        fallback_topics = self._rule_based_topics(text)
        payload = self.llm_client.generate_json(
            system_prompt=(
                "Extract product-feedback topics. Return JSON with key 'topics' where value is "
                "a list of objects: {{topic: <one of Performance, UX, Payments, Login, Feature Request, Bugs>, confidence: <0..1>}}"
            ),
            user_prompt=f"Feedback:\n{text}",
            default={"topics": fallback_topics},
        )
        topics = payload.get("topics", fallback_topics)
        cleaned: list[dict[str, float]] = []

        if isinstance(topics, list):
            for item in topics:
                if not isinstance(item, dict):
                    continue
                topic = item.get("topic")
                confidence = item.get("confidence", 0.5)
                if topic not in TOPIC_KEYWORDS:
                    continue
                try:
                    confidence = float(confidence)
                except (TypeError, ValueError):
                    confidence = 0.5
                cleaned.append({"topic": topic, "confidence": max(0.0, min(confidence, 1.0))})

        return cleaned or fallback_topics

    @staticmethod
    def _rule_based_topics(text: str) -> list[dict[str, float]]:
        lower = text.lower()
        scores: defaultdict[str, float] = defaultdict(float)
        for topic, keywords in TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lower:
                    scores[topic] += 1

        if not scores:
            return [{"topic": "UX", "confidence": 0.35}]

        max_score = max(scores.values())
        return [
            {"topic": topic, "confidence": round(score / max_score, 2)}
            for topic, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
        ]
