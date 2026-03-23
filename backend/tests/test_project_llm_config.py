import os
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.models.project import Project, ProjectStatus
from app.models.project_secrets import ProjectSecretsStore


class TestProjectLLMConfig(unittest.TestCase):
    def test_project_serialization_includes_llm_config(self):
        project = Project(
            project_id="proj_123",
            name="Demo",
            status=ProjectStatus.CREATED,
            created_at="2026-03-23T10:00:00",
            updated_at="2026-03-23T10:05:00",
            llm_config={
                "provider_type": "anthropic",
                "mode": "api",
                "model_name": "claude-sonnet-4-5",
                "api_key_source": "project",
            },
        )

        data = project.to_dict()

        self.assertEqual(data["llm_config"]["provider_type"], "anthropic")
        self.assertEqual(data["llm_config"]["mode"], "api")
        self.assertEqual(data["llm_config"]["model_name"], "claude-sonnet-4-5")
        self.assertNotIn("api_key", data)
        self.assertNotIn("api_key", data["llm_config"])

    def test_project_from_dict_defaults_llm_config_to_none(self):
        project = Project.from_dict(
            {
                "project_id": "proj_legacy",
                "name": "Legacy",
                "status": "created",
                "created_at": "2026-03-23T10:00:00",
                "updated_at": "2026-03-23T10:05:00",
            }
        )

        self.assertIsNone(project.llm_config)

    def test_project_from_dict_preserves_llm_config(self):
        project = Project.from_dict(
            {
                "project_id": "proj_456",
                "name": "Configured",
                "status": "ontology_generated",
                "created_at": "2026-03-23T10:00:00",
                "updated_at": "2026-03-23T10:05:00",
                "llm_config": {
                    "provider_type": "openai",
                    "mode": "api",
                    "model_name": "gpt-5",
                },
            }
        )

        self.assertEqual(project.llm_config["provider_type"], "openai")
        self.assertEqual(project.llm_config["mode"], "api")
        self.assertEqual(project.llm_config["model_name"], "gpt-5")

    def test_project_secrets_store_save_load_mask_delete(self):
        tmp_root = Path(self._testMethodName)
        projects_dir = tmp_root / "projects"
        os.makedirs(projects_dir / "proj_secret", exist_ok=True)
        original_dir = ProjectSecretsStore.PROJECTS_DIR
        ProjectSecretsStore.PROJECTS_DIR = str(projects_dir)
        try:
            result = ProjectSecretsStore.save_project_api_secret(
                "proj_secret",
                provider_type="anthropic",
                api_key="sk-ant-secret-123456",
            )

            secrets_path = Path(ProjectSecretsStore._get_project_secrets_path("proj_secret"))
            self.assertTrue(secrets_path.exists())
            self.assertNotIn("api_key", result)
            self.assertEqual(result["masked_api_key"], "sk-an...3456")

            loaded = ProjectSecretsStore.get_project_api_secret("proj_secret")
            self.assertEqual(loaded["provider_type"], "anthropic")
            self.assertEqual(loaded["api_key"], "sk-ant-secret-123456")
            self.assertEqual(ProjectSecretsStore.mask_secret("sk-ant-secret-123456"), "sk-an...3456")

            ProjectSecretsStore.delete_project_api_secret("proj_secret")
            self.assertIsNone(ProjectSecretsStore.get_project_api_secret("proj_secret"))
            self.assertFalse(secrets_path.exists())
        finally:
            ProjectSecretsStore.PROJECTS_DIR = original_dir
            if tmp_root.exists():
                for path in sorted(tmp_root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()

    def test_project_secrets_store_handles_missing_file(self):
        tmp_root = Path(self._testMethodName)
        original_dir = ProjectSecretsStore.PROJECTS_DIR
        ProjectSecretsStore.PROJECTS_DIR = str(tmp_root / "projects")
        try:
            self.assertIsNone(ProjectSecretsStore.get_project_api_secret("missing"))
        finally:
            ProjectSecretsStore.PROJECTS_DIR = original_dir
            if tmp_root.exists():
                for path in sorted(tmp_root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()

    def test_project_secrets_store_requires_existing_project_dir(self):
        tmp_root = Path(self._testMethodName)
        original_dir = ProjectSecretsStore.PROJECTS_DIR
        ProjectSecretsStore.PROJECTS_DIR = str(tmp_root / "projects")
        try:
            with self.assertRaises(FileNotFoundError):
                ProjectSecretsStore.save_project_api_secret(
                    "missing_project",
                    provider_type="openai",
                    api_key="sk-test",
                )

            self.assertFalse((Path(ProjectSecretsStore.PROJECTS_DIR) / "missing_project").exists())
        finally:
            ProjectSecretsStore.PROJECTS_DIR = original_dir
            if tmp_root.exists():
                for path in sorted(tmp_root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()


if __name__ == "__main__":
    unittest.main()
