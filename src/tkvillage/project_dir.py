from __future__ import annotations

from pathlib import Path


def resolve_project_dir(project_dir_name=".tkvillage", project_root=None):
    root = Path.cwd() if project_root is None else Path(project_root)
    project_dir = root / project_dir_name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir.resolve()
