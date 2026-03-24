"""
Local graph construction from chunk-level extraction.
"""

from __future__ import annotations

import uuid
from typing import Any, Callable, Dict, List, Optional

from ..utils.llm_client import LLMClient
from .text_processor import TextProcessor

LOCAL_GRAPH_EXTRACTION_SYSTEM_PROMPT = """You extract knowledge graph data for ModusOctopus.

Return valid JSON only with this shape:
{
  "entities": [
    {
      "name": "Entity name",
      "entity_type": "One ontology entity type",
      "summary": "Short summary",
      "attributes": {}
    }
  ],
  "relations": [
    {
      "type": "One ontology edge type",
      "source": "Source entity name",
      "target": "Target entity name",
      "fact": "Grounded factual statement from the chunk",
      "attributes": {}
    }
  ]
}

Rules:
- Use only entity types and relation types defined in the ontology.
- Extract only entities and relations clearly grounded in the chunk.
- Do not invent missing entities.
- If nothing useful is present, return empty arrays.
"""


class LocalGraphBuilder:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def build(
        self,
        *,
        text: str,
        ontology: Dict[str, Any],
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        chunks = TextProcessor.split_text(text, chunk_size=chunk_size, overlap=chunk_overlap)
        extracted_chunks: List[Dict[str, Any]] = []
        latest_graph: Optional[Dict[str, Any]] = None
        total_chunks = len(chunks)

        for chunk_index, chunk in enumerate(chunks, start=1):
            extracted_chunks.append(self._extract_from_chunk(chunk, ontology))
            latest_graph = self._consolidate(chunks[:chunk_index], extracted_chunks)
            if progress_callback:
                progress_callback(
                    {
                        "completed_chunks": chunk_index,
                        "total_chunks": total_chunks,
                        "chunk_index": chunk_index,
                        "chunk_text": chunk,
                        "graph": latest_graph,
                    }
                )

        if latest_graph is None:
            return self._consolidate(chunks, extracted_chunks)
        return latest_graph

    def _extract_from_chunk(self, chunk: str, ontology: Dict[str, Any]) -> Dict[str, Any]:
        entity_types = [entity["name"] for entity in ontology.get("entity_types", [])]
        edge_types = [edge["name"] for edge in ontology.get("edge_types", [])]
        prompt = (
            f"Ontology entity types: {entity_types}\n"
            f"Ontology edge types: {edge_types}\n\n"
            f"Chunk:\n{chunk}"
        )
        result = self.llm_client.chat_json(
            messages=[
                {"role": "system", "content": LOCAL_GRAPH_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1600,
        )
        return {
            "entities": list(result.get("entities") or []),
            "relations": list(result.get("relations") or []),
        }

    @staticmethod
    def _normalize_entity_key(entity_type: str, name: str) -> str:
        return f"{entity_type.strip().lower()}::{name.strip().lower()}"

    def _consolidate(self, chunks: List[str], extracted_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes_by_key: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []
        chunks_payload = []

        for chunk_index, (chunk_text, extracted) in enumerate(zip(chunks, extracted_chunks, strict=False), start=1):
            chunk_id = f"chunk_{chunk_index}"
            chunks_payload.append({"chunk_id": chunk_id, "text": chunk_text})

            for entity in extracted.get("entities", []):
                name = (entity.get("name") or "").strip()
                entity_type = (entity.get("entity_type") or "").strip()
                if not name or not entity_type:
                    continue

                key = self._normalize_entity_key(entity_type, name)
                existing = nodes_by_key.get(key)
                summary = (entity.get("summary") or "").strip()
                attributes = dict(entity.get("attributes") or {})

                if existing is None:
                    nodes_by_key[key] = {
                        "uuid": f"node_{uuid.uuid4().hex[:12]}",
                        "name": name,
                        "labels": ["Entity", entity_type],
                        "summary": summary,
                        "attributes": attributes,
                        "source_chunk_ids": [chunk_id],
                    }
                    continue

                for attr_key, attr_value in attributes.items():
                    if attr_key not in existing["attributes"] and attr_value not in (None, ""):
                        existing["attributes"][attr_key] = attr_value

                if summary and summary not in existing["summary"]:
                    existing["summary"] = (
                        f"{existing['summary']} | {summary}" if existing["summary"] else summary
                    )

                if chunk_id not in existing["source_chunk_ids"]:
                    existing["source_chunk_ids"].append(chunk_id)

            for relation in extracted.get("relations", []):
                relation_type = (relation.get("type") or "").strip()
                source_name = (relation.get("source") or "").strip()
                target_name = (relation.get("target") or "").strip()
                fact = (relation.get("fact") or "").strip()
                if not relation_type or not source_name or not target_name:
                    continue

                source_node = self._find_node_by_name(nodes_by_key, source_name)
                target_node = self._find_node_by_name(nodes_by_key, target_name)
                if source_node is None or target_node is None:
                    continue

                edges.append(
                    {
                        "uuid": f"edge_{uuid.uuid4().hex[:12]}",
                        "name": relation_type,
                        "fact": fact,
                        "source_node_uuid": source_node["uuid"],
                        "target_node_uuid": target_node["uuid"],
                        "source_node_name": source_node["name"],
                        "target_node_name": target_node["name"],
                        "attributes": dict(relation.get("attributes") or {}),
                        "source_chunk_ids": [chunk_id],
                    }
                )

        return {
            "chunks": chunks_payload,
            "nodes": list(nodes_by_key.values()),
            "edges": edges,
        }

    @staticmethod
    def _find_node_by_name(nodes_by_key: Dict[str, Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
        normalized_name = name.strip().lower()
        for node in nodes_by_key.values():
            if node["name"].strip().lower() == normalized_name:
                return node
        return None
