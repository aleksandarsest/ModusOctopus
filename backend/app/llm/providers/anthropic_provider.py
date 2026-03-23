"""
Anthropic API provider.
"""

from __future__ import annotations

import importlib
import json
from typing import Any, Dict, List, Optional

from ..capabilities import API_PROVIDER_CAPABILITIES, LLMCapabilities
from .base import BaseLLMProvider, LLMChatResult


class AnthropicProvider(BaseLLMProvider):
    provider_type = "anthropic"
    mode = "api"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self._client = None

        if not self.api_key:
            raise ValueError("Anthropic API key is required for provider type 'anthropic'")

    @property
    def capabilities(self) -> LLMCapabilities:
        return API_PROVIDER_CAPABILITIES

    def _get_client(self):
        if self._client is None:
            anthropic_module = importlib.import_module("anthropic")
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = anthropic_module.Anthropic(**kwargs)
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
        system_prompt = None
        converted_messages: List[Dict[str, str]] = []
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            if role == "system":
                system_prompt = content if system_prompt is None else f"{system_prompt}\n{content}"
            else:
                converted_messages.append({"role": role, "content": content})

        response = self._get_client().messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=converted_messages,
        )

        content_parts = []
        for block in response.content:
            text = getattr(block, "text", None)
            if text:
                content_parts.append(text)
        return LLMChatResult(
            content="\n".join(content_parts).strip(),
            finish_reason=getattr(response, "stop_reason", None),
        )

    def chat_json_with_metadata(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        json_messages = list(messages)
        if json_messages:
            last_message = dict(json_messages[-1])
            last_message["content"] = (
                f"{last_message.get('content', '')}\n\n"
                "Return only valid JSON. Do not wrap it in Markdown."
            ).strip()
            json_messages[-1] = last_message

        result = self.chat_with_metadata(
            messages=json_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        cleaned = result.content.strip()
        cleaned = cleaned.removeprefix("```json").strip()
        cleaned = cleaned.removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()
        return json.loads(cleaned), result

    def refine_brief(self, brief_input: Any) -> Dict[str, Any]:
        prompt = self._brief_input_to_text(brief_input)
        messages = [
            {
                "role": "system",
                "content": "You refine ModusOctopus simulation briefs into concrete, stakeholder-aware business scenarios.",
            },
            {"role": "user", "content": prompt},
        ]
        return {
            "provider_type": self.provider_type,
            "mode": self.mode,
            "refined_brief": self.chat(messages, temperature=0.3, max_tokens=2048),
        }
