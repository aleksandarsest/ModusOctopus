"""
OpenAI-compatible API provider.
"""

from __future__ import annotations

import importlib
import json
import re
from typing import Any, Dict, List, Optional

from ...config import Config
from ..capabilities import API_PROVIDER_CAPABILITIES, LLMCapabilities
from .base import BaseLLMProvider, LLMChatResult


class OpenAICompatibleProvider(BaseLLMProvider):
    provider_type = "openai_compatible"
    mode = "api"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model_name = model_name or Config.LLM_MODEL_NAME
        self._client = None

        if not self.api_key:
            raise ValueError("LLM_API_KEY is not configured")

    @property
    def capabilities(self) -> LLMCapabilities:
        return API_PROVIDER_CAPABILITIES

    def _get_client(self):
        if self._client is None:
            openai_module = importlib.import_module("openai")
            self._client = openai_module.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    def healthcheck(self) -> Dict[str, Any]:
        return {
            "ok": bool(self.api_key),
            "provider_type": self.provider_type,
            "mode": self.mode,
            "model_name": self.model_name,
            "base_url": self.base_url,
            "supports_pipeline": self.capabilities.supports_pipeline,
            "supports_refinement": self.capabilities.supports_refinement,
        }

    def chat_with_metadata(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMChatResult:
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = self._get_client().chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        return LLMChatResult(
            content=re.sub(r"<think>[\s\S]*?</think>", "", content).strip(),
            finish_reason=getattr(response.choices[0], "finish_reason", None),
        )

    def chat_json_with_metadata(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        result = self.chat_with_metadata(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return json.loads(result.content), result

    def refine_brief(self, brief_input: Any) -> Dict[str, Any]:
        prompt = self._brief_input_to_text(brief_input)
        messages = [
            {
                "role": "system",
                "content": "You refine MiroFish simulation briefs into concrete, stakeholder-aware business scenarios.",
            },
            {"role": "user", "content": prompt},
        ]
        return {
            "provider_type": self.provider_type,
            "mode": self.mode,
            "refined_brief": self.chat(messages, temperature=0.3, max_tokens=2048),
        }
