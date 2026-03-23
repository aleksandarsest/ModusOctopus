"""
Backend-agnostic graph store contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Sequence

from .models import (
    GraphContext,
    GraphData,
    GraphIngestionResult,
    GraphMetadata,
    GraphSearchResult,
    GraphStatistics,
)


class GraphStore(ABC):
    """Contract for graph backends."""

    backend_name: str = "unknown"

    @property
    def name(self) -> str:
        return self.backend_name

    @abstractmethod
    def create_graph(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphMetadata:
        raise NotImplementedError

    @abstractmethod
    def get_graph(self, graph_id: str) -> GraphMetadata:
        raise NotImplementedError

    @abstractmethod
    def apply_ontology(self, graph_id: str, ontology: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def ingest_chunks(
        self,
        graph_id: str,
        chunks: Sequence[str],
        *,
        batch_size: int = 3,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> GraphIngestionResult:
        raise NotImplementedError

    @abstractmethod
    def get_graph_data(self, graph_id: str) -> GraphData:
        raise NotImplementedError

    @abstractmethod
    def delete_graph(self, graph_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        graph_id: str,
        query: str,
        *,
        limit: int = 10,
        scope: str = "edges",
    ) -> GraphSearchResult:
        raise NotImplementedError

    @abstractmethod
    def get_graph_statistics(self, graph_id: str) -> GraphStatistics:
        raise NotImplementedError

    @abstractmethod
    def get_context(
        self,
        graph_id: str,
        simulation_requirement: str,
        *,
        limit: int = 30,
    ) -> GraphContext:
        raise NotImplementedError
