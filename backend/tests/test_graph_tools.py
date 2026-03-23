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
from app.services.graph_tools import LocalGraphToolsService


class TestLocalGraphToolsService(unittest.TestCase):
    def test_local_graph_tools_cover_report_search_methods(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalGraphStore(project_root=tmpdir)
            graph = store.create_graph("Report Graph")
            store.replace_graph_data(
                graph.graph_id,
                nodes=[
                    {
                        "uuid": "n1",
                        "name": "Alice",
                        "labels": ["Entity", "Person"],
                        "summary": "Leads the response",
                        "attributes": {},
                    }
                ],
                edges=[
                    {
                        "uuid": "e1",
                        "name": "RESPONDS_TO",
                        "fact": "Alice responds to the policy change",
                        "source_node_uuid": "n1",
                        "target_node_uuid": "n1",
                        "source_node_name": "Alice",
                        "target_node_name": "Alice",
                        "attributes": {},
                    }
                ],
            )

            tools = LocalGraphToolsService(graph_store=store)
            quick = tools.quick_search(graph.graph_id, "Alice", limit=5)
            panorama = tools.panorama_search(graph.graph_id, "policy")
            insight = tools.insight_forge(
                graph_id=graph.graph_id,
                query="How is Alice positioned?",
                simulation_requirement="Assess likely reaction",
                report_context="Risk section",
            )
            stats = tools.get_graph_statistics(graph.graph_id)
            context = tools.get_simulation_context(graph.graph_id, "Assess likely reaction")

            self.assertGreaterEqual(quick.total_count, 1)
            self.assertGreaterEqual(panorama.total_nodes, 1)
            self.assertGreaterEqual(insight.total_facts, 1)
            self.assertEqual(stats["total_nodes"], 1)
            self.assertEqual(context["total_entities"], 1)


if __name__ == "__main__":
    unittest.main()
