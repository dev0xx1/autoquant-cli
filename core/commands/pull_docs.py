from __future__ import annotations

from pathlib import Path
from typing import Any

from core.utils.docs_repo import DOCS_REPO_BRANCH, ensure_docs_repo_synced, fast_forward_docs_repo


def pull_docs() -> dict[str, Any]:
    sync_state = ensure_docs_repo_synced()
    repo_dir = Path(sync_state["repo_dir"])
    baseline_commit = sync_state["baseline_commit"]
    latest_commit = sync_state["latest_commit"]
    head_after_pull = baseline_commit
    updated = False
    if baseline_commit != latest_commit:
        head_after_pull = fast_forward_docs_repo(repo_dir, branch=DOCS_REPO_BRANCH)
        updated = True
    return {
        "repo_url": sync_state["repo_url"],
        "repo_dir": sync_state["repo_dir"],
        "branch": sync_state["branch"],
        "baseline_commit": baseline_commit,
        "latest_commit": latest_commit,
        "head_after_pull": head_after_pull,
        "updated": updated,
    }
