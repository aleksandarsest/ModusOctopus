import os
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

from app.models.project import Project, ProjectManager, ProjectStatus


class TestProjectGraphBackend(unittest.TestCase):
    def test_project_serialization_includes_graph_backend(self):
        project = Project(
            project_id="proj_graph",
            name="Graph Project",
            status=ProjectStatus.CREATED,
            created_at="2026-03-23T10:00:00",
            updated_at="2026-03-23T10:05:00",
            graph_backend="local",
        )

        data = project.to_dict()

        self.assertEqual(data["graph_backend"], "local")

    def test_project_from_dict_defaults_to_local_without_legacy_graph(self):
        project = Project.from_dict(
            {
                "project_id": "proj_local",
                "name": "Local Default",
                "status": "created",
                "created_at": "2026-03-23T10:00:00",
                "updated_at": "2026-03-23T10:05:00",
            }
        )

        self.assertEqual(project.graph_backend, "local")

    def test_project_from_dict_infers_zep_for_legacy_graph_project(self):
        project = Project.from_dict(
            {
                "project_id": "proj_legacy_zep",
                "name": "Legacy Zep",
                "status": "graph_completed",
                "created_at": "2026-03-23T10:00:00",
                "updated_at": "2026-03-23T10:05:00",
                "graph_id": "graph_123",
            }
        )

        self.assertEqual(project.graph_backend, "zep")

    def test_create_project_defaults_to_local_backend(self):
        tmp_root = Path(self._testMethodName)
        original_dir = ProjectManager.PROJECTS_DIR
        ProjectManager.PROJECTS_DIR = str(tmp_root / "projects")
        try:
            project = ProjectManager.create_project(name="Local First")

            self.assertEqual(project.graph_backend, "local")

            reloaded = ProjectManager.get_project(project.project_id)
            self.assertIsNotNone(reloaded)
            self.assertEqual(reloaded.graph_backend, "local")
        finally:
            ProjectManager.PROJECTS_DIR = original_dir
            if tmp_root.exists():
                for path in sorted(tmp_root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()

    def test_create_project_preserves_explicit_backend(self):
        tmp_root = Path(self._testMethodName)
        original_dir = ProjectManager.PROJECTS_DIR
        ProjectManager.PROJECTS_DIR = str(tmp_root / "projects")
        try:
            project = ProjectManager.create_project(name="Zep Project", graph_backend="zep")

            self.assertEqual(project.graph_backend, "zep")

            reloaded = ProjectManager.get_project(project.project_id)
            self.assertIsNotNone(reloaded)
            self.assertEqual(reloaded.graph_backend, "zep")
        finally:
            ProjectManager.PROJECTS_DIR = original_dir
            if tmp_root.exists():
                for path in sorted(tmp_root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()

    def test_find_project_by_graph_id_returns_matching_project(self):
        tmp_root = Path(self._testMethodName)
        original_dir = ProjectManager.PROJECTS_DIR
        ProjectManager.PROJECTS_DIR = str(tmp_root / "projects")
        try:
            project = ProjectManager.create_project(name="Find Me", graph_backend="local")
            project.graph_id = "local_graph_123"
            ProjectManager.save_project(project)

            found = ProjectManager.find_project_by_graph_id("local_graph_123")

            self.assertIsNotNone(found)
            self.assertEqual(found.project_id, project.project_id)
            self.assertEqual(found.graph_backend, "local")
        finally:
            ProjectManager.PROJECTS_DIR = original_dir
            if tmp_root.exists():
                for path in sorted(tmp_root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()


if __name__ == "__main__":
    unittest.main()
