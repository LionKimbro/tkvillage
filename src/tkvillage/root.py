from __future__ import annotations

import tkinter as tk

from . import app as rt


def ensure_root():
    if rt.g["root"] is None:
        tk_root = tk.Tk()
        tk_root.withdraw()
        tk_root.option_add("*tearOff", False)
        rt.g["root"] = tk_root
    return rt.g["root"]


def root_is_withdrawn():
    if rt.g["root"] is None:
        return False
    return rt.g["root"].state() == "withdrawn"
