from __future__ import annotations

import argparse
import json
import runpy

from .app import declare_app, run
from .config import get_config, list_config, set_config
from .debug import get_debug_snapshot


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tkvillage")
    parser.add_argument("--project-dir", default=".tkvillage")
    parser.add_argument("--project-root", default=None)
    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("entrypoint", nargs="?")

    sub.add_parser("config-list")
    get_cmd = sub.add_parser("config-get")
    get_cmd.add_argument("name")
    set_cmd = sub.add_parser("config-set")
    set_cmd.add_argument("name")
    set_cmd.add_argument("value")
    sub.add_parser("debug-snapshot")

    args = parser.parse_args(argv)
    declare_app(
        {
            "name": "tkvillage",
            "project-dir-name": args.project_dir,
            "project-root": args.project_root,
            "shutdown-policy": "explicit",
            "shutdown-window-kind": None,
            "on-shutdown": None,
        }
    )

    if args.command == "run":
        if args.entrypoint:
            runpy.run_path(args.entrypoint, run_name="__main__")
        run()
        return 0
    if args.command == "config-list":
        print(json.dumps(list_config(), indent=2, default=str))
        return 0
    if args.command == "config-get":
        print(get_config(args.name))
        return 0
    if args.command == "config-set":
        print(set_config(args.name, args.value))
        return 0
    if args.command == "debug-snapshot":
        print(json.dumps(get_debug_snapshot(), indent=2, default=str))
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
