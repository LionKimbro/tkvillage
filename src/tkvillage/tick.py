from __future__ import annotations

import time
import traceback

from .app import app, append_log
from .effects import route_effects
from .reducers import reduce_window_event
from .windows import project_window


def start_tick_loop():
    app["is_running"] = True
    schedule_next_tick()


def stop_tick_loop():
    app["is_running"] = False
    root = app.get("root")
    after_id = app.get("tick_after_id")
    if root is not None and after_id is not None:
        try:
            root.after_cancel(after_id)
        except Exception:
            pass
    app["tick_after_id"] = None


def schedule_next_tick():
    root = app["root"]
    if root is not None and app["is_running"]:
        app["tick_after_id"] = root.after(app["tick_interval_ms"], tick_loop)


def tick_loop():
    tick_once()
    schedule_next_tick()


def tick_once():
    app["tick_count"] += 1
    try:
        drain_service_targets()
        drain_window_events()
        call_window_ticks()
        project_dirty_windows()
    except Exception as exc:
        append_log(
            "runtime_log",
            {
                "at": time.time(),
                "message": "tick exception",
                "error": repr(exc),
                "traceback": traceback.format_exc(),
            },
        )
        if app["test_mode"]:
            raise
    return app["tick_count"]


def run_ticks(count=1, update_tk=True):
    for _ in range(count):
        tick_once()
        if update_tk and app["root"] is not None:
            app["root"].update_idletasks()
            app["root"].update()


def drain_window_events():
    for window_id, record in list(app["windows"].items()):
        queue = record["event_queue"]
        while queue:
            event = queue.pop(0)
            effects = reduce_window_event(record, event)
            route_effects(effects, window_id)


def drain_service_targets():
    for target_id, target in list(app["targets"].items()):
        if target["target_kind"] == "window":
            continue
        handler = target["handler"]
        while target["inbox"]:
            event = target["inbox"].pop(0)
            effects = handler(app, target, event) or []
            route_effects(effects, target_id)


def call_window_ticks():
    for record in list(app["windows"].values()):
        hook = app["window_kinds"][record["window_kind"]]["on_tick"]
        if hook is not None:
            effects = hook(app, record) or []
            route_effects(effects, record["window_id"])


def project_dirty_windows():
    for record in list(app["windows"].values()):
        if record["needs_project"]:
            project_window(record)
