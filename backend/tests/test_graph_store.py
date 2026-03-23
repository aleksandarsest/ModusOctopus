import unittest
from dataclasses import asdict
from pathlib import Path
import sys
import types
import tempfile

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if "flask" not in sys.modules:
    flask_stub = types.ModuleType("flask")

    class _Flask:
        def __init__(self, *args, **kwargs):
            pass

    flask_stub.Flask = _Flask
    flask_stub.request = object()
    sys.modules["flask"] = flask_stub

if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")
    flask_cors_stub.CORS = lambda *args, **kwargs: None
    sys.modules["flask_cors"] = flask_cors_stub

from app.graph_store import (
    GraphContext,
    GraphData,
    GraphIngestionResult,
    GraphMetadata,
    LocalGraphStore,
    GraphSearchResult,
    GraphStatistics,
    GraphStoreFactory,
    ZepGraphStore,
)


class DummyBuilder:
    def __init__(self):
        self.created = []
        self.applied = []
        self.ingested = []
        self.deleted = []
        self.graph_data = {
            "graph_id": "graph_1",
            "nodes": [{"uuid": "n1", "name": "Node 1"}],
            "edges": [{"uuid": "e1", "fact": "rel"}],
            "node_count": 1,
            "edge_count": 1,
        }

    def create_graph(self, name):
        self.created.append(name)
        return "graph_1"

    def set_ontology(self, graph_id, ontology):
        self.applied.append((graph_id, ontology))

    def add_text_batches(self, graph_id, chunks, batch_size=3, progress_callback=None):
        self.ingested.append((graph_id, list(chunks), batch_size))
        return ["ep_1", "ep_2"]

    def get_graph_data(self, graph_id):
        return dict(self.graph_data, graph_id=graph_id)

    def delete_graph(self, graph_id):
        self.deleted.append(graph_id)


class DummyTools:
    def __init__(self):
        self.search_calls = []
        self.stats_calls = []
        self.context_calls = []

    def search_graph(self, graph_id, query, limit=10, scope="edges"):
        self.search_calls.append((graph_id, query, limit, scope))
        return GraphSearchResult(
            query=query,
            facts=["fact-1"],
            nodes=[{"uuid": "n1", "name": "Node 1"}],
            edges=[{"uuid": "e1", "fact": "fact-1"}],
            total_count=1,
            backend="zep",
        )

    def get_graph_statistics(self, graph_id):
        self.stats_calls.append(graph_id)
        return GraphStatistics(
            graph_id=graph_id,
            total_nodes=4,
            total_edges=2,
            entity_types={"Person": 3},
            relation_types={"MENTIONS": 2},
            backend="zep",
        )

    def get_simulation_context(self, graph_id, simulation_requirement, limit=30):
        self.context_calls.append((graph_id, simulation_requirement, limit))
        return GraphContext(
            simulation_requirement=simulation_requirement,
            related_facts=["fact-1"],
            graph_statistics=self.get_graph_statistics(graph_id),
            entities=[{"name": "Node 1", "type": "Person"}],
            total_entities=1,
            backend="zep",
        )


class TestGraphStoreFactory(unittest.TestCase):
    def test_resolve_backend_defaults_to_local(self):
        self.assertEqual(GraphStoreFactory.resolve_backend(None), "local")

    def test_resolve_backend_normalizes_input(self):
        self.assertEqual(GraphStoreFactory.resolve_backend(" ZEP "), "zep")

    def test_create_returns_zep_store(self):
        store = GraphStoreFactory.create(
            backend="zep",
            zep_builder=DummyBuilder(),
            zep_tools=DummyTools(),
        )

        self.assertIsInstance(store, ZepGraphStore)

    def test_create_rejects_local_backend_until_implemented(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = GraphStoreFactory.create(backend="local", project_root=tmpdir)

        self.assertIsInstance(store, LocalGraphStore)


class TestZepGraphStore(unittest.TestCase):
    def test_adapter_delegates_core_graph_operations(self):
        builder = DummyBuilder()
        tools = DummyTools()
        store = ZepGraphStore(builder=builder, tools=tools)

        created = store.create_graph("Scenario Graph", description="Demo", metadata={"project_id": "proj_1"})
        store.apply_ontology(created.graph_id, {"entity_types": []})
        ingestion = store.ingest_chunks(created.graph_id, ["alpha", "beta"], batch_size=2)
        graph_data = store.get_graph_data(created.graph_id)
        search = store.search(created.graph_id, "alpha")
        stats = store.get_graph_statistics(created.graph_id)
        context = store.get_context(created.graph_id, "test scenario")
        store.delete_graph(created.graph_id)

        self.assertEqual(created.graph_id, "graph_1")
        self.assertEqual(created.name, "Scenario Graph")
        self.assertEqual(builder.created, ["Scenario Graph"])
        self.assertEqual(builder.applied, [("graph_1", {"entity_types": []})])
        self.assertEqual(ingestion.episode_uuids, ["ep_1", "ep_2"])
        self.assertEqual(graph_data.node_count, 1)
        self.assertEqual(search.facts, ["fact-1"])
        self.assertEqual(stats.total_nodes, 4)
        self.assertEqual(context.total_entities, 1)
        self.assertEqual(builder.deleted, ["graph_1"])

    def test_adapter_tracks_metadata_for_created_graphs(self):
        store = ZepGraphStore(builder=DummyBuilder(), tools=DummyTools())
        created = store.create_graph("Tracked Graph", metadata={"project_id": "proj_2"})

        graph = store.get_graph(created.graph_id)

        self.assertEqual(graph.graph_id, created.graph_id)
        self.assertEqual(graph.name, "Tracked Graph")
        self.assertEqual(graph.metadata["project_id"], "proj_2")
        self.assertEqual(graph.backend, "zep")
        self.assertEqual(asdict(graph)["backend"], "zep")


class TestLocalGraphStore(unittest.TestCase):
    def test_local_store_persists_snapshot_and_can_reload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalGraphStore(project_root=tmpdir)
            graph = store.create_graph("Local Graph", metadata={"project_id": "proj_local"})
            store.apply_ontology(graph.graph_id, {"entity_types": [{"name": "Person"}], "edge_types": []})
            store.ingest_chunks(graph.graph_id, ["Alice leads the project", "Bob responds to Alice"], batch_size=2)
            store.replace_graph_data(
                graph.graph_id,
                nodes=[
                    {
                        "uuid": "n1",
                        "name": "Alice",
                        "labels": ["Entity", "Person"],
                        "summary": "Project lead",
                        "attributes": {"role": "Lead"},
                    },
                    {
                        "uuid": "n2",
                        "name": "Bob",
                        "labels": ["Entity", "Person"],
                        "summary": "Responder",
                        "attributes": {"role": "Staff"},
                    },
                ],
                edges=[
                    {
                        "uuid": "e1",
                        "name": "RESPONDS_TO",
                        "fact": "Bob responds to Alice",
                        "source_node_uuid": "n2",
                        "target_node_uuid": "n1",
                        "source_node_name": "Bob",
                        "target_node_name": "Alice",
                        "attributes": {},
                    }
                ],
            )

            reloaded = LocalGraphStore(project_root=tmpdir)
            graph_data = reloaded.get_graph_data(graph.graph_id)
            stats = reloaded.get_graph_statistics(graph.graph_id)
            search = reloaded.search(graph.graph_id, "Alice")
            context = reloaded.get_context(graph.graph_id, "How will Alice be perceived?")

            self.assertEqual(reloaded.get_graph(graph.graph_id).metadata["project_id"], "proj_local")
            self.assertEqual(graph_data.node_count, 2)
            self.assertEqual(graph_data.edge_count, 1)
            self.assertEqual(stats.entity_types["Person"], 2)
            self.assertEqual(stats.relation_types["RESPONDS_TO"], 1)
            self.assertEqual(search.total_count, 2)
            self.assertEqual(context.total_entities, 2)
            self.assertEqual(context.backend, "local")

    def test_local_store_delete_graph_removes_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalGraphStore(project_root=tmpdir)
            graph = store.create_graph("Disposable Graph")
            snapshot_path = Path(tmpdir) / f"{graph.graph_id}.json"
            self.assertTrue(snapshot_path.exists())

            store.delete_graph(graph.graph_id)

            self.assertFalse(snapshot_path.exists())
            with self.assertRaises(KeyError):
                store.get_graph(graph.graph_id)


if __name__ == "__main__":
    unittest.main()
