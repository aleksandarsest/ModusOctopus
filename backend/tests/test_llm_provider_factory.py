import sys
import types
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if "flask" not in sys.modules:
    flask_stub = types.ModuleType("flask")

    class _Flask:  # pragma: no cover - import stub only
        def __init__(self, *args, **kwargs):
            pass

    flask_stub.Flask = _Flask
    flask_stub.request = object()
    sys.modules["flask"] = flask_stub

if "flask_cors" not in sys.modules:
    flask_cors_stub = types.ModuleType("flask_cors")

    def _cors(*args, **kwargs):  # pragma: no cover - import stub only
        return None

    flask_cors_stub.CORS = _cors
    sys.modules["flask_cors"] = flask_cors_stub

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

from app.config import Config
from app.llm.capabilities import API_PROVIDER_CAPABILITIES, CLI_PROVIDER_CAPABILITIES
from app.llm.factory import LLMProviderFactory
from app.llm.providers.anthropic_provider import AnthropicProvider
from app.llm.providers.claude_code_cli import ClaudeCodeCLIProvider
from app.llm.providers.codex_cli import CodexCLIProvider
from app.llm.providers.openai_compatible import OpenAICompatibleProvider
from app.llm.providers.openai_native import OpenAINativeProvider
from app.llm.providers.base import BaseLLMProvider, LLMChatResult
from app.utils.llm_client import LLMClient


class DummyJSONProvider(BaseLLMProvider):
    provider_type = "dummy_json"
    mode = "api"

    def __init__(self):
        self.last_response_format = None

    @property
    def capabilities(self):
        return API_PROVIDER_CAPABILITIES

    def healthcheck(self):
        return {"ok": True, "provider_type": self.provider_type, "mode": self.mode}

    def chat_with_metadata(self, messages, temperature=0.7, max_tokens=4096, response_format=None):
        self.last_response_format = response_format
        return LLMChatResult(content='{"ok": true}', finish_reason="stop")


class TestLLMProviderFactory(unittest.TestCase):
    def test_factory_returns_api_providers_with_pipeline_support(self):
        openai_compatible = LLMProviderFactory.create(
            {
                "provider_type": "openai_compatible",
                "api_key": "test-key",
                "base_url": "https://example.com/v1",
                "model_name": "gpt-test",
            }
        )
        self.assertIsInstance(openai_compatible, OpenAICompatibleProvider)
        self.assertEqual(openai_compatible.capabilities, API_PROVIDER_CAPABILITIES)

        openai_native = LLMProviderFactory.create(
            {
                "provider_type": "openai",
                "api_key": "test-key",
                "model_name": "gpt-test",
            }
        )
        self.assertIsInstance(openai_native, OpenAINativeProvider)
        self.assertEqual(openai_native.capabilities, API_PROVIDER_CAPABILITIES)

        anthropic = LLMProviderFactory.create(
            {
                "provider_type": "anthropic",
                "api_key": "test-key",
                "model_name": "claude-test",
            }
        )
        self.assertIsInstance(anthropic, AnthropicProvider)
        self.assertEqual(anthropic.capabilities, API_PROVIDER_CAPABILITIES)

        self.assertTrue(openai_compatible.capabilities.supports_pipeline)
        self.assertTrue(openai_compatible.capabilities.supports_refinement)
        self.assertTrue(openai_compatible.capabilities.supports_chat_json)

    def test_factory_returns_cli_providers_with_pipeline_support(self):
        codex = LLMProviderFactory.create({"provider_type": "codex_cli"})
        self.assertIsInstance(codex, CodexCLIProvider)
        self.assertEqual(codex.capabilities, CLI_PROVIDER_CAPABILITIES)
        self.assertTrue(codex.capabilities.supports_pipeline)
        self.assertTrue(codex.capabilities.supports_refinement)
        self.assertTrue(codex.capabilities.supports_chat_json)

        claude = LLMProviderFactory.create({"provider_type": "claude_code_cli"})
        self.assertIsInstance(claude, ClaudeCodeCLIProvider)
        self.assertEqual(claude.capabilities, CLI_PROVIDER_CAPABILITIES)
        self.assertTrue(claude.capabilities.supports_pipeline)
        self.assertTrue(claude.capabilities.supports_refinement)

    def test_cli_healthcheck_reports_missing_executable_cleanly(self):
        provider = CodexCLIProvider(executable="definitely-not-installed-executable-12345")
        health = provider.healthcheck()

        self.assertFalse(health["ok"])
        self.assertEqual(health["status"], "missing_executable")
        self.assertEqual(health["provider_type"], "codex_cli")
        self.assertEqual(health["mode"], "cli")
        self.assertIn("not found", health["message"])
        self.assertTrue(health["supports_pipeline"])
        self.assertTrue(health["supports_refinement"])

    def test_base_chat_json_does_not_force_openai_response_format(self):
        provider = DummyJSONProvider()
        result = provider.chat_json([{"role": "user", "content": "return json"}])

        self.assertEqual(result, {"ok": True})
        self.assertIsNone(provider.last_response_format)

    def test_anthropic_requires_explicit_api_key(self):
        with self.assertRaises(ValueError):
            AnthropicProvider(api_key=None, model_name="claude-test")

    def test_factory_does_not_fall_back_to_generic_openai_key_for_anthropic(self):
        with self.assertRaises(ValueError):
            LLMProviderFactory.create({"provider_type": "anthropic", "model_name": "claude-test"})

    def test_llm_client_does_not_fall_back_to_global_key_for_anthropic_project_config(self):
        original_global_key = Config.LLM_API_KEY
        Config.LLM_API_KEY = "global-openai-key"
        try:
            with self.assertRaises(ValueError):
                LLMClient(
                    provider_config={
                        "provider_type": "anthropic",
                        "model_name": "claude-test",
                    }
                )
        finally:
            Config.LLM_API_KEY = original_global_key

    def test_llm_client_chat_json_works_with_anthropic_provider(self):
        client = LLMClient(
            provider_config={
                "provider_type": "anthropic",
                "api_key": "anthropic-test-key",
                "model_name": "claude-test",
            }
        )

        response = client.chat_json([{"role": "user", "content": "return json"}])

        self.assertEqual(response, {"ok": True})

    def test_unknown_provider_type_raises(self):
        with self.assertRaises(ValueError):
            LLMProviderFactory.create({"provider_type": "unknown"})


if __name__ == "__main__":
    unittest.main()
