"""
Zep-backed graph store adapter.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Callable, Dict, Optional, Sequence

from ..config import Config
from .base import GraphStore
from .models import (
    GraphContext,
    GraphData,
    GraphIngestionResult,
    GraphMetadata,
    GraphSearchResult,
    GraphStatistics,
)


def _payload_to_dict(payload: Any) -> Dict[str, Any]:
    if payload is None:
        return {}
    if isinstance(payload, dict):
        return dict(payload)
    if is_dataclass(payload):
        return asdict(payload)
    if hasattr(payload, "to_dict") and callable(payload.to_dict):
        result = payload.to_dict()
        if isinstance(result, dict):
            return result
    if hasattr(payload, "__dict__"):
        return {
            key: value
            for key, value in vars(payload).items()
            if not key.startswith("_")
        }
    return {}


class ZepGraphStore(GraphStore):
    backend_name = "zep"

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        builder: Any = None,
        tools: Any = None,
    ):
        self.api_key = api_key or Config.ZEP_API_KEY
        self._builder = builder
        self._tools = tools
        self._graph_registry: Dict[str, GraphMetadata] = {}

    def _require_api_key(self) -> str:
        if not self.api_key:
            raise ValueError("ZEP_API_KEY is not configured")
        return self.api_key

    def _builder_service(self):
        if self._builder is None:
            self._require_api_key()
            from ..services.graph_builder import GraphBuilderService

            self._builder = GraphBuilderService(api_key=self.api_key)
        return self._builder

    def _tools_service(self):
        if self._tools is None:
            self._require_api_key()
            from ..services.zep_tools import ZepToolsService

            self._tools = ZepToolsService(api_key=self.api_key)
        return self._tools

    def _remember_graph(self, graph: GraphMetadata) -> GraphMetadata:
        self._graph_registry[graph.graph_id] = graph
        return graph

    def _graph_metadata_for(self, graph_id: str) -> GraphMetadata:
        existing = self._graph_registry.get(graph_id)
        if existing is not None:
            return existing

        graph_data = self.get_graph_data(graph_id)
        stats = self.get_graph_statistics(graph_id)
        metadata = {
            "node_count": graph_data.node_count,
            "edge_count": graph_data.edge_count,
            "entity_types": dict(stats.entity_types),
            "relation_types": dict(stats.relation_types),
        }
        return GraphMetadata(
            graph_id=graph_id,
            name=graph_id,
            description="",
            backend=self.backend_name,
            metadata=metadata,
        )

    def create_graph(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphMetadata:
        graph_id = self._builder_service().create_graph(name)
        graph_metadata = GraphMetadata(
            graph_id=graph_id,
            name=name,
            description=description,
            backend=self.backend_name,
            metadata=dict(metadata or {}),
        )
        if description:
            graph_metadata.metadata.setdefault("description", description)
        graph_metadata.metadata.setdefault("graph_name", name)
        return self._remember_graph(graph_metadata)

    def get_graph(self, graph_id: str) -> GraphMetadata:
        return self._graph_metadata_for(graph_id)

    def apply_ontology(self, graph_id: str, ontology: Dict[str, Any]) -> None:
        self._builder_service().set_ontology(graph_id, ontology)
        graph = self._graph_registry.get(graph_id)
        if graph is None:
            graph = GraphMetadata(graph_id=graph_id, backend=self.backend_name)
        graph.metadata["ontology"] = dict(ontology)
        graph.metadata["ontology_applied"] = True
        self._graph_registry[graph_id] = graph

    def ingest_chunks(
        self,
        graph_id: str,
        chunks: Sequence[str],
        *,
        batch_size: int = 3,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> GraphIngestionResult:
        chunk_list = list(chunks)
        episode_uuids = self._builder_service().add_text_batches(
            graph_id=graph_id,
            chunks=chunk_list,
            batch_size=batch_size,
            progress_callback=progress_callback,
        )
        return GraphIngestionResult(
            graph_id=graph_id,
            chunk_count=len(chunk_list),
            episode_uuids=list(episode_uuids or []),
            backend=self.backend_name,
            metadata={"batch_size": batch_size},
        )

    def get_graph_data(self, graph_id: str) -> GraphData:
        data = _payload_to_dict(self._builder_service().get_graph_data(graph_id))
        return GraphData(
            graph_id=data.get("graph_id", graph_id),
            nodes=list(data.get("nodes", [])),
            edges=list(data.get("edges", [])),
            node_count=int(data.get("node_count", len(data.get("nodes", [])))),
            edge_count=int(data.get("edge_count", len(data.get("edges", [])))),
            backend=self.backend_name,
            metadata={key: value for key, value in data.items() if key not in {"graph_id", "nodes", "edges", "node_count", "edge_count"}},
        )

    def delete_graph(self, graph_id: str) -> None:
        self._builder_service().delete_graph(graph_id)
        self._graph_registry.pop(graph_id, None)

    def search(
        self,
        graph_id: str,
        query: str,
        *,
        limit: int = 10,
        scope: str = "edges",
    ) -> GraphSearchResult:
        payload = _payload_to_dict(
            self._tools_service().search_graph(
                graph_id=graph_id,
                query=query,
                limit=limit,
                scope=scope,
            )
        )
        facts = list(payload.get("facts", []))
        return GraphSearchResult(
            query=payload.get("query", query),
            facts=facts,
            nodes=list(payload.get("nodes", [])),
            edges=list(payload.get("edges", [])),
            total_count=int(payload.get("total_count", len(facts))),
            backend=self.backend_name,
        )

    def get_graph_statistics(self, graph_id: str) -> GraphStatistics:
        payload = _payload_to_dict(self._tools_service().get_graph_statistics(graph_id))
        return GraphStatistics(
            graph_id=payload.get("graph_id", graph_id),
            total_nodes=int(payload.get("total_nodes", 0)),
            total_edges=int(payload.get("total_edges", 0)),
            entity_types=dict(payload.get("entity_types", {})),
            relation_types=dict(payload.get("relation_types", {})),
            backend=self.backend_name,
        )

    def get_context(
        self,
        graph_id: str,
        simulation_requirement: str,
        *,
        limit: int = 30,
    ) -> GraphContext:
        payload = _payload_to_dict(
            self._tools_service().get_simulation_context(
                graph_id=graph_id,
                simulation_requirement=simulation_requirement,
                limit=limit,
            )
        )
        stats_payload = payload.get("graph_statistics")
        stats = None
        if stats_payload:
            stats_dict = _payload_to_dict(stats_payload)
            stats = GraphStatistics(
                graph_id=stats_dict.get("graph_id", graph_id),
                total_nodes=int(stats_dict.get("total_nodes", 0)),
                total_edges=int(stats_dict.get("total_edges", 0)),
                entity_types=dict(stats_dict.get("entity_types", {})),
                relation_types=dict(stats_dict.get("relation_types", {})),
                backend=self.backend_name,
            )
        return GraphContext(
            simulation_requirement=payload.get("simulation_requirement", simulation_requirement),
            related_facts=list(payload.get("related_facts", [])),
            graph_statistics=stats,
            entities=list(payload.get("entities", [])),
            total_entities=int(payload.get("total_entities", 0)),
            backend=self.backend_name,
        )

