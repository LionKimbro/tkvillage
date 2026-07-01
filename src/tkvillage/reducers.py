from __future__ import annotations

from . import app as rt


def reduce_window_event(record, event):
    kind = rt.window_kinds[record["window_kind"]]
    new_state, effects = kind["reduce_event"](record["state"], event)
    record["state"] = new_state
    target = rt.targets[record["window_id"]]
    target["state"] = new_state
    record["needs_project"] = True
    return effects or []
