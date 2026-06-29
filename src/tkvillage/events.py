from __future__ import annotations

import time

from . import app as rt
from .app import append_log


def post_event(target_id, event):
    target = rt.targets[target_id]
    target["inbox"].append(event)
    append_log(rt.event_log, {"at": time.time(), "target_id": target_id, "event": event})
    return event


def post_event_to_window(window_id, event):
    return post_event(window_id, event)


def post_event_to_instance(instance_key, event):
    return post_event(rt.windows_by_instance_key[instance_key], event)


def post_event_to_kind(window_kind, event):
    instance_key = f"{window_kind}:singleton"
    return post_event_to_instance(instance_key, event)


def broadcast_event(event):
    for target_id in list(rt.targets):
        post_event(target_id, dict(event))
