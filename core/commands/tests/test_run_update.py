from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.commands.run_update import run_update


class RunUpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_workspace = os.environ.get("AUTOQUANT_WORKSPACE")
        os.environ["AUTOQUANT_WORKSPACE"] = self.temp_dir.name
        self.pip_path = Path(self.temp_dir.name) / "venv" / "autoquant" / "bin" / "pip"
        self.pip_path.parent.mkdir(parents=True, exist_ok=True)
        self.pip_path.write_text("", encoding="utf-8")

    def tearDown(self) -> None:
        if self.original_workspace is None:
            os.environ.pop("AUTOQUANT_WORKSPACE", None)
        else:
            os.environ["AUTOQUANT_WORKSPACE"] = self.original_workspace
        self.temp_dir.cleanup()

    def test_run_update_success_advances_docs_repo(self) -> None:
        sync_before = {
            "repo_dir": str(Path(self.temp_dir.name) / "autoquant-docs"),
            "repo_url": "https://github.com/dev0xx1/autoquant.git",
            "branch": "main",
            "baseline_commit": "old_head",
            "latest_commit": "new_head",
        }
        sync_after = {
            "repo_dir": str(Path(self.temp_dir.name) / "autoquant-docs"),
            "repo_url": "https://github.com/dev0xx1/autoquant.git",
            "branch": "main",
            "baseline_commit": "old_head",
            "latest_commit": "new_head",
        }
        with patch("core.commands.run_update.ensure_docs_repo_synced", side_effect=[sync_before, sync_after]):
            with patch(
                "core.commands.run_update.subprocess.run",
                return_value=subprocess.CompletedProcess(["pip"], 0, "ok", ""),
            ):
                with patch("core.commands.run_update.fast_forward_docs_repo", return_value="new_head"):
                    result = run_update()
        self.assertEqual(result["exit_code"], 0)
        self.assertTrue(result["docs_repo_advanced"])
        self.assertEqual(result["docs_repo_head_after_update"], "new_head")

    def test_run_update_raises_when_pip_fails(self) -> None:
        sync = {
            "repo_dir": str(Path(self.temp_dir.name) / "autoquant-docs"),
            "repo_url": "https://github.com/dev0xx1/autoquant.git",
            "branch": "main",
            "baseline_commit": "a",
            "latest_commit": "b",
        }
        with patch("core.commands.run_update.ensure_docs_repo_synced", return_value=sync):
            with patch(
                "core.commands.run_update.subprocess.run",
                return_value=subprocess.CompletedProcess(["pip"], 1, "out", "err"),
            ):
                with self.assertRaises(RuntimeError):
                    run_update()


if __name__ == "__main__":
    unittest.main()
