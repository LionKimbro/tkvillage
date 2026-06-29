from __future__ import annotations

import time

from .app import app
from .tick import tick_once


def run_until(predicate, timeout_ms=1000, max_ticks=1000):
    started = time.time()
    ticks = 0
    while ticks < max_ticks:
        if predicate():
            return True
        tick_once()
        if app["root"] is not None:
            app["root"].update_idletasks()
            app["root"].update()
        ticks += 1
        if (time.time() - started) * 1000 > timeout_ms:
            break
    return predicate()
