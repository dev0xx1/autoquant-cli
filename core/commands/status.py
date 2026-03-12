from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _required_env_vars() -> list[str]:
    env_example = Path(__file__).resolve().parent.parent.parent / ".env.example"
    if not env_example.exists():
        return []
    required: list[str] = []
    for raw_line in env_example.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            required.append(key)
    return required


def _is_configured(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered:
        return False
    if lowered.startswith("your_"):
        return False
    if lowered in {"changeme", "replace_me", "todo"}:
        return False
    return True


def status() -> dict[str, Any]:
    required = _required_env_vars()
    env_values = {key: os.getenv(key, "") for key in required}
    env_ok = {key: _is_configured(value) for key, value in env_values.items()}
    missing = [key for key, configured in env_ok.items() if not configured]
    provided = [key for key, configured in env_ok.items() if configured]
    workspace_value = os.getenv("AUTOQUANT_WORKSPACE", "").strip()
    workspace_path = Path(workspace_value).expanduser() if workspace_value else None
    ws_exists = bool(workspace_path and workspace_path.is_absolute() and workspace_path.is_dir())
    workspace_status = "created" if ws_exists else "absent"
    return {
        "missing_env_vars": missing,
        "provided_env_vars": provided,
        "workspace_status": workspace_status,
    }
