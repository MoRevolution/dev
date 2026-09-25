---
name: git-writing
description: "How I write commit messages and pull request descriptions, and how I like PR commits kept. Use when writing or editing a commit message, a PR title or body, or when revising the commits on a PR."
---

# Commits and PRs

## The short version

**A PR says why it exists, what changed, and anything a reviewer has to act on. Nothing else.**

**Commits are small, named for what they change, and fixed in place.**

## Commits

- Conventional Commits prefix (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `ci:`, `build:`, `chore:`, `perf:`), then what changed in plain words: `fix: stop the worker when its last task fails`.
- One line by default. Add a short body only when the why isn't obvious from the subject and the diff: the problem, its cause, the fix.
- One logical change per commit.
- When revising a PR, fold the fix into the commit that introduced the problem (`git commit --fixup <sha>`, then `git rebase -i --autosquash`) instead of stacking "address review" commits on top.

## PR descriptions

Open with the reason, and vary how:

- an honest take on the problem: "Not liking all the hand-rolled parsing here: …"
- the problem and its cause: "Currently when a command runs past its timeout, only the client gets killed and the process keeps running…", then "Fixing that by…"
- the purpose: "Adding this so other backends can be used with the tool. To do that, this PR…"
- something that already exists: "Since we already store every request, it would be nice to…"

Don't start every PR the same way. Say how things were before, plainly, without inventing an example to illustrate it.

Then say what changes: a sentence or two, or bullets when there's a real set of parallel changes (a list of distinct problems, or of fixes). Bullets say what changed. They don't need a tail about why it's nicer now.

Leave out:

- a list of what each commit does
- a "tests pass" line
- line counts, timings, and small behaviour trivia (those belong in your reply to me, not the PR)
- caveats a reviewer doesn't need to act on

Keep a caveat when the reviewer has to do something about it: a migration, a manual cleanup, a flag that changed meaning. Add evidence (a small table, a CLI output block, a screenshot) only when it shows what the change does.

Be precise about where a setting or behaviour lives (per project or per task, a default or an override). Casual and plain is right, first person is fine, and so is saying an agent wrote some of the code.

Draft the text in chat for me to edit before posting it.

## Examples

[pr_examples.md](./references/pr_examples.md) has PR descriptions I wrote. For shape, Mitchell Hashimoto's merged PRs in `ghostty-org/ghostty` and the ones in `astral-sh/uv` are good references: context and cause in a paragraph, the fix in the next, then `Closes #N`.

## Keeping it current

If I keep rewriting the same part of your drafts, this file is missing a preference. Point it out and offer to update it.
