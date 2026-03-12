from __future__ import annotations

from pathlib import Path
from typing import Any

from core.utils.docs_repo import diff_file_between_refs, ensure_docs_repo_synced

UPDATE_FILES = ("README.md", "UPDATE.md")


def get_update_diffs() -> dict[str, Any]:
    sync_state = ensure_docs_repo_synced()
    repo_dir = Path(sync_state["repo_dir"])
    baseline_commit = sync_state["baseline_commit"]
    latest_commit = sync_state["latest_commit"]
    file_diffs: list[dict[str, Any]] = []
    for rel_path in UPDATE_FILES:
        diff_text = diff_file_between_refs(repo_dir, baseline_commit, latest_commit, rel_path)
        file_diffs.append(
            {
                "path": rel_path,
                "changed": bool(diff_text.strip()),
                "diff": diff_text,
            }
        )
    return {
        "repo_url": sync_state["repo_url"],
        "repo_dir": sync_state["repo_dir"],
        "branch": sync_state["branch"],
        "baseline_commit": baseline_commit,
        "latest_commit": latest_commit,
        "has_changes": any(item["changed"] for item in file_diffs),
        "files": file_diffs,
    }
