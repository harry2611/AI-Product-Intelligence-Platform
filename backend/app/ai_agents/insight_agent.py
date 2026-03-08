from collections import Counter

from app.ai_agents.llm_client import LLMClient


class InsightAgent:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def summarize_feedback(self, message: str, sentiment: str, topics: list[str], features: list[str]) -> str:
        fallback = self._fallback_insight(message=message, sentiment=sentiment, topics=topics, features=features)
        payload = self.llm_client.generate_text(
            system_prompt=(
                "You are a product analyst. Create one concise actionable insight from one feedback message. "
                "Focus on product impact and use <= 35 words."
            ),
            user_prompt=(
                f"Feedback: {message}\n"
                f"Sentiment: {sentiment}\n"
                f"Topics: {topics}\n"
                f"Feature requests: {features}\n"
            ),
            fallback=fallback,
        )
        return payload

    def generate_global_insights(
        self,
        top_negative_topics: list[tuple[str, int]],
        top_feature_requests: list[tuple[str, int]],
    ) -> list[str]:
        if not top_negative_topics and not top_feature_requests:
            return ["No clear trend detected yet. More data is needed for strong recommendations."]

        recommendations: list[str] = []
        if top_negative_topics:
            topic, count = top_negative_topics[0]
            recommendations.append(f"Primary pain-point is {topic.lower()} ({count} mentions). Prioritize a cross-team fix sprint.")
        if top_feature_requests:
            feature, count = top_feature_requests[0]
            recommendations.append(f"Most requested feature is {feature} ({count} requests). Consider roadmap validation with user cohort interviews.")

        recommendations.extend(
            [
                "Set weekly KPI guardrails for negative feedback share and escalate anomalies.",
                "Create an owner + ETA for top two complaints to close the feedback loop.",
            ]
        )
        return recommendations[:4]

    @staticmethod
    def _fallback_insight(message: str, sentiment: str, topics: list[str], features: list[str]) -> str:
        topic = topics[0] if topics else "general UX"
        if features:
            return f"Users are asking for {features[0]} while discussing {topic.lower()}; evaluate scope for upcoming release planning."
        if sentiment == "Negative":
            return f"Negative signal linked to {topic.lower()} indicates a friction point impacting user experience."
        return f"Feedback indicates stable sentiment with emphasis on {topic.lower()}; monitor trend before prioritization changes."


def normalize_feature_counter(items: list[str]) -> list[tuple[str, int]]:
    return Counter(items).most_common(10)
