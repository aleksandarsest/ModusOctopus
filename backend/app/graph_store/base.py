"""
Abstract graph-store contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .models import (
    GraphContext,
    GraphData,
    GraphIngestionResult,
    GraphMetadata,
    GraphSearchResult,
    GraphStatistics,
)


class GraphStore(ABC):
    backend: str = "unknown"

    @abstractmethod
    def create_graph(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphMetadata:
        """Create a new graph."""

    @abstractmethod
    def get_graph(self, graph_id: str) -> GraphMetadata:
        """Return graph metadata."""

    @abstractmethod
    def apply_ontology(self, graph_id: str, ontology: Dict[str, Any]) -> None:
        """Apply ontology to a graph."""

    @abstractmethod
    def ingest_chunks(
        self,
        graph_id: str,
        chunks: List[str],
        *,
        batch_size: int = 3,
    ) -> GraphIngestionResult:
        """Ingest text chunks into a graph."""

    @abstractmethod
    def get_graph_data(self, graph_id: str) -> GraphData:
        """Fetch graph nodes/edges."""

    @abstractmethod
    def search(
        self,
        graph_id: str,
        query: str,
        *,
        limit: int = 10,
        scope: str = "edges",
    ) -> GraphSearchResult:
        """Search graph content."""

    @abstractmethod
    def get_graph_statistics(self, graph_id: str) -> GraphStatistics:
        """Return graph-level statistics."""

    @abstractmethod
    def get_context(
        self,
        graph_id: str,
        simulation_requirement: str,
        *,
        limit: int = 30,
    ) -> GraphContext:
        """Return graph context for simulation/reporting."""

    @abstractmethod
    def delete_graph(self, graph_id: str) -> None:
        """Delete a graph."""
