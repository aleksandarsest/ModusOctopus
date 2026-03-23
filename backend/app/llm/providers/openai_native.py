"""
OpenAI native API provider.
"""

from __future__ import annotations

from typing import Optional

from .openai_compatible import OpenAICompatibleProvider


class OpenAINativeProvider(OpenAICompatibleProvider):
    provider_type = "openai"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url or "https://api.openai.com/v1",
            model_name=model_name,
        )
