from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from core.utils.docs_repo import DOCS_REPO_BRANCH, ensure_docs_repo_synced, fast_forward_docs_repo

PIP_PACKAGE_TARGET = "git+https://github.com/dev0xx1/autoquant-cli.git@main"


def _workspace_path() -> Path:
    workspace_value = os.getenv("AUTOQUANT_WORKSPACE", "").strip()
    if not workspace_value:
        raise RuntimeError("AUTOQUANT_WORKSPACE is required for run-update")
    workspace_path = Path(workspace_value).expanduser()
    if not workspace_path.is_absolute():
        raise RuntimeError("AUTOQUANT_WORKSPACE must be an absolute path")
    workspace_path.mkdir(parents=True, exist_ok=True)
    return workspace_path


def run_update() -> dict[str, Any]:
    sync_before = ensure_docs_repo_synced()
    workspace_path = _workspace_path()
    pip_path = workspace_path / "venv" / "autoquant" / "bin" / "pip"
    if not pip_path.exists():
        raise RuntimeError(f"Pip executable not found: {pip_path}")
    command = [str(pip_path), "install", "--upgrade", "--force-reinstall", PIP_PACKAGE_TARGET]
    pip_result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if pip_result.returncode != 0:
        stderr = (pip_result.stderr or "").strip()
        stdout = (pip_result.stdout or "").strip()
        details = "\n".join([part for part in [stderr, stdout] if part])
        raise RuntimeError(f"Update failed for command: {' '.join(command)}\n{details}".strip())
    sync_after = ensure_docs_repo_synced()
    repo_dir = Path(sync_after["repo_dir"])
    advanced_docs_repo = False
    docs_repo_head = sync_after["baseline_commit"]
    if sync_after["baseline_commit"] != sync_after["latest_commit"]:
        docs_repo_head = fast_forward_docs_repo(repo_dir, branch=DOCS_REPO_BRANCH)
        advanced_docs_repo = True
    return {
        "command": command,
        "exit_code": pip_result.returncode,
        "stdout": pip_result.stdout,
        "stderr": pip_result.stderr,
        "docs_repo_dir": sync_after["repo_dir"],
        "docs_repo_branch": sync_after["branch"],
        "docs_repo_commit_before_update": sync_before["baseline_commit"],
        "docs_repo_commit_before_fast_forward": sync_after["baseline_commit"],
        "docs_repo_latest_commit": sync_after["latest_commit"],
        "docs_repo_head_after_update": docs_repo_head,
        "docs_repo_advanced": advanced_docs_repo,
    }
