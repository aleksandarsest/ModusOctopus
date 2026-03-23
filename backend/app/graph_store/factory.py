"""
Graph store factory.
"""

from __future__ import annotations

from typing import Any, Optional

from .base import GraphStore


class GraphStoreFactory:
    DEFAULT_BACKEND = "zep"
    SUPPORTED_BACKENDS = {"zep", "local"}

    @classmethod
    def resolve_backend(
        cls,
        backend: Optional[str] = None,
        *,
        graph_backend: Optional[str] = None,
    ) -> str:
        candidate = backend if backend is not None else graph_backend
        resolved = (candidate or cls.DEFAULT_BACKEND).strip().lower()
        if resolved not in cls.SUPPORTED_BACKENDS:
            raise ValueError(f"Unknown graph backend: {resolved}")
        return resolved

    @classmethod
    def create(
        cls,
        backend: Optional[str] = None,
        *,
        graph_backend: Optional[str] = None,
        zep_api_key: Optional[str] = None,
        zep_builder: Any = None,
        zep_tools: Any = None,
    ) -> GraphStore:
        resolved = cls.resolve_backend(backend, graph_backend=graph_backend)

        if resolved == "zep":
            from .zep_store import ZepGraphStore

            return ZepGraphStore(
                api_key=zep_api_key,
                builder=zep_builder,
                tools=zep_tools,
            )

        raise NotImplementedError("LocalGraphStore is not implemented yet")

    @classmethod
    def from_project(
        cls,
        project: Any,
        **kwargs: Any,
    ) -> GraphStore:
        graph_backend = getattr(project, "graph_backend", None)
        if graph_backend is None and isinstance(project, dict):
            graph_backend = project.get("graph_backend")
        return cls.create(graph_backend=graph_backend, **kwargs)

