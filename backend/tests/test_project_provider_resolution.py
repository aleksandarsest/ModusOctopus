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

if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")

    class _OpenAI:
        def __init__(self, *args, **kwargs):
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(
                    create=lambda **kwargs: types.SimpleNamespace(
                        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='{"ok": true}'), finish_reason="stop")]
                    )
                )
            )

    openai_stub.OpenAI = _OpenAI
    sys.modules["openai"] = openai_stub

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

if "camel.models" not in sys.modules:
    camel_models_stub = types.ModuleType("camel.models")
    camel_models_stub.ModelFactory = object
    sys.modules["camel.models"] = camel_models_stub
    camel_pkg = types.ModuleType("camel")
    camel_pkg.models = camel_models_stub
    sys.modules["camel"] = camel_pkg

if "camel.types" not in sys.modules:
    camel_types_stub = types.ModuleType("camel.types")
    camel_types_stub.ModelPlatformType = object
    camel_types_stub.ModelType = object
    sys.modules["camel.types"] = camel_types_stub

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
from app.llm.factory import LLMProviderFactory
from app.llm.providers.base import BaseLLMProvider, LLMChatResult
from app.services.oasis_profile_generator import OasisProfileGenerator
from app.services.report_agent import ReportAgent
from app.services.simulation_config_generator import SimulationConfigGenerator
from app.utils.llm_client import LLMClient


class DummyZepTools:
    pass


class TruncatedJSONProvider(BaseLLMProvider):
    provider_type = "truncated_json"
    mode = "api"

    def __init__(self, content: str):
        self.content = content

    @property
    def capabilities(self):
        return API_PROVIDER_CAPABILITIES

    def healthcheck(self):
        return {"ok": True}

    def chat_with_metadata(self, messages, temperature=0.7, max_tokens=4096, response_format=None):
        return LLMChatResult(content=self.content, finish_reason="length")


class TestProjectProviderResolution(unittest.TestCase):
    def test_llm_client_uses_provider_factory_config(self):
        client = LLMClient(
            provider_config={
                "provider_type": "openai_compatible",
                "api_key": "test-key",
                "base_url": "https://example.com/v1",
                "model_name": "gpt-test",
            }
        )

        self.assertEqual(client.provider.provider_type, "openai_compatible")
        self.assertTrue(client.provider.capabilities.supports_pipeline)

    def test_cli_provider_is_rejected_for_simulation_config_generator(self):
        llm_client = LLMClient(
            provider=LLMProviderFactory.create({"provider_type": "codex_cli"})
        )

        with self.assertRaises(ValueError):
            SimulationConfigGenerator(llm_client=llm_client)

    def test_cli_provider_is_rejected_for_oasis_profile_generator(self):
        llm_client = LLMClient(
            provider=LLMProviderFactory.create({"provider_type": "claude_code_cli"})
        )

        with self.assertRaises(ValueError):
            OasisProfileGenerator(llm_client=llm_client)

    def test_cli_provider_is_rejected_for_report_agent(self):
        llm_client = LLMClient(
            provider=LLMProviderFactory.create({"provider_type": "codex_cli"})
        )

        with self.assertRaises(ValueError):
            ReportAgent(
                graph_id="graph_123",
                simulation_id="sim_123",
                simulation_requirement="test",
                llm_client=llm_client,
                zep_tools=DummyZepTools(),
            )

    def test_simulation_config_generator_repairs_truncated_json(self):
        llm_client = LLMClient(
            provider=TruncatedJSONProvider('{"reasoning": "partial"')
        )
        generator = SimulationConfigGenerator(llm_client=llm_client)

        result = generator._call_llm_with_retry(
            prompt="return json",
            system_prompt="return json",
        )

        self.assertEqual(result["reasoning"], "partial")

    def test_oasis_profile_generator_repairs_truncated_json(self):
        llm_client = LLMClient(
            provider=TruncatedJSONProvider('{"bio":"Short bio","persona":"Partial persona"')
        )
        generator = OasisProfileGenerator(llm_client=llm_client)

        result = generator._generate_profile_with_llm(
            entity_name="Alice",
            entity_type="Person",
            entity_summary="Leader",
            entity_attributes={},
            context="Scenario context",
        )

        self.assertEqual(result["bio"], "Short bio")
        self.assertEqual(result["persona"], "Partial persona")


if __name__ == "__main__":
    unittest.main()
