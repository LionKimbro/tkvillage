from __future__ import annotations

from pathlib import Path


def resolve_project_dir_path(project_dir_name=".tkvillage", project_root=None):
    root = Path.cwd() if project_root is None else Path(project_root)
    return (root / project_dir_name).resolve()


def ensure_lionscliapp_tkvillage_dir():
    from lionscliapp.paths import get_project_root

    host_project_dir = get_project_root()
    project_dir = host_project_dir / "tkvillage"
    project_dir.mkdir(parents=True, exist_ok=True)
    return host_project_dir, project_dir
