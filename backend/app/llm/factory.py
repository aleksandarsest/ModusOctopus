"""
Factory for project-level LLM providers.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from ..config import Config
from .providers.anthropic_provider import AnthropicProvider
from .providers.base import BaseLLMProvider
from .providers.claude_code_cli import ClaudeCodeCLIProvider
from .providers.codex_cli import CodexCLIProvider
from .providers.openai_compatible import OpenAICompatibleProvider
from .providers.openai_native import OpenAINativeProvider


class LLMProviderFactory:
    """Resolve provider instances from project configuration."""

    PROVIDERS: Dict[str, Type[BaseLLMProvider]] = {
        "openai_compatible": OpenAICompatibleProvider,
        "openai": OpenAINativeProvider,
        "anthropic": AnthropicProvider,
        "codex_cli": CodexCLIProvider,
        "claude_code_cli": ClaudeCodeCLIProvider,
    }

    @classmethod
    def create(
        cls,
        provider_config: Optional[Dict[str, Any]] = None,
        *,
        default_api_key: Optional[str] = None,
    ) -> BaseLLMProvider:
        config = dict(provider_config or {})
        provider_type = config.get("provider_type", "openai_compatible")
        provider_cls = cls.PROVIDERS.get(provider_type)

        if provider_cls is None:
            raise ValueError(f"Unknown LLM provider type: {provider_type}")

        if provider_type in {"openai_compatible", "openai"}:
            api_key = config.get("api_key") or default_api_key or Config.LLM_API_KEY
            base_url = config.get("base_url")
            model_name = config.get("model_name")
            return provider_cls(api_key=api_key, base_url=base_url, model_name=model_name)

        if provider_type == "anthropic":
            api_key = config.get("api_key") or default_api_key
            base_url = config.get("base_url")
            model_name = config.get("model_name")
            return provider_cls(api_key=api_key, base_url=base_url, model_name=model_name)

        if provider_type == "codex_cli":
            executable = config.get("executable", "codex")
            working_directory = config.get("working_directory")
            return provider_cls(executable=executable, working_directory=working_directory)

        if provider_type == "claude_code_cli":
            executable = config.get("executable", "claude")
            working_directory = config.get("working_directory")
            return provider_cls(executable=executable, working_directory=working_directory)

        raise ValueError(f"Unsupported LLM provider type: {provider_type}")
