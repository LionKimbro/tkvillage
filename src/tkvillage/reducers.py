from __future__ import annotations

from .app import app


def reduce_window_event(record, event):
    kind = app["window_kinds"][record["window_kind"]]
    new_state, effects = kind["reduce_event"](app, record["state"], event)
    record["state"] = new_state
    target = app["targets"][record["window_id"]]
    target["state"] = new_state
    record["needs_project"] = True
    return effects or []
