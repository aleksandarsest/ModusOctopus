"""
Graph store value objects shared across backend implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GraphMetadata:
    graph_id: str
    name: str = ""
    description: str = ""
    backend: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "name": self.name,
            "description": self.description,
            "backend": self.backend,
            "metadata": dict(self.metadata),
        }


@dataclass
class GraphData:
    graph_id: str
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    backend: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "nodes": list(self.nodes),
            "edges": list(self.edges),
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "backend": self.backend,
            "metadata": dict(self.metadata),
        }


@dataclass
class GraphSearchResult:
    query: str
    facts: List[str] = field(default_factory=list)
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    edges: List[Dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    backend: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "facts": list(self.facts),
            "nodes": list(self.nodes),
            "edges": list(self.edges),
            "total_count": self.total_count,
            "backend": self.backend,
        }


@dataclass
class GraphStatistics:
    graph_id: str
    total_nodes: int = 0
    total_edges: int = 0
    entity_types: Dict[str, int] = field(default_factory=dict)
    relation_types: Dict[str, int] = field(default_factory=dict)
    backend: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "entity_types": dict(self.entity_types),
            "relation_types": dict(self.relation_types),
            "backend": self.backend,
        }


@dataclass
class GraphContext:
    simulation_requirement: str
    related_facts: List[str] = field(default_factory=list)
    graph_statistics: GraphStatistics | None = None
    entities: List[Dict[str, Any]] = field(default_factory=list)
    total_entities: int = 0
    backend: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_requirement": self.simulation_requirement,
            "related_facts": list(self.related_facts),
            "graph_statistics": self.graph_statistics.to_dict() if self.graph_statistics else None,
            "entities": list(self.entities),
            "total_entities": self.total_entities,
            "backend": self.backend,
        }


@dataclass
class GraphIngestionResult:
    graph_id: str
    chunk_count: int = 0
    episode_uuids: List[str] = field(default_factory=list)
    backend: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "chunk_count": self.chunk_count,
            "episode_uuids": list(self.episode_uuids),
            "backend": self.backend,
            "metadata": dict(self.metadata),
        }
