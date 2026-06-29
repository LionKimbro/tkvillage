from __future__ import annotations

import tkinter as tk

from .app import app


def ensure_root():
    if app["root"] is None:
        root = tk.Tk()
        root.withdraw()
        root.option_add("*tearOff", False)
        app["root"] = root
    return app["root"]


def root_is_withdrawn():
    root = app["root"]
    if root is None:
        return False
    return root.state() == "withdrawn"
