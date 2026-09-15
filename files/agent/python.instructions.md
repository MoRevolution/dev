---
name: "Python"
description: "My Python defaults: uv, ruff, type hints on signatures, numpy over loops. Repo config overrides."
applyTo: "**/*.py"
---

# Python defaults

These apply unless the repo's `pyproject.toml` or instructions say otherwise.

- `uv` for everything: `uv add`, `uv run`, `uv sync`. Not pip, not conda, not a bare `python`.
- ruff for lint and format. If the repo has no config, assume line length 88.
- Type hints on function signatures. Not on locals, and not retrofitted onto code you didn't touch.
- Prefer numpy vectorization over Python loops when it reads naturally. Don't contort logic to avoid a loop that's clear.
- `pathlib.Path` over `os.path`.
- No `print` debugging left behind.
