from dataclasses import dataclass

from app.ai_agents.llm_client import LLMClient


@dataclass
class SentimentOutput:
    label: str
    score: float
    rationale: str


class SentimentAgent:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def analyze(self, text: str) -> SentimentOutput:
        fallback = self._rule_based_sentiment(text)
        payload = self.llm_client.generate_json(
            system_prompt=(
                "You are a sentiment classifier for product feedback. "
                "Return JSON with keys: label, score, rationale. "
                "label must be one of Positive, Neutral, Negative. score is 0..1 confidence."
            ),
            user_prompt=f"Feedback:\n{text}",
            default={"label": fallback.label, "score": fallback.score, "rationale": fallback.rationale},
        )

        label = payload.get("label", fallback.label)
        score = payload.get("score", fallback.score)
        rationale = payload.get("rationale", fallback.rationale)

        if label not in {"Positive", "Neutral", "Negative"}:
            label = fallback.label

        try:
            score = float(score)
        except (TypeError, ValueError):
            score = fallback.score

        score = max(0.0, min(score, 1.0))
        return SentimentOutput(label=label, score=score, rationale=str(rationale))

    @staticmethod
    def _rule_based_sentiment(text: str) -> SentimentOutput:
        lower = text.lower()
        negative_hits = sum(
            keyword in lower
            for keyword in [
                "slow",
                "bug",
                "broken",
                "issue",
                "fail",
                "error",
                "crash",
                "bad",
                "worse",
                "problem",
            ]
        )
        positive_hits = sum(
            keyword in lower
            for keyword in ["love", "great", "good", "excellent", "smooth", "fast", "awesome", "helpful"]
        )

        if negative_hits > positive_hits:
            return SentimentOutput(label="Negative", score=min(0.95, 0.55 + negative_hits * 0.08), rationale="Keyword match")
        if positive_hits > negative_hits:
            return SentimentOutput(label="Positive", score=min(0.95, 0.55 + positive_hits * 0.08), rationale="Keyword match")
        return SentimentOutput(label="Neutral", score=0.5, rationale="No dominant sentiment signal")
