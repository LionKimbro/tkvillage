from __future__ import annotations

import time
import tkinter.messagebox as messagebox

from . import app as rt
from .app import append_log


def route_effects(effects, source_id=None):
    for effect in effects or []:
        route_effect(effect, source_id)


def route_effect(effect, source_id=None):
    append_log(rt.effect_log, {"at": time.time(), "source_id": source_id, "effect": effect})
    effect_type = effect.get("type")
    if effect_type == "POST_EVENT":
        from .events import post_event

        return post_event(effect["target_id"], effect["event"])
    if effect_type == "SEND_MESSAGE":
        from .messages import send_message

        return send_message(effect["target_id"], effect["message"], source_id=source_id)
    if effect_type == "SUMMON_WINDOW":
        from .windows import summon_window

        return summon_window(effect["window_kind"], effect.get("key"), effect.get("payload"))
    if effect_type == "CLOSE_WINDOW":
        from .windows import close_window

        return close_window(effect.get("window_id", source_id))
    if effect_type == "DESTROY_WINDOW":
        from .windows import destroy_window

        return destroy_window(effect.get("window_id", source_id))
    if effect_type == "REQUEST_PROJECT":
        window_id = effect.get("window_id", source_id)
        if window_id in rt.windows:
            rt.windows[window_id]["needs_project"] = True
        return None
    if effect_type == "LOG":
        append_log(rt.runtime_log, {"at": time.time(), "source_id": source_id, "message": effect.get("message")})
        return None
    if effect_type == "SHOW_MESSAGE_BOX":
        return messagebox.showinfo(effect.get("title", "TkVillage"), effect.get("message", ""))
    if rt.g["strict_effects"]:
        raise ValueError(f"Unknown effect type: {effect_type}")
    append_log(rt.runtime_log, {"at": time.time(), "source_id": source_id, "message": f"Unknown effect: {effect_type}"})
    return None
