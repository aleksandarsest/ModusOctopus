"""
Shared base classes for LLM providers.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..capabilities import LLMCapabilities


@dataclass
class LLMChatResult:
    """Normalized chat response payload across providers."""

    content: str
    finish_reason: Optional[str] = None


class BaseLLMProvider(ABC):
    """Common interface for API and CLI providers."""

    provider_type: str = "base"
    mode: str = "api"

    @property
    @abstractmethod
    def capabilities(self) -> LLMCapabilities:
        """Return the provider capability flags."""

    @abstractmethod
    def healthcheck(self) -> Dict[str, Any]:
        """Return provider availability information."""

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.chat_with_metadata(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        ).content

    def chat_with_metadata(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMChatResult:
        raise NotImplementedError(f"{self.provider_type} does not support chat")

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        return self.chat_json_with_metadata(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )[0]

    def chat_json_with_metadata(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> tuple[Dict[str, Any], LLMChatResult]:
        result = self.chat_with_metadata(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        cleaned = result.content.strip()
        cleaned = cleaned.removeprefix("```json").strip()
        cleaned = cleaned.removeprefix("```").strip()
        cleaned = cleaned.removesuffix("```").strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()
        return json.loads(cleaned), result

    def refine_brief(self, brief_input: Any) -> Dict[str, Any]:
        raise NotImplementedError(f"{self.provider_type} does not support brief refinement")

    @staticmethod
    def _brief_input_to_text(brief_input: Any) -> str:
        if isinstance(brief_input, str):
            return brief_input
        if isinstance(brief_input, dict):
            return json.dumps(brief_input, ensure_ascii=False, indent=2)
        return str(brief_input)
