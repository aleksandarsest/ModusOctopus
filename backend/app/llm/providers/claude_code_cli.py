"""
Claude Code CLI provider.
"""

from __future__ import annotations

import subprocess
import shutil
from typing import Any, Dict, List, Optional

from ...config import Config
from ..capabilities import CLI_PROVIDER_CAPABILITIES, LLMCapabilities
from .base import BaseLLMProvider, LLMChatResult


class ClaudeCodeCLIProvider(BaseLLMProvider):
    provider_type = "claude_code_cli"
    mode = "cli"

    def __init__(self, executable: str = "claude", working_directory: Optional[str] = None):
        self.executable = executable
        self.working_directory = working_directory

    @property
    def capabilities(self) -> LLMCapabilities:
        return CLI_PROVIDER_CAPABILITIES

    def _run_cli(self, prompt: str) -> str:
        command = [
            self.executable,
            "-p",
            "--output-format",
            "text",
            "--permission-mode",
            "dontAsk",
            "--tools",
            "",
            prompt,
        ]
        if self.working_directory:
            command[1:1] = ["--add-dir", self.working_directory]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=Config.CLI_PROVIDER_TIMEOUT_SECONDS,
                cwd=self.working_directory or None,
                check=True,
            )
        except FileNotFoundError as exc:
            raise ValueError(f"Executable '{self.executable}' was not found on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise ValueError("Claude Code CLI timed out while executing the request") from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            raise ValueError(stderr or "Claude Code CLI request failed") from exc

        return (result.stdout or "").strip()

    def chat_with_metadata(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMChatResult:
        del temperature, max_tokens, response_format
        prompt = "\n\n".join(
            f"{message.get('role', 'user').upper()}:\n{message.get('content', '')}"
            for message in messages
        )
        content = self._run_cli(prompt)
        return LLMChatResult(content=content, finish_reason="stop")

    def healthcheck(self) -> Dict[str, Any]:
        executable_path = shutil.which(self.executable)
        if not executable_path:
            return {
                "ok": False,
                "provider_type": self.provider_type,
                "mode": self.mode,
                "executable": self.executable,
                "status": "missing_executable",
                "message": f"Executable '{self.executable}' was not found on PATH",
                "supports_pipeline": self.capabilities.supports_pipeline,
                "supports_refinement": self.capabilities.supports_refinement,
            }
        return {
            "ok": True,
            "provider_type": self.provider_type,
            "mode": self.mode,
            "executable": self.executable,
            "executable_path": executable_path,
            "status": "available",
            "supports_pipeline": self.capabilities.supports_pipeline,
            "supports_refinement": self.capabilities.supports_refinement,
        }

    def refine_brief(self, brief_input: Any) -> Dict[str, Any]:
        prompt = (
            "Rewrite the following ModusOctopus simulation brief into a clearer, more concrete "
            "business scenario brief. Do not use tools. Reply with plain text only.\n\n"
            f"{self._brief_input_to_text(brief_input)}"
        )
        return {
            "provider_type": self.provider_type,
            "mode": self.mode,
            "refined_brief": self._run_cli(prompt),
        }
