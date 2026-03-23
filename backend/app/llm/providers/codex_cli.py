"""
Codex CLI provider.
"""

from __future__ import annotations

import subprocess
import shutil
from typing import Any, Dict, Optional

from ...config import Config
from ..capabilities import CLI_PROVIDER_CAPABILITIES, LLMCapabilities
from .base import BaseLLMProvider


class CodexCLIProvider(BaseLLMProvider):
    provider_type = "codex_cli"
    mode = "cli"

    def __init__(self, executable: str = "codex", working_directory: Optional[str] = None):
        self.executable = executable
        self.working_directory = working_directory

    @property
    def capabilities(self) -> LLMCapabilities:
        return CLI_PROVIDER_CAPABILITIES

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
            "Rewrite the following MiroFish simulation brief into a clearer, more concrete "
            "business scenario brief. Do not use tools. Reply with plain text only.\n\n"
            f"{self._brief_input_to_text(brief_input)}"
        )
        command = [
            self.executable,
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--color",
            "never",
            prompt,
        ]
        if self.working_directory:
            command[2:2] = ["-C", self.working_directory]

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
            raise ValueError("Codex CLI timed out while refining the brief") from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            raise ValueError(stderr or "Codex CLI failed to refine the brief") from exc

        return {
            "provider_type": self.provider_type,
            "mode": self.mode,
            "refined_brief": (result.stdout or "").strip(),
        }
