---
name: "Python"
description: "My Python defaults: uv, ruff, type hints on signatures, numpy over loops. Repo config overrides."
applyTo: "**/*.py"
---

# Python defaults

These are my defaults. If the repo's `pyproject.toml` or instructions say otherwise, follow the repo.

- Use `uv` for environments, dependencies, and commands (`uv add`, `uv run`, `uv sync`).
- Use ruff for linting and formatting. If the repo has no config, use a line length of 88.
- Type-hint function signatures, but don't annotate locals by default or retrofit hints onto code you didn't touch.
- Prefer numpy vectorization when it makes the operation clearer. A readable loop is better than a contorted vectorized expression.
- Prefer `pathlib.Path` to `os.path`.
- Remove temporary `print` debugging before finishing.
