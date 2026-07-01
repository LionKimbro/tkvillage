# Learned Programming Guidelines

This file records project-local programming rules for Codex, Claude Code, and other coding agents working on TkVillage.

## Bundle Arguments Belong in Dictionaries

TkVillage follows this rule:

> Pass as parameters only the things that actually vary independently. If a group of values is a declaration, specification, or other bundle, pass it as one explicit dictionary.

Use a single dictionary for APIs that declare structured runtime things.

Preferred:

```python
village.declare_app({
    "name": "my-app",
    "project-dir-name": ".my-app",
    "shutdown-policy": "on-last-window-close",
})

village.register_window_kind({
    "window-kind": "main",
    "title": "Main",
    "multiplicity": "singleton",
    "create": create,
    "make-initial-state": make_initial_state,
    "reduce-event": reduce_event,
    "project": project,
})

village.declare_config({
    "name": "theme",
    "default": "light",
    "type": "choice",
    "description": "UI theme",
    "choices": ["light", "dark"],
})
```

Avoid wide signatures where arguments are really fields of one declaration.

Avoid:

```python
village.register_window_kind("main", title="Main", multiplicity="singleton", create=create)
village.declare_config("theme", "light", "choice", "UI theme", ["light", "dark"])
```

## Use Kebab-Case Keys for User-Facing Declarations

When a declaration dictionary is part of the public API, prefer kebab-case keys:

```python
"project-dir-name"
"window-kind"
"make-initial-state"
"reduce-event"
"debug-label"
```

Internal Python records may still use snake_case where that is already the local runtime convention.

## Do Not Preserve Early Experimental APIs Unless Asked

TkVillage is still young. If a public API is corrected before real downstream software depends on it, prefer a clean replacement over compatibility shims.

Deprecated compatibility is acceptable when explicitly requested or already documented, as with `create_app()`.

## Runtime Modules Are Not Callback Parameters

Do not pass `tkvillage.app` or an `rt` alias into callbacks. The runtime module is not varying data.

If callback code genuinely needs runtime inspection, import the module directly:

```python
import tkvillage.app as rt
```

Callback parameters should be the values that actually vary for the callback, such as `record`, `state`, `event`, `target`, `key`, or `payload`.
