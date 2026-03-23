"""
Snapshot-backed local graph store.
"""

from __future__ import annotations

import json
import os
import uuid
from collections import Counter
from typing import Any, Dict, List, Optional

from .base import GraphStore
from .models import (
    GraphContext,
    GraphData,
    GraphIngestionResult,
    GraphMetadata,
    GraphSearchResult,
    GraphStatistics,
)


class LocalGraphStore(GraphStore):
    backend = "local"

    def __init__(self, *, project_root: str):
        self.project_root = project_root
        os.makedirs(self.project_root, exist_ok=True)

    def _snapshot_path(self, graph_id: str) -> str:
        return os.path.join(self.project_root, f"{graph_id}.json")

    def _load_snapshot(self, graph_id: str) -> Dict[str, Any]:
        snapshot_path = self._snapshot_path(graph_id)
        if not os.path.exists(snapshot_path):
            raise KeyError(f"Graph snapshot not found: {graph_id}")
        with open(snapshot_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_snapshot(self, graph_id: str, snapshot: Dict[str, Any]) -> None:
        snapshot_path = self._snapshot_path(graph_id)
        with open(snapshot_path, "w", encoding="utf-8") as handle:
            json.dump(snapshot, handle, ensure_ascii=False, indent=2)

    def create_graph(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphMetadata:
        graph_id = f"local_{uuid.uuid4().hex[:16]}"
        graph = GraphMetadata(
            graph_id=graph_id,
            name=name,
            description=description,
            metadata=dict(metadata or {}),
            backend=self.backend,
        )
        self._save_snapshot(
            graph_id,
            {
                "graph": {
                    "graph_id": graph.graph_id,
                    "name": graph.name,
                    "description": graph.description,
                    "metadata": graph.metadata,
                    "backend": self.backend,
                },
                "ontology": None,
                "chunks": [],
                "nodes": [],
                "edges": [],
            },
        )
        return graph

    def get_graph(self, graph_id: str) -> GraphMetadata:
        graph = self._load_snapshot(graph_id)["graph"]
        return GraphMetadata(
            graph_id=graph["graph_id"],
            name=graph["name"],
            description=graph.get("description"),
            metadata=dict(graph.get("metadata") or {}),
            backend=graph.get("backend", self.backend),
        )

    def apply_ontology(self, graph_id: str, ontology: Dict[str, Any]) -> None:
        snapshot = self._load_snapshot(graph_id)
        snapshot["ontology"] = ontology
        self._save_snapshot(graph_id, snapshot)

    def ingest_chunks(
        self,
        graph_id: str,
        chunks: List[str],
        *,
        batch_size: int = 3,
    ) -> GraphIngestionResult:
        snapshot = self._load_snapshot(graph_id)
        existing_chunks = list(snapshot.get("chunks") or [])
        start_index = len(existing_chunks)
        existing_chunks.extend(
            {
                "chunk_id": f"chunk_{start_index + index + 1}",
                "text": chunk,
            }
            for index, chunk in enumerate(chunks)
        )
        snapshot["chunks"] = existing_chunks
        self._save_snapshot(graph_id, snapshot)
        return GraphIngestionResult(
            graph_id=graph_id,
            chunk_count=len(chunks),
            batch_size=batch_size,
            episode_uuids=[chunk["chunk_id"] for chunk in existing_chunks[-len(chunks):]],
            backend=self.backend,
        )

    def replace_graph_data(
        self,
        graph_id: str,
        *,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> None:
        snapshot = self._load_snapshot(graph_id)
        snapshot["nodes"] = nodes
        snapshot["edges"] = edges
        self._save_snapshot(graph_id, snapshot)

    def get_graph_data(self, graph_id: str) -> GraphData:
        snapshot = self._load_snapshot(graph_id)
        nodes = list(snapshot.get("nodes") or [])
        edges = list(snapshot.get("edges") or [])
        return GraphData(
            graph_id=graph_id,
            nodes=nodes,
            edges=edges,
            node_count=len(nodes),
            edge_count=len(edges),
            backend=self.backend,
        )

    def search(
        self,
        graph_id: str,
        query: str,
        *,
        limit: int = 10,
        scope: str = "edges",
    ) -> GraphSearchResult:
        snapshot = self._load_snapshot(graph_id)
        needle = query.lower().strip()
        matched_nodes = []
        matched_edges = []
        facts = []

        if scope in {"nodes", "both", "edges"}:
            for node in snapshot.get("nodes") or []:
                haystack = " ".join(
                    str(part)
                    for part in (
                        node.get("name", ""),
                        node.get("summary", ""),
                        json.dumps(node.get("attributes", {}), ensure_ascii=False),
                    )
                ).lower()
                if needle and needle in haystack:
                    matched_nodes.append(node)
                    if node.get("summary"):
                        facts.append(f"[{node.get('name', 'Unknown')}]: {node['summary']}")

        if scope in {"edges", "both"}:
            for edge in snapshot.get("edges") or []:
                haystack = " ".join(
                    str(part)
                    for part in (
                        edge.get("name", ""),
                        edge.get("fact", ""),
                        json.dumps(edge.get("attributes", {}), ensure_ascii=False),
                    )
                ).lower()
                if needle and needle in haystack:
                    matched_edges.append(edge)
                    if edge.get("fact"):
                        facts.append(edge["fact"])

        matched_nodes = matched_nodes[:limit]
        matched_edges = matched_edges[:limit]
        facts = facts[: limit * 2]

        return GraphSearchResult(
            query=query,
            facts=facts,
            nodes=matched_nodes,
            edges=matched_edges,
            total_count=len(matched_nodes) + len(matched_edges),
            backend=self.backend,
        )

    def get_graph_statistics(self, graph_id: str) -> GraphStatistics:
        snapshot = self._load_snapshot(graph_id)
        nodes = snapshot.get("nodes") or []
        edges = snapshot.get("edges") or []

        entity_types: Counter[str] = Counter()
        for node in nodes:
            for label in node.get("labels") or []:
                if label not in {"Entity", "Node"}:
                    entity_types[label] += 1

        relation_types = Counter(edge.get("name", "") for edge in edges if edge.get("name"))

        return GraphStatistics(
            graph_id=graph_id,
            total_nodes=len(nodes),
            total_edges=len(edges),
            entity_types=dict(entity_types),
            relation_types=dict(relation_types),
            backend=self.backend,
        )

    def get_context(
        self,
        graph_id: str,
        simulation_requirement: str,
        *,
        limit: int = 30,
    ) -> GraphContext:
        snapshot = self._load_snapshot(graph_id)
        nodes = list(snapshot.get("nodes") or [])[:limit]
        edges = list(snapshot.get("edges") or [])[:limit]
        related_facts = [edge.get("fact", "") for edge in edges if edge.get("fact")]
        entities = [
            {
                "name": node.get("name", "Unknown"),
                "type": next((label for label in node.get("labels", []) if label not in {"Entity", "Node"}), "Entity"),
                "summary": node.get("summary", ""),
            }
            for node in nodes
        ]
        return GraphContext(
            simulation_requirement=simulation_requirement,
            related_facts=related_facts,
            graph_statistics=self.get_graph_statistics(graph_id),
            entities=entities,
            total_entities=len(entities),
            backend=self.backend,
        )

    def delete_graph(self, graph_id: str) -> None:
        snapshot_path = self._snapshot_path(graph_id)
        if os.path.exists(snapshot_path):
            os.remove(snapshot_path)
