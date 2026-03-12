from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.commands.get_update_diffs import get_update_diffs


class GetUpdateDiffsTests(unittest.TestCase):
    def test_get_update_diffs_returns_expected_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "autoquant-docs"
            repo_dir.mkdir(parents=True, exist_ok=True)
            sync_state = {
                "repo_url": "https://github.com/dev0xx1/autoquant.git",
                "repo_dir": str(repo_dir),
                "branch": "main",
                "baseline_commit": "abc",
                "latest_commit": "def",
            }

            def fake_diff(repo: Path, baseline: str, latest: str, rel_path: str) -> str:
                if rel_path == "README.md":
                    return "--- a/README.md\n+++ b/README.md\n"
                return ""

            with patch("core.commands.get_update_diffs.ensure_docs_repo_synced", return_value=sync_state):
                with patch("core.commands.get_update_diffs.diff_file_between_refs", side_effect=fake_diff):
                    result = get_update_diffs()

        self.assertEqual(result["baseline_commit"], "abc")
        self.assertEqual(result["latest_commit"], "def")
        self.assertTrue(result["has_changes"])
        self.assertEqual(len(result["files"]), 2)
        changed_paths = [item["path"] for item in result["files"] if item["changed"]]
        self.assertEqual(changed_paths, ["README.md"])


if __name__ == "__main__":
    unittest.main()
