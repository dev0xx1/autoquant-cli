from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from core.commands.clear_data import clear_data


class ClearDataTests(unittest.TestCase):
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

    def test_clear_data_deletes_known_workspace_paths(self) -> None:
        workspace = Path(self.temp_dir.name)
        (workspace / "runs" / "r1").mkdir(parents=True, exist_ok=True)
        (workspace / "tmp" / "r1").mkdir(parents=True, exist_ok=True)
        (workspace / "autoquant-docs").mkdir(parents=True, exist_ok=True)
        result = clear_data()
        self.assertEqual(sorted(result["deleted"]), ["autoquant-docs", "runs", "tmp"])
        self.assertEqual(result["missing"], [])
        self.assertFalse((workspace / "runs").exists())
        self.assertFalse((workspace / "tmp").exists())
        self.assertFalse((workspace / "autoquant-docs").exists())

    def test_clear_data_reports_missing_paths(self) -> None:
        result = clear_data()
        self.assertEqual(result["deleted"], [])
        self.assertEqual(sorted(result["missing"]), ["autoquant-docs", "runs", "tmp"])


if __name__ == "__main__":
    unittest.main()
