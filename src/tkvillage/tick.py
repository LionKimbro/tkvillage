from __future__ import annotations

import time
import traceback

from . import app as rt
from .app import append_log
from .effects import route_effects
from .reducers import reduce_window_event
from .windows import project_window


def start_tick_loop():
    rt.g["is_running"] = True
    schedule_next_tick()


def stop_tick_loop():
    rt.g["is_running"] = False
    if rt.g["root"] is not None and rt.g["tick_after_id"] is not None:
        try:
            rt.g["root"].after_cancel(rt.g["tick_after_id"])
        except Exception:
            pass
    rt.g["tick_after_id"] = None


def schedule_next_tick():
    if rt.g["root"] is not None and rt.g["is_running"]:
        rt.g["tick_after_id"] = rt.g["root"].after(rt.g["tick_interval_ms"], tick_loop)


def tick_loop():
    tick_once()
    schedule_next_tick()


def tick_once():
    rt.g["tick_count"] += 1
    try:
        drain_service_targets()
        drain_window_events()
        call_window_ticks()
        project_dirty_windows()
    except Exception as exc:
        append_log(
            rt.runtime_log,
            {
                "at": time.time(),
                "message": "tick exception",
                "error": repr(exc),
                "traceback": traceback.format_exc(),
            },
        )
        if rt.g["test_mode"]:
            raise
    return rt.g["tick_count"]


def run_ticks(count=1, update_tk=True):
    for _ in range(count):
        tick_once()
        if update_tk and rt.g["root"] is not None:
            rt.g["root"].update_idletasks()
            rt.g["root"].update()


def drain_window_events():
    for window_id, record in list(rt.windows.items()):
        queue = record["event_queue"]
        while queue:
            event = queue.pop(0)
            effects = reduce_window_event(record, event)
            route_effects(effects, window_id)


def drain_service_targets():
    for target_id, target in list(rt.targets.items()):
        if target["target_kind"] == "window":
            continue
        handler = target["handler"]
        while target["inbox"]:
            event = target["inbox"].pop(0)
            effects = handler(rt, target, event) or []
            route_effects(effects, target_id)


def call_window_ticks():
    for record in list(rt.windows.values()):
        hook = rt.window_kinds[record["window_kind"]]["on_tick"]
        if hook is not None:
            effects = hook(rt, record) or []
            route_effects(effects, record["window_id"])


def project_dirty_windows():
    for record in list(rt.windows.values()):
        if record["needs_project"]:
            project_window(record)
