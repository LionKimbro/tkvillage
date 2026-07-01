from __future__ import annotations

import pytest

import tkvillage as village
import tkvillage.app as rt


def make_tk_app(tmp_path):
    try:
        village.declare_app(
            {
                "name": "test-tkvillage",
                "project-dir-name": ".test-tkvillage",
                "project-root": tmp_path,
                "test-mode": True,
                "shutdown-policy": "explicit",
                "shutdown-window-kind": None,
                "on-shutdown": None,
            }
        )
    except Exception as exc:
        pytest.skip(f"Tk is not available in this environment: {exc}")


def teardown_function():
    village.reset_app()


def test_reset_preserves_runtime_container_identities(tmp_path):
    original_g = rt.g
    original_windows = rt.windows
    original_event_log = rt.event_log
    original_debug = rt.debug

    village.declare_app(
        {
            "name": "test-tkvillage",
            "project-dir-name": ".test-tkvillage",
            "project-root": tmp_path,
            "test-mode": True,
            "create-root": False,
            "shutdown-policy": "explicit",
            "shutdown-window-kind": None,
            "on-shutdown": None,
        }
    )
    rt.windows["temporary"] = {"window_id": "temporary"}
    rt.event_log.append({"type": "TEMP"})

    village.reset_app()

    assert rt.g is original_g
    assert rt.windows is original_windows
    assert rt.event_log is original_event_log
    assert rt.debug is original_debug
    assert rt.g["name"] == "tkvillage"
    assert rt.windows == {}
    assert rt.event_log == []
    assert rt.debug == {"enabled": False, "last_snapshot": None}


def test_declare_app_requires_shutdown_policy(tmp_path):
    with pytest.raises(ValueError):
        village.declare_app(
            {
                "name": "test-tkvillage",
                "project-dir-name": ".test-tkvillage",
                "project-root": tmp_path,
                "create-root": False,
            }
        )


def test_explicit_shutdown_policy_waits_for_request(tmp_path):
    called = []
    village.declare_app(
        {
            "name": "test-tkvillage",
            "project-dir-name": ".test-tkvillage",
            "project-root": tmp_path,
            "create-root": False,
            "shutdown-policy": "explicit",
            "shutdown-window-kind": None,
            "on-shutdown": lambda: called.append("shutdown"),
        }
    )

    village.tick_once()
    assert called == []
    assert rt.g["is_shutting_down"] is False

    village.request_shutdown("test")
    village.tick_once()

    assert called == ["shutdown"]
    assert rt.g["is_shutting_down"] is True
    assert rt.g["shutdown_reason"] == "test"


def test_on_last_window_close_waits_until_a_window_has_existed(tmp_path):
    called = []
    village.declare_app(
        {
            "name": "test-tkvillage",
            "project-dir-name": ".test-tkvillage",
            "project-root": tmp_path,
            "create-root": False,
            "shutdown-policy": "on-last-window-close",
            "shutdown-window-kind": None,
            "on-shutdown": lambda: called.append("shutdown"),
        }
    )

    village.tick_once()
    assert called == []

    rt.g["has_had_window"] = True
    village.tick_once()

    assert called == ["shutdown"]
    assert rt.g["is_shutting_down"] is True


def test_on_window_close_waits_for_declared_kind_to_have_existed(tmp_path):
    called = []
    village.declare_app(
        {
            "name": "test-tkvillage",
            "project-dir-name": ".test-tkvillage",
            "project-root": tmp_path,
            "create-root": False,
            "shutdown-policy": "on-window-close",
            "shutdown-window-kind": "main",
            "on-shutdown": lambda: called.append("shutdown"),
        }
    )

    village.tick_once()
    assert called == []

    rt.g["shutdown_window_kind_seen"] = True
    village.tick_once()

    assert called == ["shutdown"]
    assert rt.g["is_shutting_down"] is True


def register_counter_kind(kind="counter", multiplicity="singleton"):
    def make_initial_state(_app, key=None, payload=None):
        state = {"count": 0}
        if key is not None:
            state["key"] = key
        if payload is not None:
            state["payload"] = payload
        return state

    def reduce_event(_app, state, event):
        if event["type"] == "INCREMENT":
            new_state = dict(state)
            new_state["count"] += event.get("amount", 1)
            return new_state, [{"type": "LOG", "message": "increment"}]
        if event["type"] == "MESSAGE":
            new_state = dict(state)
            new_state["last_message"] = event["message"]
            return new_state, []
        return state, []

    def project(_app, record):
        record["state"]["projected_count"] = record["state"]["count"]

    village.register_window_kind(
        kind,
        title=kind,
        multiplicity=multiplicity,
        make_initial_state=make_initial_state,
        reduce_event=reduce_event,
        project=project,
    )


def test_singleton_summon_reuses_window(tmp_path):
    make_tk_app(tmp_path)
    register_counter_kind()

    first = village.summon_window("counter")
    second = village.summon_window("counter")

    assert first["window_id"] == second["window_id"]
    assert len(rt.windows) == 1
    assert rt.g["root"].state() == "withdrawn"


def test_free_instance_summon_creates_multiple_windows(tmp_path):
    make_tk_app(tmp_path)
    register_counter_kind("scratch", "free-instance")

    first = village.summon_window("scratch")
    second = village.summon_window("scratch")

    assert first["window_id"] != second["window_id"]
    assert len(rt.windows) == 2


def test_per_key_summon_reuses_matching_key(tmp_path):
    make_tk_app(tmp_path)
    register_counter_kind("editor", "per-key")

    first_a = village.summon_window("editor", key="a")
    second_a = village.summon_window("editor", key="a")
    first_b = village.summon_window("editor", key="b")

    assert first_a["window_id"] == second_a["window_id"]
    assert first_a["window_id"] != first_b["window_id"]
    assert len(rt.windows) == 2


def test_event_reducer_effect_and_projection(tmp_path):
    make_tk_app(tmp_path)
    register_counter_kind()
    record = village.summon_window("counter")

    village.post_event_to_window(record["window_id"], {"type": "INCREMENT", "amount": 3})
    village.tick_once()

    assert record["state"]["count"] == 3
    assert record["state"]["projected_count"] == 3
    assert rt.effect_log[-1]["effect"]["type"] == "LOG"


def test_message_routes_to_window_queue(tmp_path):
    make_tk_app(tmp_path)
    register_counter_kind()
    record = village.summon_window("counter")

    village.send_message_to_window(record["window_id"], {"hello": "there"}, source_id="test")
    village.tick_once()

    assert record["state"]["last_message"] == {"hello": "there"}
    assert rt.message_log[-1]["target_id"] == record["window_id"]


def test_service_target_receives_queued_input(tmp_path):
    make_tk_app(tmp_path)
    seen = []

    def handler(_app, target, event):
        seen.append(event)
        target["state"]["handled"] = True
        return [{"type": "LOG", "message": "service handled"}]

    village.register_service_target("svc", handler, {})
    village.post_event("svc", {"type": "PING"})
    village.tick_once()

    assert seen == [{"type": "PING"}]
    assert rt.targets["svc"]["state"]["handled"] is True


def test_config_declares_coerces_and_persists(tmp_path):
    village.declare_app(
        {
            "name": "test-tkvillage",
            "project-dir-name": ".test-tkvillage",
            "project-root": tmp_path,
            "test-mode": True,
            "create-root": False,
            "shutdown-policy": "explicit",
            "shutdown-window-kind": None,
            "on-shutdown": None,
        }
    )
    village.declare_config("ui.scale", 1, "int", "UI scale")
    village.set_config("ui.scale", "3")

    village.declare_app(
        {
            "name": "test-tkvillage",
            "project-dir-name": ".test-tkvillage",
            "project-root": tmp_path,
            "test-mode": True,
            "create-root": False,
            "shutdown-policy": "explicit",
            "shutdown-window-kind": None,
            "on-shutdown": None,
        }
    )
    village.declare_config("ui.scale", 1, "int", "UI scale")
    village.load_config()

    assert village.get_config("ui.scale") == 3


def test_debug_snapshot_is_json_friendly(tmp_path):
    make_tk_app(tmp_path)
    register_counter_kind()
    record = village.summon_window("counter")

    snapshot = village.get_debug_snapshot(record["window_id"])

    assert "counter" in snapshot["window_kinds"]
    assert record["window_id"] in snapshot["active_windows"]
    assert snapshot["selected_window_state"]["count"] == 0
