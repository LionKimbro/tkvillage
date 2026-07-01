from __future__ import annotations

import time
import warnings

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
            "shutdown_policy": None,
            "shutdown_window_kind": None,
            "shutdown_requested": False,
            "shutdown_reason": None,
            "is_shutting_down": False,
            "shutdown_handler": None,
            "shutdown_handler_called": False,
            "has_had_window": False,
            "shutdown_window_kind_seen": False,
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


def declare_app(spec):
    """Declare and initialize the runtime from one visible application spec."""
    validate_app_spec(spec)
    reset_app()
    set_runtime_identity(
        spec["name"],
        spec.get("tick-interval-ms", DEFAULT_TICK_INTERVAL_MS),
        spec.get("test-mode", False),
    )
    g["project_dir"] = resolve_project_dir(spec["project-dir-name"], spec.get("project-root"))
    g["shutdown_policy"] = spec["shutdown-policy"]
    g["shutdown_window_kind"] = spec.get("shutdown-window-kind")
    g["shutdown_handler"] = spec.get("on-shutdown")

    if spec.get("create-root", True):
        from .root import ensure_root

        ensure_root()

    from .config import load_config
    from .debug import install_debug_shortcut, register_debug_windows

    load_config()
    register_debug_windows()
    if g["root"] is not None:
        install_debug_shortcut()
    return g


def create_app(
    name="tkvillage",
    project_dir_name=".tkvillage",
    project_root=None,
    tick_interval_ms=DEFAULT_TICK_INTERVAL_MS,
    test_mode=False,
    create_root=True,
):
    """Deprecated compatibility wrapper. Prefer declare_app(spec)."""
    warnings.warn(
        "create_app() is deprecated; use declare_app({...}) instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return declare_app(
        {
            "name": name,
            "project-dir-name": project_dir_name,
            "project-root": project_root,
            "tick-interval-ms": tick_interval_ms,
            "test-mode": test_mode,
            "create-root": create_root,
            "shutdown-policy": "explicit",
            "shutdown-window-kind": None,
            "on-shutdown": None,
        }
    )


def validate_app_spec(spec):
    required = ["name", "project-dir-name", "shutdown-policy"]
    for key in required:
        if key not in spec:
            raise ValueError(f"declare_app spec requires {key!r}")
    policy = spec["shutdown-policy"]
    if policy not in {"on-window-close", "on-last-window-close", "explicit"}:
        raise ValueError(f"Unknown shutdown-policy: {policy}")
    if policy == "on-window-close" and not spec.get("shutdown-window-kind"):
        raise ValueError("shutdown-window-kind is required for on-window-close")
    handler = spec.get("on-shutdown")
    if handler is not None and not callable(handler):
        raise ValueError("on-shutdown must be callable or None")


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


def request_shutdown(reason=None):
    g["shutdown_requested"] = True
    g["shutdown_reason"] = reason
    append_log(
        runtime_log,
        {
            "at": time.time(),
            "message": "shutdown requested",
            "reason": reason,
        },
    )


def maybe_begin_shutdown():
    if g["is_shutting_down"]:
        return False
    if not should_begin_shutdown():
        return False
    begin_shutdown()
    return True


def should_begin_shutdown():
    policy = g["shutdown_policy"]
    if policy == "explicit":
        return g["shutdown_requested"]
    if policy == "on-last-window-close":
        return g["has_had_window"] and not windows
    if policy == "on-window-close":
        kind = g["shutdown_window_kind"]
        if not g["shutdown_window_kind_seen"]:
            return False
        return not any(record["window_kind"] == kind for record in windows.values())
    return False


def begin_shutdown():
    g["is_shutting_down"] = True
    try:
        call_shutdown_handler()
    finally:
        from .tick import stop_tick_loop

        stop_tick_loop()
        if g["root"] is not None:
            try:
                g["root"].quit()
            except Exception:
                pass
        g["is_running"] = False


def call_shutdown_handler():
    handler = g["shutdown_handler"]
    if handler is None or g["shutdown_handler_called"]:
        return
    g["shutdown_handler_called"] = True
    handler()


def run():
    from .root import ensure_root
    from .tick import start_tick_loop

    tk_root = ensure_root()
    start_tick_loop()
    tk_root.mainloop()


def shutdown():
    from .tick import stop_tick_loop

    g["is_shutting_down"] = True
    call_shutdown_handler()
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
