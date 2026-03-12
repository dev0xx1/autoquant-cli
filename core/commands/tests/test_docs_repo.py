from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.utils.docs_repo import ensure_docs_repo_synced


class DocsRepoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_workspace = os.environ.get("AUTOQUANT_WORKSPACE")
        os.environ["AUTOQUANT_WORKSPACE"] = self.temp_dir.name

    def tearDown(self) -> None:
        if self.original_workspace is None:
            os.environ.pop("AUTOQUANT_WORKSPACE", None)
        else:
            os.environ["AUTOQUANT_WORKSPACE"] = self.original_workspace
        self.temp_dir.cleanup()

    def test_ensure_docs_repo_synced_clones_when_missing(self) -> None:
        def fake_run(
            command: list[str],
            cwd: Path | None = None,
            capture_output: bool = True,
            text: bool = True,
            check: bool = False,
        ) -> subprocess.CompletedProcess[str]:
            if command[1] == "clone":
                repo_dir = Path(command[-1])
                repo_dir.mkdir(parents=True, exist_ok=True)
                (repo_dir / ".git").mkdir(parents=True, exist_ok=True)
                return subprocess.CompletedProcess(command, 0, "", "")
            if command[1] == "fetch":
                return subprocess.CompletedProcess(command, 0, "", "")
            if command[1] == "rev-parse":
                if command[2] == "HEAD":
                    return subprocess.CompletedProcess(command, 0, "abc123\n", "")
                return subprocess.CompletedProcess(command, 0, "def456\n", "")
            return subprocess.CompletedProcess(command, 0, "", "")

        with patch("core.utils.docs_repo.subprocess.run", side_effect=fake_run):
            result = ensure_docs_repo_synced()
        self.assertEqual(result["baseline_commit"], "abc123")
        self.assertEqual(result["latest_commit"], "def456")
        self.assertTrue((Path(result["repo_dir"]) / ".git").exists())

    def test_ensure_docs_repo_synced_fetches_existing_clone(self) -> None:
        repo_dir = Path(self.temp_dir.name) / "autoquant-docs"
        repo_dir.mkdir(parents=True, exist_ok=True)
        (repo_dir / ".git").mkdir(parents=True, exist_ok=True)

        def fake_run(
            command: list[str],
            cwd: Path | None = None,
            capture_output: bool = True,
            text: bool = True,
            check: bool = False,
        ) -> subprocess.CompletedProcess[str]:
            if command[1] == "clone":
                return subprocess.CompletedProcess(command, 1, "", "clone should not run")
            if command[1] == "fetch":
                return subprocess.CompletedProcess(command, 0, "", "")
            if command[1] == "rev-parse":
                if command[2] == "HEAD":
                    return subprocess.CompletedProcess(command, 0, "111111\n", "")
                return subprocess.CompletedProcess(command, 0, "222222\n", "")
            return subprocess.CompletedProcess(command, 0, "", "")

        with patch("core.utils.docs_repo.subprocess.run", side_effect=fake_run):
            result = ensure_docs_repo_synced()
        self.assertEqual(result["baseline_commit"], "111111")
        self.assertEqual(result["latest_commit"], "222222")

    def test_ensure_docs_repo_synced_raises_when_path_is_not_directory(self) -> None:
        repo_file = Path(self.temp_dir.name) / "autoquant-docs"
        repo_file.write_text("x", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            ensure_docs_repo_synced()


if __name__ == "__main__":
    unittest.main()
