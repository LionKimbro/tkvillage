from __future__ import annotations

import time

from . import app as rt
from .app import append_log
from .events import post_event


def register_service_target(target_id, handler, state=None):
    record = {
        "target_id": target_id,
        "target_kind": "service",
        "inbox": [],
        "handler": handler,
        "state": state or {},
        "is_active": True,
    }
    rt.targets[target_id] = record
    return record


def send_message(target_id, message, source_id=None):
    envelope = {"type": "MESSAGE", "source_id": source_id, "message": message}
    append_log(rt.message_log, {"at": time.time(), "target_id": target_id, "message": envelope})
    return post_event(target_id, envelope)


def send_message_to_window(window_id, message, source_id=None):
    return send_message(window_id, message, source_id)


def send_message_to_instance(instance_key, message, source_id=None):
    return send_message(rt.windows_by_instance_key[instance_key], message, source_id)


def send_message_to_kind(window_kind, message, source_id=None):
    return send_message_to_instance(f"{window_kind}:singleton", message, source_id)


def broadcast_message(message, source_id=None):
    for target_id in list(rt.targets):
        send_message(target_id, dict(message), source_id)
