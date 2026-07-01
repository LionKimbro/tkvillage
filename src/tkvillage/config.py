from __future__ import annotations

import json
from pathlib import Path

from . import app as rt


CONFIG_TYPES = {"string", "int", "float", "bool", "path", "choice"}


def config_path():
    return rt.g["project_dir"] / "config.json"


def declare_config(spec):
    name = spec["name"]
    default = spec.get("default")
    type = spec.get("type", "string")
    description = spec.get("description", "")
    choices = spec.get("choices")
    if type not in CONFIG_TYPES:
        raise ValueError(f"Unknown config type: {type}")
    if type == "choice" and not choices:
        raise ValueError("choice config requires choices")
    declaration = {
        "name": name,
        "type": type,
        "default": default,
        "description": description,
        "choices": list(choices or []),
    }
    rt.config_declarations[name] = declaration
    rt.config_values.setdefault(name, default)
    return declaration


def load_config():
    path = config_path()
    values = {}
    if path.exists():
        values = json.loads(path.read_text(encoding="utf-8"))
    for name, declaration in rt.config_declarations.items():
        rt.config_values[name] = coerce_config_value(
            values.get(name, declaration["default"]), declaration
        )
    for name, value in values.items():
        if name not in rt.config_declarations:
            rt.config_values[name] = value
    return rt.config_values


def save_config():
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    for name, value in rt.config_values.items():
        data[name] = str(value) if isinstance(value, Path) else value
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_config(name):
    return rt.config_values[name]


def set_config(name, value, persist=True):
    declaration = rt.config_declarations.get(name)
    if declaration is None:
        declaration = declare_config(
            {"name": name, "default": value, "type": infer_config_type(value)}
        )
    rt.config_values[name] = coerce_config_value(value, declaration)
    if persist:
        save_config()
    return rt.config_values[name]


def list_config():
    rows = []
    for name, declaration in rt.config_declarations.items():
        row = dict(declaration)
        row["value"] = rt.config_values.get(name)
        rows.append(row)
    return rows


def infer_config_type(value):
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, Path):
        return "path"
    return "string"


def coerce_config_value(value, declaration):
    type = declaration["type"]
    if type == "string":
        return "" if value is None else str(value)
    if type == "int":
        return int(value)
    if type == "float":
        return float(value)
    if type == "bool":
        return coerce_bool(value)
    if type == "path":
        return Path(value).expanduser().resolve()
    if type == "choice":
        if value not in declaration["choices"]:
            raise ValueError(f"{value!r} is not a valid choice for {declaration['name']}")
        return value
    return value


def coerce_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return bool(value)
