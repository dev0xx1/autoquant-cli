from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from core.paths import workspace_root
from core.utils.docs_repo import DOCS_REPO_DIRNAME

DATA_PATHS = ("runs", "tmp", DOCS_REPO_DIRNAME)


def _delete_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
        return
    path.unlink()


def clear_data() -> dict[str, Any]:
    root = workspace_root()
    deleted: list[str] = []
    missing: list[str] = []
    for rel_path in DATA_PATHS:
        target = root / rel_path
        if not target.exists():
            missing.append(rel_path)
            continue
        _delete_path(target)
        deleted.append(rel_path)
    return {
        "workspace": str(root),
        "deleted": deleted,
        "missing": missing,
    }
