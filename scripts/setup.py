"""Repeatable development install; no libraries, models or production assets created."""

import os
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for executable, args in [
    ("uv", ["sync", "--locked"]),
    ("npm", ["ci", "--prefix", "frontend"]),
    ("npm", ["run", "build", "--prefix", "frontend"]),
]:
    command = shutil.which(executable)
    if not command:
        raise SystemExit(f"Install the documented {executable} tool first")
    subprocess.run([command, *args], cwd=root, env=os.environ.copy(), check=True)
