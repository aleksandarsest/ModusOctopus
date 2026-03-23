"""
Zep-backed GraphStore adapter.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import GraphStore
from .models import (
    GraphContext,
    GraphData,
    GraphIngestionResult,
    GraphMetadata,
    GraphSearchResult,
    GraphStatistics,
)


class ZepGraphStore(GraphStore):
    backend = "zep"

    def __init__(
        self,
        *,
        builder: Optional[Any] = None,
        tools: Optional[Any] = None,
    ):
        if builder is None:
            from ..services.graph_builder import GraphBuilderService

            builder = GraphBuilderService()
        if tools is None:
            from ..services.zep_tools import ZepToolsService

            tools = ZepToolsService()

        self.builder = builder
        self.tools = tools
        self._graph_metadata: Dict[str, GraphMetadata] = {}

    def create_graph(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphMetadata:
        graph_id = self.builder.create_graph(name)
        graph = GraphMetadata(
            graph_id=graph_id,
            name=name,
            description=description,
            metadata=dict(metadata or {}),
            backend=self.backend,
        )
        self._graph_metadata[graph_id] = graph
        return graph

    def get_graph(self, graph_id: str) -> GraphMetadata:
        graph = self._graph_metadata.get(graph_id)
        if graph is None:
            return GraphMetadata(graph_id=graph_id, name=graph_id, backend=self.backend)
        return graph

    def apply_ontology(self, graph_id: str, ontology: Dict[str, Any]) -> None:
        self.builder.set_ontology(graph_id, ontology)

    def ingest_chunks(
        self,
        graph_id: str,
        chunks: list[str],
        *,
        batch_size: int = 3,
    ) -> GraphIngestionResult:
        episode_uuids = self.builder.add_text_batches(
            graph_id,
            chunks,
            batch_size=batch_size,
        )
        return GraphIngestionResult(
            graph_id=graph_id,
            chunk_count=len(chunks),
            batch_size=batch_size,
            episode_uuids=episode_uuids,
            backend=self.backend,
        )

    def get_graph_data(self, graph_id: str) -> GraphData:
        graph_data = self.builder.get_graph_data(graph_id)
        return GraphData(backend=self.backend, **graph_data)

    def search(
        self,
        graph_id: str,
        query: str,
        *,
        limit: int = 10,
        scope: str = "edges",
    ) -> GraphSearchResult:
        return self.tools.search_graph(graph_id, query, limit=limit, scope=scope)

    def get_graph_statistics(self, graph_id: str) -> GraphStatistics:
        return self.tools.get_graph_statistics(graph_id)

    def get_context(
        self,
        graph_id: str,
        simulation_requirement: str,
        *,
        limit: int = 30,
    ) -> GraphContext:
        return self.tools.get_simulation_context(
            graph_id,
            simulation_requirement,
            limit=limit,
        )

    def delete_graph(self, graph_id: str) -> None:
        self.builder.delete_graph(graph_id)
        self._graph_metadata.pop(graph_id, None)
