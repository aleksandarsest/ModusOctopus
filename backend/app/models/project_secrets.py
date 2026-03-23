"""
Per-project secret storage for LLM provider credentials.

Secrets are stored separately from project metadata so the project JSON can
remain safe to expose while still supporting per-project API key configuration.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from ..config import Config


class ProjectSecretsStore:
    """Local secret store keyed by project ID."""

    PROJECTS_DIR = os.path.join(Config.UPLOAD_FOLDER, "projects")

    @classmethod
    def _get_existing_project_dir(cls, project_id: str) -> str:
        project_dir = os.path.join(cls.PROJECTS_DIR, project_id)
        if not os.path.isdir(project_dir):
            raise FileNotFoundError(f"Project directory does not exist: {project_id}")
        return project_dir

    @classmethod
    def _get_project_secrets_path(cls, project_id: str) -> str:
        return os.path.join(cls.PROJECTS_DIR, project_id, Config.PROJECT_LLM_SECRETS_FILENAME)

    @staticmethod
    def mask_secret(secret: Optional[str]) -> Optional[str]:
        if not secret:
            return None
        if len(secret) <= 8:
            return "*" * len(secret)
        return f"{secret[:5]}...{secret[-4:]}"

    @classmethod
    def save_project_api_secret(
        cls,
        project_id: str,
        provider_type: str,
        api_key: str,
    ) -> Dict[str, Any]:
        cls._get_existing_project_dir(project_id)
        payload = {
            "project_id": project_id,
            "provider_type": provider_type,
            "masked_api_key": cls.mask_secret(api_key),
            "saved_at": datetime.now().isoformat(),
        }
        secret_payload = {
            **payload,
            "api_key": api_key,
        }
        with open(cls._get_project_secrets_path(project_id), "w", encoding="utf-8") as f:
            json.dump(secret_payload, f, ensure_ascii=False, indent=2)
        return payload

    @classmethod
    def get_project_api_secret(cls, project_id: str) -> Optional[Dict[str, Any]]:
        secrets_path = cls._get_project_secrets_path(project_id)
        if not os.path.exists(secrets_path):
            return None
        with open(secrets_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def delete_project_api_secret(cls, project_id: str) -> bool:
        secrets_path = cls._get_project_secrets_path(project_id)
        if not os.path.exists(secrets_path):
            return False
        os.remove(secrets_path)
        return True
