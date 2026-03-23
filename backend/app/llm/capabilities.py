"""
Capability flags for LLM providers.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LLMCapabilities:
    supports_pipeline: bool
    supports_refinement: bool
    supports_chat_json: bool = True
    supports_healthcheck: bool = True


API_PROVIDER_CAPABILITIES = LLMCapabilities(
    supports_pipeline=True,
    supports_refinement=True,
    supports_chat_json=True,
    supports_healthcheck=True,
)


CLI_PROVIDER_CAPABILITIES = LLMCapabilities(
    supports_pipeline=False,
    supports_refinement=True,
    supports_chat_json=False,
    supports_healthcheck=True,
)
