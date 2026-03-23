"""
Shared graph-store data structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GraphMetadata:
    graph_id: str
    name: str
    backend: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphData:
    graph_id: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    node_count: int
    edge_count: int
    backend: str


@dataclass
class GraphIngestionResult:
    graph_id: str
    chunk_count: int
    batch_size: int
    episode_uuids: List[str] = field(default_factory=list)
    backend: str = "unknown"


@dataclass
class GraphSearchResult:
    query: str
    facts: List[str]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    total_count: int
    backend: str


@dataclass
class GraphStatistics:
    graph_id: str
    total_nodes: int
    total_edges: int
    entity_types: Dict[str, int] = field(default_factory=dict)
    relation_types: Dict[str, int] = field(default_factory=dict)
    backend: str = "unknown"


@dataclass
class GraphContext:
    simulation_requirement: str
    related_facts: List[str]
    graph_statistics: GraphStatistics
    entities: List[Dict[str, Any]]
    total_entities: int
    backend: str
