from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def run_cli(*args: str, env: dict[str, str] | None = None):
    merged = os.environ.copy()
    merged["PYTHONPATH"] = str(SRC)
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, "-m", "central_repo_scaffold", *args], cwd=ROOT,
        env=merged, text=True, capture_output=True, check=False,
    )
