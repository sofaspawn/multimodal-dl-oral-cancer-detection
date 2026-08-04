#!/usr/bin/env python
import subprocess
import sys
import os

os.chdir("backend")
result = subprocess.run(
    [".venv/bin/python", "test_smoke.py"],
    capture_output=True,
    text=True
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
sys.exit(result.returncode)
