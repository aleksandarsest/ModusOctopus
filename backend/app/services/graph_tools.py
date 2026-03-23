"""
Graph-tool facade for local graph backends.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..graph_store.base import GraphStore
from .graph_entity_reader import GraphEntityReader
from .zep_tools import (
    InsightForgeResult,
    PanoramaResult,
    SearchResult,
)


class LocalGraphToolsService:
    def __init__(self, graph_store: GraphStore, llm_client: Optional[Any] = None):
        self.graph_store = graph_store
        self.llm_client = llm_client
        self.entity_reader = GraphEntityReader(graph_store)

    def search_graph(self, graph_id: str, query: str, limit: int = 10, scope: str = "edges") -> SearchResult:
        result = self.graph_store.search(graph_id, query, limit=limit, scope=scope)
        return SearchResult(
            facts=result.facts,
            edges=result.edges,
            nodes=result.nodes,
            query=result.query,
            total_count=result.total_count,
        )

    def quick_search(self, graph_id: str, query: str, limit: int = 10) -> SearchResult:
        return self.search_graph(graph_id, query, limit=limit, scope="both")

    def get_graph_statistics(self, graph_id: str) -> Dict[str, Any]:
        stats = self.graph_store.get_graph_statistics(graph_id)
        return {
            "graph_id": stats.graph_id,
            "total_nodes": stats.total_nodes,
            "total_edges": stats.total_edges,
            "entity_types": stats.entity_types,
            "relation_types": stats.relation_types,
            "backend": stats.backend,
        }

    def get_simulation_context(
        self,
        graph_id: str,
        simulation_requirement: str,
        limit: int = 30,
    ) -> Dict[str, Any]:
        context = self.graph_store.get_context(
            graph_id,
            simulation_requirement,
            limit=limit,
        )
        return {
            "simulation_requirement": context.simulation_requirement,
            "related_facts": context.related_facts,
            "graph_statistics": self.get_graph_statistics(graph_id),
            "entities": context.entities,
            "total_entities": context.total_entities,
            "backend": context.backend,
        }

    def insight_forge(
        self,
        graph_id: str,
        query: str,
        simulation_requirement: str,
        report_context: str = "",
    ) -> InsightForgeResult:
        search = self.search_graph(graph_id, query, limit=10, scope="both")
        context = self.get_simulation_context(graph_id, simulation_requirement)
        entities = context["entities"][:10]
        semantic_facts = search.facts or context["related_facts"][:10]
        return InsightForgeResult(
            query=query,
            simulation_requirement=simulation_requirement,
            sub_queries=[query] if not report_context else [query, report_context],
            semantic_facts=semantic_facts,
            entity_insights=entities,
            relationship_chains=[
                f"{edge.get('source_node_name', edge.get('source_node_uuid'))} -> "
                f"{edge.get('name', '')} -> "
                f"{edge.get('target_node_name', edge.get('target_node_uuid'))}"
                for edge in search.edges[:10]
            ],
            total_facts=len(semantic_facts),
            total_entities=len(entities),
            total_relationships=len(search.edges),
        )

    def panorama_search(
        self,
        graph_id: str,
        query: str,
        include_expired: bool = True,
    ) -> PanoramaResult:
        del include_expired
        graph_data = self.graph_store.get_graph_data(graph_id)
        search = self.search_graph(graph_id, query, limit=20, scope="both")
        return PanoramaResult(
            query=query,
            all_nodes=[],
            all_edges=[],
            active_facts=search.facts,
            historical_facts=[],
            total_nodes=graph_data.node_count,
            total_edges=graph_data.edge_count,
            active_count=len(search.facts),
            historical_count=0,
        )

    def get_entity_summary(self, graph_id: str, entity_name: str) -> Dict[str, Any]:
        search = self.search_graph(graph_id, entity_name, limit=5, scope="nodes")
        node = search.nodes[0] if search.nodes else None
        return {
            "entity_name": entity_name,
            "found": node is not None,
            "summary": node.get("summary", "") if node else "",
            "labels": node.get("labels", []) if node else [],
            "attributes": node.get("attributes", {}) if node else {},
        }

    def get_entities_by_type(self, graph_id: str, entity_type: str):
        return self.entity_reader.get_entities_by_type(graph_id, entity_type, enrich_with_edges=False)

    def interview_agents(
        self,
        simulation_id: str,
        interview_requirement: str,
        simulation_requirement: str,
        max_agents: int = 5,
    ):
        from .zep_tools import ZepToolsService

        return ZepToolsService(llm_client=self.llm_client).interview_agents(
            simulation_id=simulation_id,
            interview_requirement=interview_requirement,
            simulation_requirement=simulation_requirement,
            max_agents=max_agents,
        )
