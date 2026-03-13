from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.commands.pull_docs import pull_docs


class PullDocsTests(unittest.TestCase):
    def test_pull_docs_fast_forwards_when_behind(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sync_state = {
                "repo_dir": str(Path(temp_dir) / "autoquant-docs"),
                "repo_url": "https://github.com/dev0xx1/autoquant.git",
                "branch": "main",
                "baseline_commit": "old_head",
                "latest_commit": "new_head",
            }
            with patch("core.commands.pull_docs.ensure_docs_repo_synced", return_value=sync_state):
                with patch("core.commands.pull_docs.fast_forward_docs_repo", return_value="new_head"):
                    result = pull_docs()
        self.assertTrue(result["updated"])
        self.assertEqual(result["head_after_pull"], "new_head")

    def test_pull_docs_noop_when_up_to_date(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sync_state = {
                "repo_dir": str(Path(temp_dir) / "autoquant-docs"),
                "repo_url": "https://github.com/dev0xx1/autoquant.git",
                "branch": "main",
                "baseline_commit": "same_head",
                "latest_commit": "same_head",
            }
            with patch("core.commands.pull_docs.ensure_docs_repo_synced", return_value=sync_state):
                with patch("core.commands.pull_docs.fast_forward_docs_repo") as ff_mock:
                    result = pull_docs()
        self.assertFalse(result["updated"])
        self.assertEqual(result["head_after_pull"], "same_head")
        ff_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
