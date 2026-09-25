# PR examples

Here are some PR descriptions I wrote, to give you a feel for how I like them to read. Don't copy the details; notice how each one opens, how little it says about process, and where it stops.

## A refactor, opening with an honest take

> Not liking all the hand rolled parsing for manifests: lots of .get() defaults, isinstance checks, and a few one-off validators (the unknown-limits check, wrapping Network.parse, the command adapter's install/env/usage_format/provider_error checks). Also the manifests on a parse didn't reject unknown keys so they fell back to defaults.
>
> This moves all that onto small pydantic models:
>
> - Benchmark manifests, their hooks and requirements, and each dataset row are models now.
> - Each agent adapter sets SPEC to a model of its manifest (AgentSpec, MiniSweSpec, CommandSpec), and its limits model replaces LIMIT_DEFAULTS while callers read manifest.spec.
> - The evaluator's output is a model too, so "passed": "yes" is a contract error now instead of failing later when the database tries int("yes").
>
> Unknown keys, wrong types, and quoted booleans are all rejected at harness run, before anything is queued, with the file and field on one line (agent.yaml: limits.step: Extra inputs are not permitted).

A first draft of this one opened by pointing at an earlier PR, invented a typo to illustrate the problem, ended each bullet with why the result was nicer, and closed with a paragraph of line counts and timings. None of that helped a reviewer, so it went.

## A fix, problem first

> Currently when a sandbox command runs past its timeout, the harness only kills its local `docker exec` client, and the command itself lingers in the container until cleanup, taking up CPU time and changing the workspace after the agent has moved on. Whatever it printed before the timeout is lost too. Fixing that by running each timed command inside a small `sh` wrapper that writes its pid to a file, so on timeout one more `docker exec` can kill that process group. The timeout error now also keeps the last 2,000 characters of output.
>
> Two gaps are left: a timeout shorter than the wrapper's startup (about 150 ms) kills nothing, and processes that start their own session (`setsid`, daemons) escape the kill.

## A feature framed as fixing misleading data, with a small output block

> Currently the scores saved in the database mislead a bit, since they don't say how many of the benchmark's tasks were scored (or are even downloaded): a 100% on `swe-bench-verified` meant 3 of 3 local tasks, while upstream SWE-bench Verified has 500. Adding some fixes here to make that context a bit clearer. Each importer's `sources.json` now records `upstream_task_count` next to the revision it pins, and `benchmarks`, `runs`, `results`, and Grafana show it:
>
> ```text
> $ harness benchmarks
> bash-operations             5 tasks
> swe-bench-verified          3 of 500 tasks
> terminal-bench-v4           2 of 66 tasks
> ```
>
> This is the first schema change: an existing database gets the new column the first time it's opened.
>
> Closes #23.

The last paragraph stays because a reviewer needs to know their database will be migrated.

## A feature built on something that already exists

> Since the worker already stores the input and output tokens for every model call, it would be nice to see how many calls and tokens an agent spent on each task. This PR sums them from `model_calls` (no schema change): `harness results` shows calls and tokens for each task's graded attempt plus run totals, and Grafana's results table gets input and output token columns.
>
> A token here is whatever the provider reports in each response's `usage`, counted by that model's own tokenizer, so totals compare within a model but not across model families.

## More openings

- A refactor plus bug fixes: "There are currently quite a few places that decide whether a failed attempt retries: [the places]… This adds a small base class…", then "It also fixes three bugs from the same review:" and one bullet per bug.
- A follow-up cleanup: "Following up on #38. There isn't much config to speak of right now, since most settings are already CLI flags, env vars, or constants… A few of them were kind of scattered across the repo though, so this fixes those:" then bullets.
- CI: "Just updating CI here now that we've changed a couple of things, and also just looking over some of Claude's code. A few things were off:" then the problems as bullets, "This fixes those:", and the fixes as bullets.
- A feature: "Adding this to allow other agents besides `MiniSweAgent` to be used with this benchmarking tool. To do that, this PR…"
