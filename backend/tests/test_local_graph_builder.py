import sys
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

if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")

    class _OpenAI:
        def __init__(self, *args, **kwargs):
            pass

    openai_stub.OpenAI = _OpenAI
    sys.modules["openai"] = openai_stub

if "anthropic" not in sys.modules:
    anthropic_stub = types.ModuleType("anthropic")

    class _Anthropic:
        def __init__(self, *args, **kwargs):
            self.messages = types.SimpleNamespace(
                create=lambda **kwargs: types.SimpleNamespace(
                    content=[types.SimpleNamespace(text='{"ok": true}')],
                    stop_reason="end_turn",
                )
            )

    anthropic_stub.Anthropic = _Anthropic
    sys.modules["anthropic"] = anthropic_stub

from app.llm.capabilities import API_PROVIDER_CAPABILITIES
from app.llm.providers.base import BaseLLMProvider, LLMChatResult
from app.services.local_graph_builder import LocalGraphBuilder
from app.utils.llm_client import LLMClient


class SequenceProvider(BaseLLMProvider):
    provider_type = "sequence"
    mode = "api"

    def __init__(self, responses):
        self.responses = list(responses)

    @property
    def capabilities(self):
        return API_PROVIDER_CAPABILITIES

    def healthcheck(self):
        return {"ok": True}

    def chat_with_metadata(self, messages, temperature=0.7, max_tokens=4096, response_format=None):
        if not self.responses:
            raise AssertionError("No more fake responses configured")
        return LLMChatResult(content=self.responses.pop(0), finish_reason="stop")


class TestLocalGraphBuilder(unittest.TestCase):
    def test_builder_merges_duplicate_entities_and_links_edges(self):
        provider = SequenceProvider(
            [
                """
                {
                  "entities": [
                    {"name": "Alice", "entity_type": "Person", "summary": "Team lead", "attributes": {"role": "Lead"}},
                    {"name": "Acme", "entity_type": "Organization", "summary": "Employer", "attributes": {}}
                  ],
                  "relations": [
                    {"type": "WORKS_FOR", "source": "Alice", "target": "Acme", "fact": "Alice works for Acme", "attributes": {}}
                  ]
                }
                """,
                """
                {
                  "entities": [
                    {"name": "alice ", "entity_type": "Person", "summary": "Leads the team", "attributes": {"location": "Remote"}},
                    {"name": "Bob", "entity_type": "Person", "summary": "Reports to Alice", "attributes": {}}
                  ],
                  "relations": [
                    {"type": "RESPONDS_TO", "source": "Bob", "target": "Alice", "fact": "Bob responds to Alice", "attributes": {}}
                  ]
                }
                """,
            ]
        )
        builder = LocalGraphBuilder(llm_client=LLMClient(provider=provider))

        graph = builder.build(
            text="Alice works for Acme.\n\nBob responds to Alice.",
            ontology={
                "entity_types": [{"name": "Person"}, {"name": "Organization"}],
                "edge_types": [{"name": "WORKS_FOR"}, {"name": "RESPONDS_TO"}],
            },
            chunk_size=30,
            chunk_overlap=0,
        )

        self.assertEqual(len(graph["nodes"]), 3)
        self.assertEqual(len(graph["edges"]), 2)

        alice = next(node for node in graph["nodes"] if node["name"] == "Alice")
        self.assertIn("Person", alice["labels"])
        self.assertEqual(alice["attributes"]["role"], "Lead")
        self.assertEqual(alice["attributes"]["location"], "Remote")
        self.assertIn("Team lead", alice["summary"])
        self.assertIn("Leads the team", alice["summary"])

        works_for = next(edge for edge in graph["edges"] if edge["name"] == "WORKS_FOR")
        responds_to = next(edge for edge in graph["edges"] if edge["name"] == "RESPONDS_TO")
        self.assertNotEqual(works_for["source_node_uuid"], works_for["target_node_uuid"])
        self.assertEqual(works_for["target_node_name"], "Acme")
        self.assertEqual(responds_to["target_node_name"], "Alice")

    def test_builder_skips_relations_with_missing_entities(self):
        provider = SequenceProvider(
            [
                """
                {
                  "entities": [
                    {"name": "Alice", "entity_type": "Person", "summary": "Team lead", "attributes": {}}
                  ],
                  "relations": [
                    {"type": "WORKS_FOR", "source": "Alice", "target": "Unknown Corp", "fact": "Alice works for Unknown Corp", "attributes": {}}
                  ]
                }
                """
            ]
        )
        builder = LocalGraphBuilder(llm_client=LLMClient(provider=provider))

        graph = builder.build(
            text="Alice works for Unknown Corp.",
            ontology={
                "entity_types": [{"name": "Person"}, {"name": "Organization"}],
                "edge_types": [{"name": "WORKS_FOR"}],
            },
            chunk_size=200,
            chunk_overlap=0,
        )

        self.assertEqual(len(graph["nodes"]), 1)
        self.assertEqual(len(graph["edges"]), 0)


if __name__ == "__main__":
    unittest.main()
