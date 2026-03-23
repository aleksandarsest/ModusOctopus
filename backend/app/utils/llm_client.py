"""
LLM client wrapper.
Routes requests through the project-level provider factory while keeping the
legacy constructor compatible with OpenAI-compatible defaults.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from ..config import Config
from ..llm.factory import LLMProviderFactory
from ..llm.providers.base import BaseLLMProvider, LLMChatResult


class LLMClient:
    """Thin wrapper around a provider-backed LLM implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        *,
        provider: Optional[BaseLLMProvider] = None,
        provider_config: Optional[Dict[str, Any]] = None,
    ):
        if provider is not None:
            self.provider = provider
        else:
            resolved_config = dict(provider_config or {})
            use_default_api_key = not resolved_config

            if any(value is not None for value in (api_key, base_url, model)):
                resolved_config.setdefault("provider_type", "openai_compatible")
                if api_key is not None:
                    resolved_config.setdefault("api_key", api_key)
                if base_url is not None:
                    resolved_config.setdefault("base_url", base_url)
                if model is not None:
                    resolved_config.setdefault("model_name", model)
                use_default_api_key = True

            self.provider = LLMProviderFactory.create(
                resolved_config,
                default_api_key=Config.LLM_API_KEY if use_default_api_key else None,
            )

        self.provider_type = getattr(self.provider, "provider_type", "unknown")
        self.mode = getattr(self.provider, "mode", "api")
        self.capabilities = getattr(self.provider, "capabilities", None)
        self.api_key = getattr(self.provider, "api_key", None)
        self.base_url = getattr(self.provider, "base_url", None)
        self.model_name = getattr(self.provider, "model_name", None)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Send a chat completion request via the configured provider."""
        return self.provider.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    def chat_with_metadata(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMChatResult:
        """Send a chat request and return normalized response metadata."""
        return self.provider.chat_with_metadata(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Send a JSON-oriented chat request and parse the result."""
        if self.capabilities is not None and not self.capabilities.supports_chat_json:
            raise ValueError(
                f"Provider '{self.provider_type}' does not support JSON chat responses"
            )

        response, _ = self.provider.chat_json_with_metadata(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response

    def chat_json_with_metadata(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> tuple[Dict[str, Any], LLMChatResult]:
        """Send a JSON-oriented request and return parsed JSON plus metadata."""
        if self.capabilities is not None and not self.capabilities.supports_chat_json:
            raise ValueError(
                f"Provider '{self.provider_type}' does not support JSON chat responses"
            )

        response, result = self.provider.chat_json_with_metadata(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response, result

    @staticmethod
    def parse_json_content(content: str) -> Dict[str, Any]:
        """Parse JSON from raw model content, tolerating fenced Markdown."""
        cleaned_response = content.strip()
        cleaned_response = re.sub(
            r"^```(?:json)?\s*\n?",
            "",
            cleaned_response,
            flags=re.IGNORECASE,
        )
        cleaned_response = re.sub(r"\n?```\s*$", "", cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM returned invalid JSON: {cleaned_response}") from exc

    def refine_brief(self, brief_input: Any) -> Dict[str, Any]:
        """Delegate brief refinement to the configured provider."""
        return self.provider.refine_brief(brief_input)

    def healthcheck(self) -> Dict[str, Any]:
        """Expose provider health status."""
        return self.provider.healthcheck()
