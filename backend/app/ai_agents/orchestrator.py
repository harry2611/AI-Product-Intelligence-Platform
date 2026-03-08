from app.ai_agents.feature_request_agent import FeatureRequestAgent
from app.ai_agents.insight_agent import InsightAgent
from app.ai_agents.llm_client import LLMClient
from app.ai_agents.sentiment_agent import SentimentAgent
from app.ai_agents.topic_extraction_agent import TopicExtractionAgent


class AgentOrchestrator:
    def __init__(self) -> None:
        llm_client = LLMClient()
        self.sentiment_agent = SentimentAgent(llm_client)
        self.topic_agent = TopicExtractionAgent(llm_client)
        self.feature_agent = FeatureRequestAgent(llm_client)
        self.insight_agent = InsightAgent(llm_client)

    def analyze_feedback(self, message: str) -> dict:
        sentiment = self.sentiment_agent.analyze(message)
        topics = self.topic_agent.analyze(message)
        feature_requests = self.feature_agent.analyze(message)

        insight = self.insight_agent.summarize_feedback(
            message=message,
            sentiment=sentiment.label,
            topics=[topic["topic"] for topic in topics],
            features=[feature["feature_name"] for feature in feature_requests],
        )

        return {
            "sentiment": {
                "label": sentiment.label,
                "score": sentiment.score,
                "rationale": sentiment.rationale,
            },
            "topics": topics,
            "feature_requests": feature_requests,
            "insight": insight,
        }
