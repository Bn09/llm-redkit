import importlib.util, sys
from pathlib import Path

def load_plugins(directory):
    plugins = {}
    d = Path(directory)
    if not d.exists():
        return plugins
    for p in d.glob("*.py"):
        if p.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(p.stem, p)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[p.stem] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            continue
        if hasattr(mod, "ATTACKS"):
            plugins[p.stem] = mod.ATTACKS
    return plugins
