import sys
import tempfile
import types
import unittest
from pathlib import Path

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

if "zep_cloud.client" not in sys.modules:
    zep_client_stub = types.ModuleType("zep_cloud.client")

    class _Zep:
        def __init__(self, *args, **kwargs):
            pass

    zep_client_stub.Zep = _Zep
    sys.modules["zep_cloud.client"] = zep_client_stub
    zep_pkg = types.ModuleType("zep_cloud")
    zep_pkg.client = zep_client_stub
    zep_pkg.EpisodeData = object
    zep_pkg.EntityEdgeSourceTarget = object
    zep_pkg.InternalServerError = Exception
    sys.modules["zep_cloud"] = zep_pkg

from app.graph_store import LocalGraphStore
from app.services.graph_entity_reader import GraphEntityReader


class TestGraphEntityReader(unittest.TestCase):
    def test_reader_filters_local_entities_and_enriches_context(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalGraphStore(project_root=tmpdir)
            graph = store.create_graph("Reader Graph")
            store.replace_graph_data(
                graph.graph_id,
                nodes=[
                    {
                        "uuid": "n1",
                        "name": "Alice",
                        "labels": ["Entity", "Person"],
                        "summary": "Lead",
                        "attributes": {"role": "Lead"},
                    },
                    {
                        "uuid": "n2",
                        "name": "Acme",
                        "labels": ["Entity", "Organization"],
                        "summary": "Employer",
                        "attributes": {},
                    },
                ],
                edges=[
                    {
                        "uuid": "e1",
                        "name": "WORKS_FOR",
                        "fact": "Alice works for Acme",
                        "source_node_uuid": "n1",
                        "target_node_uuid": "n2",
                        "source_node_name": "Alice",
                        "target_node_name": "Acme",
                        "attributes": {},
                    }
                ],
            )

            reader = GraphEntityReader(store)
            result = reader.filter_defined_entities(graph.graph_id, defined_entity_types=["Person"], enrich_with_edges=True)

            self.assertEqual(result.filtered_count, 1)
            entity = result.entities[0]
            self.assertEqual(entity.name, "Alice")
            self.assertEqual(entity.related_edges[0]["edge_name"], "WORKS_FOR")
            self.assertEqual(entity.related_nodes[0]["name"], "Acme")

    def test_reader_gets_entity_detail_and_entities_by_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalGraphStore(project_root=tmpdir)
            graph = store.create_graph("Detail Graph")
            store.replace_graph_data(
                graph.graph_id,
                nodes=[
                    {
                        "uuid": "n1",
                        "name": "Alice",
                        "labels": ["Entity", "Person"],
                        "summary": "Lead",
                        "attributes": {"role": "Lead"},
                    },
                    {
                        "uuid": "n2",
                        "name": "Bob",
                        "labels": ["Entity", "Person"],
                        "summary": "Engineer",
                        "attributes": {"role": "Engineer"},
                    },
                ],
                edges=[],
            )

            reader = GraphEntityReader(store)
            detail = reader.get_entity_with_context(graph.graph_id, "n1")
            entities = reader.get_entities_by_type(graph.graph_id, "Person", enrich_with_edges=False)

            self.assertIsNotNone(detail)
            self.assertEqual(detail.name, "Alice")
            self.assertEqual(len(entities), 2)


if __name__ == "__main__":
    unittest.main()
