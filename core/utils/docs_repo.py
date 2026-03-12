from __future__ import annotations

import subprocess
from pathlib import Path

from core.paths import workspace_root

DOCS_REPO_URL = "https://github.com/dev0xx1/autoquant.git"
DOCS_REPO_BRANCH = "main"
DOCS_REPO_DIRNAME = "autoquant-docs"


def docs_repo_dir() -> Path:
    return workspace_root() / DOCS_REPO_DIRNAME


def _run_git(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *command],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _run_git_checked(command: list[str], cwd: Path | None = None, label: str = "git command") -> subprocess.CompletedProcess[str]:
    result = _run_git(command, cwd=cwd)
    if result.returncode == 0:
        return result
    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()
    details = "\n".join([part for part in [stderr, stdout] if part])
    raise RuntimeError(f"{label} failed: {' '.join(command)}\n{details}".strip())


def _rev_parse(repo_dir: Path, ref: str) -> str:
    result = _run_git_checked(["rev-parse", ref], cwd=repo_dir, label="git rev-parse")
    value = result.stdout.strip()
    if not value:
        raise RuntimeError(f"Empty git ref value for {ref}")
    return value


def ensure_docs_repo_synced(repo_url: str = DOCS_REPO_URL, branch: str = DOCS_REPO_BRANCH) -> dict[str, str]:
    repo_dir = docs_repo_dir()
    if repo_dir.exists() and not repo_dir.is_dir():
        raise RuntimeError(f"Docs repo path exists but is not a directory: {repo_dir}")
    if not repo_dir.exists():
        repo_dir.parent.mkdir(parents=True, exist_ok=True)
        clone_result = _run_git(
            ["clone", "--branch", branch, "--single-branch", repo_url, str(repo_dir)],
            cwd=repo_dir.parent,
        )
        if clone_result.returncode != 0:
            stderr = (clone_result.stderr or "").strip()
            stdout = (clone_result.stdout or "").strip()
            details = "\n".join([part for part in [stderr, stdout] if part])
            raise RuntimeError(f"Unable to clone docs repository into {repo_dir}\n{details}".strip())
    if not (repo_dir / ".git").exists():
        raise RuntimeError(f"Docs repo directory is not a git clone: {repo_dir}")
    _run_git_checked(["fetch", "origin", branch], cwd=repo_dir, label="git fetch")
    baseline_commit = _rev_parse(repo_dir, "HEAD")
    latest_commit = _rev_parse(repo_dir, f"origin/{branch}")
    return {
        "repo_dir": str(repo_dir),
        "repo_url": repo_url,
        "branch": branch,
        "baseline_commit": baseline_commit,
        "latest_commit": latest_commit,
    }


def diff_file_between_refs(repo_dir: Path, baseline_commit: str, latest_commit: str, rel_path: str) -> str:
    result = _run_git_checked(
        ["diff", "--unified=3", baseline_commit, latest_commit, "--", rel_path],
        cwd=repo_dir,
        label="git diff",
    )
    return result.stdout


def fast_forward_docs_repo(repo_dir: Path, branch: str = DOCS_REPO_BRANCH) -> str:
    _run_git_checked(["checkout", branch], cwd=repo_dir, label="git checkout")
    _run_git_checked(["merge", "--ff-only", f"origin/{branch}"], cwd=repo_dir, label="git merge --ff-only")
    return _rev_parse(repo_dir, "HEAD")
