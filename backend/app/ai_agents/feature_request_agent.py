import re

from app.ai_agents.llm_client import LLMClient


class FeatureRequestAgent:
    REQUEST_PATTERNS = [
        r"\bplease add\b",
        r"\bwould like\b",
        r"\bfeature request\b",
        r"\bcan you add\b",
        r"\bit would be great if\b",
        r"\bneed\b",
    ]

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def analyze(self, text: str) -> list[dict[str, str]]:
        fallback = self._rule_based_feature_detection(text)
        payload = self.llm_client.generate_json(
            system_prompt=(
                "Find feature requests in product feedback. Return JSON with key 'feature_requests' "
                "as a list of objects with keys: feature_name, normalized_key, request_text. "
                "If none exist return empty list."
            ),
            user_prompt=f"Feedback:\n{text}",
            default={"feature_requests": fallback},
        )

        extracted = payload.get("feature_requests", fallback)
        if not isinstance(extracted, list):
            return fallback

        normalized: list[dict[str, str]] = []
        for item in extracted:
            if not isinstance(item, dict):
                continue
            feature_name = str(item.get("feature_name", "")).strip()
            request_text = str(item.get("request_text", "")).strip() or text
            normalized_key = str(item.get("normalized_key", "")).strip() or self._normalize_key(feature_name)
            if feature_name:
                normalized.append(
                    {
                        "feature_name": feature_name,
                        "normalized_key": normalized_key,
                        "request_text": request_text,
                    }
                )
        return normalized

    def _rule_based_feature_detection(self, text: str) -> list[dict[str, str]]:
        lower = text.lower()
        is_request = any(re.search(pattern, lower) for pattern in self.REQUEST_PATTERNS)
        if not is_request:
            return []

        candidates = []
        for feature in ["dark mode", "apple pay", "export csv", "multi-language", "offline mode", "custom dashboard"]:
            if feature in lower:
                candidates.append(feature)

        if not candidates:
            candidates = ["general improvement request"]

        return [
            {
                "feature_name": candidate.title(),
                "normalized_key": self._normalize_key(candidate),
                "request_text": text,
            }
            for candidate in candidates
        ]

    @staticmethod
    def _normalize_key(value: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
        return cleaned or "feature_request"
