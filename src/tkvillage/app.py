from __future__ import annotations

from pathlib import Path
import time

from .project_dir import resolve_project_dir


DEFAULT_TICK_INTERVAL_MS = 50


app = {}


def reset_app():
    """Reset the single TkVillage runtime dictionary for tests and fresh launches."""
    root = app.get("root")
    if root is not None:
        try:
            root.destroy()
        except Exception:
            pass
    app.clear()
    app.update(
        {
            "name": "tkvillage",
            "root": None,
            "project_dir": None,
            "config": {"declarations": {}, "values": {}},
            "window_kinds": {},
            "windows": {},
            "windows_by_instance_key": {},
            "targets": {},
            "runtime_objects": {},
            "event_log": [],
            "effect_log": [],
            "message_log": [],
            "runtime_log": [],
            "worker_records": {},
            "debug": {"enabled": False, "last_snapshot": None},
            "is_running": False,
            "test_mode": False,
            "strict_effects": False,
            "tick_interval_ms": DEFAULT_TICK_INTERVAL_MS,
            "tick_after_id": None,
            "tick_count": 0,
            "created_at": time.time(),
            "id_counters": {},
            "max_log_entries": 200,
        }
    )
    return app


def get_app():
    return app


def create_app(
    name="tkvillage",
    project_dir_name=".tkvillage",
    project_root=None,
    tick_interval_ms=DEFAULT_TICK_INTERVAL_MS,
    test_mode=False,
    create_root=True,
):
    """Create the global runtime and, by default, the hidden Tk root."""
    reset_app()
    app["name"] = name
    app["project_dir"] = resolve_project_dir(project_dir_name, project_root)
    app["tick_interval_ms"] = int(tick_interval_ms)
    app["test_mode"] = bool(test_mode)
    app["is_running"] = True

    if create_root:
        from .root import ensure_root

        ensure_root()

    from .config import load_config
    from .debug import install_debug_shortcut, register_debug_windows

    load_config()
    register_debug_windows()
    if app["root"] is not None:
        install_debug_shortcut()
    return app


def next_id(prefix):
    counters = app["id_counters"]
    counters[prefix] = counters.get(prefix, 0) + 1
    return f"{prefix}-{counters[prefix]}"


def append_log(name, item):
    log = app[name]
    log.append(item)
    del log[: max(0, len(log) - app["max_log_entries"])]


def run():
    from .root import ensure_root
    from .tick import start_tick_loop

    root = ensure_root()
    start_tick_loop()
    root.mainloop()


def shutdown():
    from .tick import stop_tick_loop

    stop_tick_loop()
    for window_id in list(app["windows"]):
        from .windows import destroy_window

        destroy_window(window_id)
    root = app.get("root")
    if root is not None:
        try:
            root.destroy()
        except Exception:
            pass
        app["root"] = None
    app["is_running"] = False


reset_app()
