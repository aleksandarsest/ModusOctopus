"""
Graph-store-backed entity reader.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ..graph_store.base import GraphStore


@dataclass
class EntityNode:
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]
    related_edges: List[Dict[str, Any]] = field(default_factory=list)
    related_nodes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "labels": self.labels,
            "summary": self.summary,
            "attributes": self.attributes,
            "related_edges": self.related_edges,
            "related_nodes": self.related_nodes,
        }


@dataclass
class FilteredEntities:
    entities: List[EntityNode]
    entity_types: Set[str]
    total_count: int
    filtered_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entities": [entity.to_dict() for entity in self.entities],
            "entity_types": list(self.entity_types),
            "total_count": self.total_count,
            "filtered_count": self.filtered_count,
        }


class GraphEntityReader:
    def __init__(self, graph_store: GraphStore):
        self.graph_store = graph_store

    def filter_defined_entities(
        self,
        graph_id: str,
        defined_entity_types: Optional[List[str]] = None,
        enrich_with_edges: bool = True,
    ) -> FilteredEntities:
        graph_data = self.graph_store.get_graph_data(graph_id)
        all_nodes = graph_data.nodes
        all_edges = graph_data.edges if enrich_with_edges else []
        node_map = {node["uuid"]: node for node in all_nodes}

        filtered_entities: List[EntityNode] = []
        entity_types_found: Set[str] = set()

        for node in all_nodes:
            labels = node.get("labels", [])
            custom_labels = [label for label in labels if label not in {"Entity", "Node"}]
            if not custom_labels:
                continue

            if defined_entity_types:
                matching_labels = [label for label in custom_labels if label in defined_entity_types]
                if not matching_labels:
                    continue
                entity_type = matching_labels[0]
            else:
                entity_type = custom_labels[0]

            entity_types_found.add(entity_type)
            entity = EntityNode(
                uuid=node["uuid"],
                name=node.get("name", ""),
                labels=labels,
                summary=node.get("summary", ""),
                attributes=dict(node.get("attributes") or {}),
            )

            if enrich_with_edges:
                entity.related_edges, entity.related_nodes = self._build_context(
                    node["uuid"],
                    all_edges,
                    node_map,
                )

            filtered_entities.append(entity)

        return FilteredEntities(
            entities=filtered_entities,
            entity_types=entity_types_found,
            total_count=len(all_nodes),
            filtered_count=len(filtered_entities),
        )

    def get_entity_with_context(self, graph_id: str, entity_uuid: str) -> Optional[EntityNode]:
        graph_data = self.graph_store.get_graph_data(graph_id)
        all_nodes = graph_data.nodes
        all_edges = graph_data.edges
        node = next((candidate for candidate in all_nodes if candidate["uuid"] == entity_uuid), None)
        if node is None:
            return None

        node_map = {item["uuid"]: item for item in all_nodes}
        related_edges, related_nodes = self._build_context(entity_uuid, all_edges, node_map)
        return EntityNode(
            uuid=node["uuid"],
            name=node.get("name", ""),
            labels=node.get("labels", []),
            summary=node.get("summary", ""),
            attributes=dict(node.get("attributes") or {}),
            related_edges=related_edges,
            related_nodes=related_nodes,
        )

    def get_entities_by_type(
        self,
        graph_id: str,
        entity_type: str,
        enrich_with_edges: bool = True,
    ) -> List[EntityNode]:
        return self.filter_defined_entities(
            graph_id=graph_id,
            defined_entity_types=[entity_type],
            enrich_with_edges=enrich_with_edges,
        ).entities

    @staticmethod
    def _build_context(
        entity_uuid: str,
        all_edges: List[Dict[str, Any]],
        node_map: Dict[str, Dict[str, Any]],
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        related_edges: List[Dict[str, Any]] = []
        related_node_uuids = set()

        for edge in all_edges:
            if edge.get("source_node_uuid") == entity_uuid:
                related_edges.append(
                    {
                        "direction": "outgoing",
                        "edge_name": edge.get("name", ""),
                        "fact": edge.get("fact", ""),
                        "target_node_uuid": edge.get("target_node_uuid"),
                    }
                )
                if edge.get("target_node_uuid"):
                    related_node_uuids.add(edge["target_node_uuid"])
            elif edge.get("target_node_uuid") == entity_uuid:
                related_edges.append(
                    {
                        "direction": "incoming",
                        "edge_name": edge.get("name", ""),
                        "fact": edge.get("fact", ""),
                        "source_node_uuid": edge.get("source_node_uuid"),
                    }
                )
                if edge.get("source_node_uuid"):
                    related_node_uuids.add(edge["source_node_uuid"])

        related_nodes = []
        for related_uuid in related_node_uuids:
            related = node_map.get(related_uuid)
            if related:
                related_nodes.append(
                    {
                        "uuid": related["uuid"],
                        "name": related.get("name", ""),
                        "labels": related.get("labels", []),
                        "summary": related.get("summary", ""),
                    }
                )

        return related_edges, related_nodes
