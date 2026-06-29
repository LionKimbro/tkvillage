from __future__ import annotations

import json
import tkinter as tk

from . import app as rt


DEBUG_DASHBOARD_KIND = "tkvillage-debug-dashboard"


def register_debug_windows():
    from .windows import register_window_kind

    if DEBUG_DASHBOARD_KIND in rt.window_kinds:
        return
    register_window_kind(
        DEBUG_DASHBOARD_KIND,
        title="TkVillage Runtime",
        multiplicity="singleton",
        create=create_debug_dashboard,
        make_initial_state=make_debug_state,
        reduce_event=reduce_debug_event,
        project=project_debug_dashboard,
        debug_label="TkVillage Runtime Dashboard",
    )


def install_debug_shortcut():
    rt.g["root"].bind_all("<Control-Shift-D>", lambda _event: toggle_debug())


def toggle_debug():
    rt.debug["enabled"] = not rt.debug["enabled"]
    if rt.debug["enabled"]:
        from .windows import summon_window

        return summon_window(DEBUG_DASHBOARD_KIND)
    return rt.debug["enabled"]


def get_debug_snapshot(selected_window_id=None):
    snapshot = {
        "app": {
            "name": rt.g["name"],
            "tick_count": rt.g["tick_count"],
            "debug_enabled": rt.debug["enabled"],
            "tick_interval_ms": rt.g["tick_interval_ms"],
            "test_mode": rt.g["test_mode"],
        },
        "window_kinds": {
            name: {
                "title": record["title"],
                "multiplicity": record["multiplicity"],
                "debug_label": record["debug_label"],
            }
            for name, record in rt.window_kinds.items()
        },
        "active_windows": {
            window_id: summarize_window(record) for window_id, record in rt.windows.items()
        },
        "recent_events": list(rt.event_log),
        "recent_effects": list(rt.effect_log),
        "recent_messages": list(rt.message_log),
        "runtime_log": list(rt.runtime_log),
    }
    if selected_window_id is not None and selected_window_id in rt.windows:
        snapshot["selected_window_state"] = rt.windows[selected_window_id]["state"]
    rt.debug["last_snapshot"] = snapshot
    return snapshot


def copy_debug_snapshot(selected_window_id=None):
    text = json.dumps(get_debug_snapshot(selected_window_id), indent=2, default=str)
    if rt.g["root"] is not None:
        rt.g["root"].clipboard_clear()
        rt.g["root"].clipboard_append(text)
    return text


def summarize_window(record):
    return {
        "window_id": record["window_id"],
        "window_kind": record["window_kind"],
        "instance_key": record["instance_key"],
        "key": record["key"],
        "is_open": record["is_open"],
        "is_destroyed": record["is_destroyed"],
        "queue_length": len(record["event_queue"]),
        "debug_label": record["debug_label"],
        "state": record["state"],
    }


def make_debug_state(_app, _key=None, _payload=None):
    return {"title": "TkVillage Runtime Dashboard"}


def create_debug_dashboard(_app, record):
    frame = tk.Frame(record["toplevel"])
    frame.grid(row=0, column=0, sticky="nsew")
    text = tk.Text(frame, width=88, height=28)
    text.grid(row=0, column=0, sticky="nsew")
    button = tk.Button(frame, text="Copy Snapshot", command=lambda: copy_debug_snapshot())
    button.grid(row=1, column=0, sticky="ew")
    record["toplevel"].columnconfigure(0, weight=1)
    record["toplevel"].rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    record["widgets"]["text"] = text


def reduce_debug_event(_app, state, event):
    if event.get("type") == "REFRESH":
        return dict(state), []
    return state, []


def project_debug_dashboard(_app, record):
    text = record["widgets"].get("text")
    if text is None:
        return
    snapshot = get_debug_snapshot()
    text.configure(state="normal")
    text.delete("1.0", "end")
    text.insert("1.0", json.dumps(snapshot, indent=2, default=str))
    text.configure(state="disabled")
