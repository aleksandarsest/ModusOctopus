"""
Helpers for project-level LLM provider configuration.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..llm.factory import LLMProviderFactory
from ..models.project_secrets import ProjectSecretsStore

API_PROVIDER_TYPES = {"openai_compatible", "openai", "anthropic"}
CLI_PROVIDER_TYPES = {"codex_cli", "claude_code_cli"}


def build_project_llm_metadata(
    raw_config: Optional[Dict[str, Any]],
    *,
    masked_api_key: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Sanitize user-supplied provider config for project metadata storage."""
    if not raw_config:
        return None

    provider_type = raw_config.get("provider_type")
    if not provider_type:
        raise ValueError("provider_type is required")

    metadata: Dict[str, Any] = {
        "provider_type": provider_type,
        "mode": "cli" if provider_type in CLI_PROVIDER_TYPES else "api",
    }

    for field in ("model_name", "base_url", "executable", "working_directory"):
        value = raw_config.get(field)
        if value:
            metadata[field] = value

    provider = LLMProviderFactory.create(raw_config)
    capabilities = provider.capabilities
    metadata["supports_pipeline"] = capabilities.supports_pipeline
    metadata["supports_refinement"] = capabilities.supports_refinement
    metadata["supports_chat_json"] = capabilities.supports_chat_json

    if masked_api_key:
        metadata["api_key_source"] = "project"
        metadata["api_key_masked"] = masked_api_key

    return metadata


def resolve_project_provider_config(project: Any) -> Optional[Dict[str, Any]]:
    """Merge project metadata with stored secrets to produce runtime provider config."""
    if project is None or not getattr(project, "llm_config", None):
        return None

    resolved = dict(project.llm_config)
    secret = ProjectSecretsStore.get_project_api_secret(project.project_id)
    if secret and secret.get("api_key"):
        resolved["api_key"] = secret["api_key"]

    return resolved
