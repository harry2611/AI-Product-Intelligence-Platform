from collections import Counter

from app.ai_agents.llm_client import LLMClient
from app.rag.retriever import FeedbackRetriever


class ProductIntelligenceAssistant:
    def __init__(self) -> None:
        self.retriever = FeedbackRetriever()
        self.llm = LLMClient()

    def ask(self, question: str, top_k: int = 8) -> dict:
        matches = self.retriever.retrieve(question=question, top_k=top_k)

        if not matches:
            return {
                "answer": "No relevant feedback found for this question yet. Add more feedback entries and retry.",
                "citations": [],
            }

        context_lines = []
        for item in matches:
            source = item["metadata"].get("source", "unknown")
            context_lines.append(f"[{item['metadata'].get('feedback_id', 'n/a')}] ({source}) {item['message']}")

        fallback = self._fallback_answer(question, matches)

        answer = self.llm.generate_text(
            system_prompt=(
                "You are an AI product manager assistant. Use ONLY supplied context to answer. "
                "Give concise, actionable insights and include bullet points where useful."
            ),
            user_prompt=(
                f"Question: {question}\n\n"
                "Context feedback snippets:\n"
                + "\n".join(context_lines)
            ),
            fallback=fallback,
        )

        citations = [
            {
                "feedback_id": int(item["metadata"].get("feedback_id", -1)),
                "source": str(item["metadata"].get("source", "unknown")),
                "user_id": str(item["metadata"].get("user_id", "unknown")),
                "message": item["message"],
                "score": round(item["score"], 4),
            }
            for item in matches
        ]

        return {
            "answer": answer,
            "citations": citations,
        }

    @staticmethod
    def _fallback_answer(question: str, matches: list[dict]) -> str:
        lower_q = question.lower()

        topic_counter = Counter()
        feature_counter = Counter()
        negative_mentions = 0

        for item in matches:
            message = item["message"].lower()
            for topic in ["checkout", "performance", "login", "payments", "ux", "bug", "otp"]:
                if topic in message:
                    topic_counter[topic] += 1
            for feature in ["dark mode", "apple pay", "export", "notifications", "dashboard"]:
                if feature in message:
                    feature_counter[feature] += 1
            if any(token in message for token in ["slow", "error", "broken", "fail", "issue"]):
                negative_mentions += 1

        lines = ["AI summary based on semantically matched feedback:"]
        if "complaint" in lower_q or "negative" in lower_q:
            lines.append(f"- Negative/problem-oriented snippets in top matches: {negative_mentions}")
        if topic_counter:
            lines.append("- Most discussed issues: " + ", ".join(f"{k} ({v})" for k, v in topic_counter.most_common(3)))
        if feature_counter:
            lines.append(
                "- Most requested features in matched context: "
                + ", ".join(f"{k} ({v})" for k, v in feature_counter.most_common(3))
            )

        lines.append("- Recommended action: validate top issue with recent tickets and prioritize one fix + one feature experiment.")
        return "\n".join(lines)
