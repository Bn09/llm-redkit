import os
import sys
import subprocess
from pathlib import Path


IS_WINDOWS = sys.platform.startswith("win")
IS_WSL = "microsoft" in (os.uname().release.lower()
                          if hasattr(os, "uname") else "")
IS_LINUX = sys.platform.startswith("linux")
IS_MAC = sys.platform == "darwin"


def open_file(path):
    """Open a file with the OS default application. Cross-platform."""
    p = Path(path).resolve()
    if not p.exists():
        return False, f"file not found: {p}"
    try:
        if IS_WINDOWS:
            os.startfile(str(p))
        elif IS_WSL:
            # Convert WSL path to Windows path and use explorer
            win = subprocess.run(
                ["wslpath", "-w", str(p)],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            subprocess.Popen(["explorer.exe", win])
        elif IS_MAC:
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])
        return True, None
    except Exception as e:
        return False, str(e)


def make_tarball(src_dir, out_path, exclude_dirs=None):
    """Create a .tar.gz. Works on Windows/Linux/Mac."""
    import tarfile
    exclude_dirs = exclude_dirs or []
    src = Path(src_dir).resolve()
    out = Path(out_path).resolve()
    with tarfile.open(out, "w:gz") as tar:
        for item in src.rglob("*"):
            rel = item.relative_to(src)
            if any(part in exclude_dirs for part in rel.parts):
                continue
            if item.is_file():
                tar.add(item, arcname=str(rel))
    return out


def get_cache_dir():
    """Per-OS cache dir."""
    if IS_WINDOWS:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif IS_MAC:
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "llm-redkit"
