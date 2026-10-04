#!/usr/bin/env python3
"""Build distribution tarball. Cross-platform (Windows/Linux/Mac/WSL)."""
import argparse
import sys
from pathlib import Path
from llm_redkit.platform_utils import make_tarball

EXCLUDE = {
    "venv", ".git", "__pycache__", ".pytest_cache",
    ".mypy_cache", "node_modules", "dist", "build",
    "report.html", "report.pdf",
    "findings.json", "findings-run1.json", "findings-run2.json",
    "audit.jsonl", "audit_orig.jsonl",
    "real_agent_demo.txt", "agentic_demo.txt",
    "concurrent_findings.json",
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", default="v2.2")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    root = Path(__file__).parent
    out = args.out or str(root / f"dist/llm-redkit-{args.version}.tar.gz")
    Path(out).parent.mkdir(parents=True, exist_ok=True)

    print(f"building from: {root}")
    print(f"output: {out}")
    make_tarball(root, out, exclude_dirs=EXCLUDE)
    size = Path(out).stat().st_size
    print(f"done. {size} bytes ({size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
