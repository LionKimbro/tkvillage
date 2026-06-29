# tkvillage

TkVillage is a small importable Python/Tkinter runtime for Lion-style modular GUI
applications. It owns a hidden Tk root, summonable `Toplevel` windows, reducer
state dictionaries, queued semantic events, a periodic tick loop, simple message
routing, config persistence, testing helpers, and debug snapshots.

The first runnable example is:

```powershell
$env:PYTHONPATH = "src"
python examples/minimal_app.py
```

The core API is re-exported from `tkvillage`:

```python
import tkvillage as village

village.create_app("my-app", ".my-app")
village.register_window_kind(...)
village.summon_window("main")
village.run()
```
