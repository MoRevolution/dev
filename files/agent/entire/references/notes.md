# Notes on Entire CLI and Delta

I tested Entire CLI (`entire 0.12.2`) and looked into Zed's Delta (`delta 0.22.0`) on `/Users/morevolution/projects/entire-demo` and `/Users/morevolution/projects/entire-secret-test` to see where they fit alongside `vals-memory`.

At first they sound like the same kind of tool, but they record different things:
- **`vals-memory`** is curated durable knowledge: someone has to explicitly retain a fact or debugging finding. High signal, but it doesn't capture ordinary day-to-day PR context.
- **Entire CLI** is commit-linked provenance: it hooks into your local agent and git, adds an `Entire-Checkpoint: <id>` trailer on commit, and saves the prompt, tool calls, and transcript under `refs/entire/checkpoints/*`.
- **Delta (DeltaDB)** is live state between commits: it streams every file edit and Claude Code turn as CRDT deltas to Cloudflare so someone else can join your uncommitted checkout mid-turn.

For local work across Claude Code, OpenCode, and Devin, Entire is the practical one because it sits on top of normal git worktrees rather than asking you to use a new app.

## What worked

- **`entire why <file>:<line>`:** Session 1 wrote `rate_limit.py` (token bucket over sliding window because benchmark runs burst) and Session 2 added `reset()`. `entire why rate_limit.py` split the file into 22 lines from Session 1 and 6 from Session 2, and `entire why rate_limit.py:24` pulled up the exact prompt for `reset()`.
- **Zero-setup on fresh clones (when checkpoints are pushed):** A plain `git clone` into `/tmp` without running `entire enable` still resolved `entire why rate_limit.py` by lazily fetching `refs/entire/checkpoints/*` from `origin`.
- **`entire search`:** Once `MoRevolution/entire-demo` was mirrored (`entire repo mirror add`, ~30s initial indexing), `entire search "why token bucket instead of sliding window" --compact` matched the session prompt directly. (In the interactive TUI, it opens on `< Commits >` first; hit `Tab` or `->` to see `Sessions`.)
- **`entire session tokens <id>`:** Shows input, output, cache read (80.8% on a short Claude session), and cache write tokens, and flags when cache replay is dominating.
- **Overhead:** 5 checkpoints across 6 sessions took `836 KB` in `.git` and `412 KB` in `.entire`.

## What broke or needs care

- **Commit-based attribution:** Hand-editing a line before committing Session 2's edit caused `entire why` to attribute my line to Session 2 as well. Underneath, it just maps `git blame` -> commit SHA -> `Entire-Checkpoint:` trailer rather than diffing what the agent's tools touched.
- **Squash merges:** When PR #1 was merged with `gh pr merge --squash`, GitHub's default bullet list kept all three `Entire-Checkpoint:` trailers in the commit body, so `entire why retry.py` and `entire why metrics.py` still worked on `main` (though `entire checkpoint list` only read the first trailer). If you strip the commit body for a single-line squash message, the trailers are gone and `entire why` loses the link.
- **Concurrent sessions in one commit:** Two `claude -p` jobs run at the same time in one worktree and committed together got bundled into one checkpoint, and `entire why` on the second file printed the first session's prompt. Separate commits or `gwt` worktrees avoid this.
- **What lives in the git ref:** In `entire-secret-test`, Entire scrubbed fake OpenAI, AWS, and Postgres credentials across the ref (21 replacements via `betterleaks` and entropy checks). However, `0/full.jsonl` inside the ref still stores Claude Code's `<system-reminder>` block verbatim (including `~/.claude/CLAUDE.md` and active skills) and won't redact plain strings like internal/EAP model names.
  - For personal local use on work repos, `entire-local` sets `push_sessions: false` so refs never leave the machine.
  - For team-wide sharing on internal repos, `--checkpoint-remote` should point at a separate private repo rather than `origin`.
- **Devin support:** Built-in capture covers `claude-code`, `codex`, `cursor`, `copilot-cli`, `factoryai-droid`, `opencode`, `pi`, and `antigravity` (not Devin yet, though Devin can query existing checkpoints via the `entire` skill).
