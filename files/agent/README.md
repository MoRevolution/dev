# agent files

How I like agents to write code and prose. Harness-agnostic on purpose.

- `baseline.instructions.md`: code taste and how to talk to me. Meant to be always on.
- `python.instructions.md`: Python defaults (uv, ruff, type hints). Loads for `.py` files.
- `writing-style/`: a skill wrapping `references/writing_style.md`, the full guide to my writing voice. That guide is the canonical copy; edit it here or in place and run `nu setup.nu collect` to pull it back.

## where they go

VS Code Copilot is wired up in `config.toml`. Instructions land in the user prompts folder, the skill in `~/.copilot/skills/`.

For anything else, the shape is the same: the baseline goes wherever the harness reads global instructions (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.config/opencode/AGENTS.md`, and so on), and `writing-style/` goes wherever it reads skills. Strip the YAML frontmatter if the harness doesn't understand it. Check the harness docs, these paths move.
