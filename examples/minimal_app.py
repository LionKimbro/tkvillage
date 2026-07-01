from __future__ import annotations

import tkinter as tk

import tkvillage as village


MAIN_WINDOW = "minimal-main"
INCREMENT_CLICKED = "INCREMENT_CLICKED"


def make_initial_state(_key=None, _payload=None):
    return {"count": 0, "status": "Ready"}


def create(record):
    top = record["toplevel"]
    top.title("TkVillage Minimal App")
    label = tk.Label(top)
    label.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
    button = tk.Button(
        top,
        text="Increment",
        command=lambda: village.post_event_to_window(
            record["window_id"], {"type": INCREMENT_CLICKED}
        ),
    )
    button.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
    record["widgets"]["label"] = label
    record["widgets"]["button"] = button


def reduce_event(state, event):
    if event["type"] == INCREMENT_CLICKED:
        new_state = dict(state)
        new_state["count"] += 1
        new_state["status"] = f"Clicked {new_state['count']} time(s)"
        return new_state, [{"type": "LOG", "message": "Incremented counter"}]
    return state, []


def project(record):
    record["widgets"]["label"].configure(text=record["state"]["status"])


def register():
    village.register_window_kind(
        MAIN_WINDOW,
        title="TkVillage Minimal App",
        multiplicity="singleton",
        create=create,
        make_initial_state=make_initial_state,
        reduce_event=reduce_event,
        project=project,
    )


def main():
    village.declare_app(
        {
            "name": "tkvillage-minimal",
            "project-dir-name": ".tkvillage-minimal",
            "shutdown-policy": "on-last-window-close",
            "shutdown-window-kind": None,
            "on-shutdown": None,
        }
    )
    register()
    village.summon_window(MAIN_WINDOW)
    village.run()


if __name__ == "__main__":
    main()
