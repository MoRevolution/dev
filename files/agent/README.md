# Agent files

These files capture how I like agents to write code and prose. They are deliberately harness-agnostic, so the same baseline can travel between tools.

- `baseline.instructions.md` covers code taste and how to talk to me. It is meant to be always on.
- `python.instructions.md` holds Python defaults and only needs to load for `.py` files.
- `writing-style/` wraps the full guide to my writing voice. The guide under `references/` is the canonical copy.
- `git-writing/` covers commit messages and PR descriptions, with PR bodies I wrote or approved under `references/`.
- `CLAUDE.md` is Claude Code's entry point; it imports the baseline and the Python defaults.

After editing a live copy, run `nu setup.nu collect` to pull it back here.

## Where they go

`config.toml` wires them up for VS Code Copilot (instructions in the user prompts folder, skills in `~/.copilot/skills/`) and Claude Code (`~/.claude/CLAUDE.md`, skills in `~/.claude/skills/`). A file can list several destinations, and `collect` pulls from the first one.

For another harness, put the baseline wherever it reads global instructions and the skill folders wherever it reads skills. Strip the YAML frontmatter if the harness doesn't understand it, and check its current docs before assuming a path (these conventions move).
