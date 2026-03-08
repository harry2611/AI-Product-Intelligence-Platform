import json
import logging
import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self._enabled = bool(settings.openai_api_key and settings.llm_provider.lower() == "openai")
        self._model = None
        if self._enabled:
            self._model = ChatOpenAI(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                temperature=0.1,
            )

    @property
    def enabled(self) -> bool:
        return self._enabled and self._model is not None

    def generate_json(self, system_prompt: str, user_prompt: str, default: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return default

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        )

        try:
            response = (prompt | self._model).invoke({})
            raw = response.content if isinstance(response.content, str) else str(response.content)
            return self._safe_parse_json(raw, default)
        except Exception as exc:  # pragma: no cover - network/provider issues
            logger.warning("LLM JSON generation failed, using fallback. Error: %s", exc)
            return default

    def generate_text(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if not self.enabled:
            return fallback

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        )

        try:
            response = (prompt | self._model).invoke({})
            content = response.content if isinstance(response.content, str) else str(response.content)
            content = content.strip()
            return content or fallback
        except Exception as exc:  # pragma: no cover - network/provider issues
            logger.warning("LLM text generation failed, using fallback. Error: %s", exc)
            return fallback

    @staticmethod
    def _safe_parse_json(raw: str, default: dict[str, Any]) -> dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                return default
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return default
