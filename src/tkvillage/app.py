from __future__ import annotations

import time

from .project_dir import resolve_project_dir


DEFAULT_TICK_INTERVAL_MS = 50


g = {}
config_declarations = {}
config_values = {}
window_kinds = {}
windows = {}
windows_by_instance_key = {}
targets = {}
runtime_objects = {}
event_log = []
effect_log = []
message_log = []
runtime_log = []
worker_records = {}
debug = {}
id_counters = {}


def reset_app():
    """Reset runtime globals while preserving container identities."""
    old_root = g.get("root")
    if old_root is not None:
        try:
            old_root.destroy()
        except Exception:
            pass

    g.clear()
    g.update(
        {
            "name": "tkvillage",
            "root": None,
            "project_dir": None,
            "is_running": False,
            "test_mode": False,
            "strict_effects": False,
            "tick_interval_ms": DEFAULT_TICK_INTERVAL_MS,
            "tick_after_id": None,
            "tick_count": 0,
            "created_at": time.time(),
            "max_log_entries": 200,
        }
    )
    config_declarations.clear()
    config_values.clear()
    window_kinds.clear()
    windows.clear()
    windows_by_instance_key.clear()
    targets.clear()
    runtime_objects.clear()
    event_log.clear()
    effect_log.clear()
    message_log.clear()
    runtime_log.clear()
    worker_records.clear()
    debug.clear()
    debug.update({"enabled": False, "last_snapshot": None})
    id_counters.clear()
    return g


def create_app(
    name="tkvillage",
    project_dir_name=".tkvillage",
    project_root=None,
    tick_interval_ms=DEFAULT_TICK_INTERVAL_MS,
    test_mode=False,
    create_root=True,
):
    """Create the runtime and, by default, the hidden Tk root."""
    reset_app()
    set_runtime_identity(name, tick_interval_ms, test_mode)
    g["project_dir"] = resolve_project_dir(project_dir_name, project_root)

    if create_root:
        from .root import ensure_root

        ensure_root()

    from .config import load_config
    from .debug import install_debug_shortcut, register_debug_windows

    load_config()
    register_debug_windows()
    if g["root"] is not None:
        install_debug_shortcut()
    return g


def set_runtime_identity(new_name, new_tick_interval_ms, new_test_mode):
    g["name"] = new_name
    g["tick_interval_ms"] = int(new_tick_interval_ms)
    g["test_mode"] = bool(new_test_mode)
    g["is_running"] = True


def next_id(prefix):
    id_counters[prefix] = id_counters.get(prefix, 0) + 1
    return f"{prefix}-{id_counters[prefix]}"


def append_log(log, item):
    log.append(item)
    del log[: max(0, len(log) - g["max_log_entries"])]


def run():
    from .root import ensure_root
    from .tick import start_tick_loop

    tk_root = ensure_root()
    start_tick_loop()
    tk_root.mainloop()


def shutdown():
    from .tick import stop_tick_loop

    stop_tick_loop()
    for window_id in list(windows):
        from .windows import destroy_window

        destroy_window(window_id)
    if g["root"] is not None:
        try:
            g["root"].destroy()
        except Exception:
            pass
        g["root"] = None
    g["is_running"] = False


reset_app()
