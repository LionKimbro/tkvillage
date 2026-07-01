from __future__ import annotations

import time
import tkinter as tk

from . import app as rt
from .app import next_id
from .root import ensure_root


MULTIPLICITIES = {"singleton", "per-key", "free-instance", "embedded", "modal"}


def register_window_kind(
    window_kind,
    title=None,
    multiplicity="singleton",
    create=None,
    make_initial_state=None,
    reduce_event=None,
    project=None,
    on_show=None,
    on_close=None,
    on_destroy=None,
    on_tick=None,
    debug_label=None,
):
    if multiplicity not in MULTIPLICITIES:
        raise ValueError(f"Unknown window multiplicity: {multiplicity}")
    if multiplicity in {"embedded", "modal"}:
        raise NotImplementedError(f"{multiplicity} windows are declared but not implemented in v1")
    record = {
        "window_kind": window_kind,
        "title": title or window_kind,
        "multiplicity": multiplicity,
        "create": create or default_create,
        "make_initial_state": make_initial_state or default_initial_state,
        "reduce_event": reduce_event or default_reduce_event,
        "project": project or default_project,
        "on_show": on_show,
        "on_close": on_close,
        "on_destroy": on_destroy,
        "on_tick": on_tick,
        "debug_label": debug_label or title or window_kind,
    }
    rt.window_kinds[window_kind] = record
    return record


def summon_window(window_kind, key=None, payload=None):
    kind = rt.window_kinds[window_kind]
    instance_key = compute_instance_key(kind, key)
    existing_id = rt.windows_by_instance_key.get(instance_key)
    if existing_id in rt.windows:
        record = rt.windows[existing_id]
        raise_window(record["window_id"])
        return record
    record = realize_window(kind, instance_key, key, payload)
    raise_window(record["window_id"])
    return record


def compute_instance_key(kind, key=None):
    multiplicity = kind["multiplicity"]
    window_kind = kind["window_kind"]
    if multiplicity == "singleton":
        return f"{window_kind}:singleton"
    if multiplicity == "per-key":
        if key is None:
            raise ValueError(f"{window_kind} requires key for per-key summon")
        return f"{window_kind}:{key}"
    return f"{window_kind}:{next_id('instance')}"


def realize_window(kind, instance_key, key=None, payload=None):
    root = ensure_root()
    window_id = next_id("window")
    toplevel = tk.Toplevel(root)
    toplevel.title(kind["title"])
    state = kind["make_initial_state"](rt, key, payload)
    state.setdefault("window_id", window_id)
    state.setdefault("window_kind", kind["window_kind"])
    state.setdefault("instance_key", instance_key)
    if key is not None:
        state.setdefault("key", key)
    record = {
        "target_id": window_id,
        "window_id": window_id,
        "window_kind": kind["window_kind"],
        "multiplicity": kind["multiplicity"],
        "instance_key": instance_key,
        "key": key,
        "payload": payload,
        "toplevel": toplevel,
        "state": state,
        "event_queue": [],
        "widgets": {},
        "created_at": time.time(),
        "last_shown_at": None,
        "is_open": True,
        "is_destroyed": False,
        "needs_project": True,
        "debug_label": kind["debug_label"],
    }
    rt.windows[window_id] = record
    rt.g["has_had_window"] = True
    if kind["window_kind"] == rt.g["shutdown_window_kind"]:
        rt.g["shutdown_window_kind_seen"] = True
    rt.windows_by_instance_key[instance_key] = window_id
    rt.targets[window_id] = {
        "target_id": window_id,
        "target_kind": "window",
        "inbox": record["event_queue"],
        "handler": None,
        "state": state,
        "is_active": True,
    }
    toplevel.protocol("WM_DELETE_WINDOW", lambda win=window_id: close_window(win))
    kind["create"](rt, record)
    project_window(record)
    return record


def raise_window(window_id):
    record = rt.windows[window_id]
    top = record["toplevel"]
    try:
        top.deiconify()
        top.lift()
        top.focus_force()
    except Exception:
        pass
    record["last_shown_at"] = time.time()
    hook = rt.window_kinds[record["window_kind"]]["on_show"]
    if hook is not None:
        hook(rt, record)
    return record


def close_window(window_id):
    record = rt.windows[window_id]
    hook = rt.window_kinds[record["window_kind"]]["on_close"]
    if hook is not None:
        result = hook(rt, record)
        if result is False:
            return False
    destroy_window(window_id)
    return True


def destroy_window(window_id):
    record = rt.windows.get(window_id)
    if record is None:
        return
    hook = rt.window_kinds[record["window_kind"]]["on_destroy"]
    if hook is not None:
        hook(rt, record)
    record["is_open"] = False
    record["is_destroyed"] = True
    rt.windows_by_instance_key.pop(record["instance_key"], None)
    rt.targets.pop(window_id, None)
    try:
        record["toplevel"].destroy()
    except Exception:
        pass
    rt.windows.pop(window_id, None)


def project_window(record):
    kind = rt.window_kinds[record["window_kind"]]
    kind["project"](rt, record)
    record["needs_project"] = False


def get_window(window_id):
    return rt.windows[window_id]


def list_windows():
    return list(rt.windows.values())


def default_initial_state(_app, key=None, payload=None):
    state = {}
    if key is not None:
        state["key"] = key
    if payload is not None:
        state["payload"] = payload
    return state


def default_create(_app, record):
    label = tk.Label(record["toplevel"], text=record["debug_label"])
    label.grid(row=0, column=0, padx=12, pady=12)
    record["widgets"]["label"] = label


def default_reduce_event(_app, state, _event):
    return state, []


def default_project(_app, _record):
    return None
