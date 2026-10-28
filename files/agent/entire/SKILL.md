---
name: entire
description: "How I use the Entire CLI locally for agent session checkpoints, line-level provenance (entire why), and token diagnostics without pushing transcripts to shared remotes."
---

# Entire CLI

Entire hooks into local coding agents (Claude Code, OpenCode) and git so commits get an `Entire-Checkpoint: <id>` trailer and the session transcript lives in `refs/entire/checkpoints/*`. That way when I (or another agent) come back to a branch later, the prompt and tool history behind a change are still attached to the commit.

## Turning it on locally

In Nushell, run `entire-local` from the repo root (defined in `config.nu`). It runs:

```sh
entire enable -y --local --skip-push-sessions --telemetry=false --agent claude-code
entire agent add opencode
```

and adds `.entire/`, `.claude/settings.json`, and `.opencode/plugins/entire.ts` to `<git-common-dir>/info/exclude`. With `push_sessions: false` in `.entire/settings.local.json`, checkpoints stay on this machine and `git status` stays clean.

## Commands

Run `entire agent-help` (or `entire agent-help <subcommand>`) for exact flags instead of guessing. The ones I actually use:

- `entire why <file>` or `entire why <file>:<line>` to see which session and prompt produced a file or line.
- `entire checkpoint explain <id-or-commit>` for the full prompt, tool calls, and transcript (`--generate` adds a short Sonnet summary).
- `entire session tokens <session-id>` for input vs. cache-read vs. cache-write token breakdown (useful when a session is spending 80%+ replaying context).
- `entire search "<query>" --compact` for hybrid keyword + semantic search across sessions (only on personal repos mirrored via `entire repo mirror add`).

## Gotchas

- **Attribution is commit-based, not diff-based:** `entire why` goes from `git blame` to the commit's `Entire-Checkpoint:` trailer. Any hand-edits committed alongside an agent session get credited to that session, and stripping the trailer from a commit message (e.g. during a squash merge) breaks `entire why`.
- **One session per commit:** running two agent sessions in the same worktree and committing their files together bundles them into one checkpoint and confuses the prompt shown by `entire why`. Use separate commits or separate `gwt` worktrees.
- **Don't push checkpoints on work repos:** Entire scrubs standard secret formats (`sk-proj-...`, AWS keys, DB URLs), but the raw ref (`0/full.jsonl`) still contains Claude Code's `<system-reminder>` block (`~/.claude/CLAUDE.md`, active skills) and won't redact plain strings like internal model names. Keep `push_sessions: false` on shared repos.

See [notes.md](./references/notes.md) for the test notes and comparison with Zed's Delta and `vals-memory`.
