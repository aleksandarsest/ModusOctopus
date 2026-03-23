"""
Helpers for resolving graph stores from project metadata.
"""

from __future__ import annotations

import os
from typing import Any

from ..models.project import ProjectManager
from .factory import GraphStoreFactory


def _local_graph_root(project_id: str) -> str:
    return os.path.join(ProjectManager.get_project_dir(project_id), "graphs")


def resolve_graph_store_for_project(project: Any):
    backend = getattr(project, "graph_backend", None)
    if backend == "local":
        return GraphStoreFactory.create(
            backend="local",
            project_root=_local_graph_root(project.project_id),
        )
    return GraphStoreFactory.create(backend="zep")


def resolve_graph_store_for_graph_id(graph_id: str):
    project = ProjectManager.find_project_by_graph_id(graph_id)
    if project is None:
        return GraphStoreFactory.create(backend="zep"), None
    return resolve_graph_store_for_project(project), project
