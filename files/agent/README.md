# Agent files

These files capture how I like agents to write code and prose. They are deliberately harness-agnostic, so the same baseline can travel between tools.

- `baseline.instructions.md` covers code taste and how to talk to me. It is meant to be always on.
- `python.instructions.md` holds Python defaults and only needs to load for `.py` files.
- `writing-style/` wraps the full guide to my writing voice. The guide under `references/` is the canonical copy; after editing the live copy, run `nu setup.nu collect` to pull it back here.

## Where they go

VS Code Copilot is already wired up in `config.toml`: instructions go in the user prompts folder and the skill goes in `~/.copilot/skills/`.

For another harness, put the baseline wherever it reads global instructions and `writing-style/` wherever it reads skills. Strip the YAML frontmatter if the harness doesn't understand it, and check its current docs before assuming a path (these conventions move).
