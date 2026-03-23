"""
Graph store factory.
"""

from __future__ import annotations

from typing import Any, Optional

from .base import GraphStore
from .local_store import LocalGraphStore
from .zep_store import ZepGraphStore


class GraphStoreFactory:
    @staticmethod
    def resolve_backend(backend: Optional[str]) -> str:
        if backend is None:
            return "local"
        normalized = backend.strip().lower()
        if normalized not in {"local", "zep"}:
            raise ValueError(f"Unknown graph backend: {backend}")
        return normalized

    @classmethod
    def create(
        cls,
        *,
        backend: Optional[str] = None,
        **kwargs: Any,
    ) -> GraphStore:
        resolved_backend = cls.resolve_backend(backend)
        if resolved_backend == "zep":
            return ZepGraphStore(
                builder=kwargs.get("zep_builder"),
                tools=kwargs.get("zep_tools"),
            )
        if resolved_backend == "local":
            project_root = kwargs.get("project_root")
            if not project_root:
                raise ValueError("project_root is required for the local graph backend")
            return LocalGraphStore(project_root=project_root)
        raise ValueError(f"Unsupported graph backend: {resolved_backend}")
