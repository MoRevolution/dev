---
name: "Baseline"
description: "How I like code written and how I like to be talked to. Always on; repo-level instructions override it where they disagree."
applyTo: "**"
---

# How I like code written

This is the "code writing guide" half of my writing style guide. It gives you a sense of how I like code to look and how I like to work. Same deal as the other half: this is taste, not a rulebook, and the examples matter more than any individual rule. A repo's own AGENTS.md or copilot-instructions.md wins where the two disagree.

## The short version

**Write less code, not more. Simple, but not flat.**

**Names carry the meaning. Docs and comments say what the code can't.**

**Change what was asked. Mention the rest.**

**Find out if it worked as early as you can.**

**Talk to me like a peer.**

---

## 1. The simplest thing that actually works

The best solution is usually the one with the least code that still solves the problem properly. Before adding a config option, a base class, or a plugin point, ask whether anything needs it yet. Usually nothing does, and we pay for that generality every time someone reads the code.

> If a function is called once, it probably doesn't need to be a function yet.

Validate at the boundaries (user input, files, the edge of a library), then trust the internals.

A library or tool that "saves code" is worth it when the result is clearer or safer, not just when some parsing shrinks. Count what it adds back: the models or config it needs, import time, an image to manage, behaviour you lose. A validation library that replaces a pile of hand-written checks earns its place; a packaged proxy that needs its own image and can't do the one thing you need doesn't.

## 2. Simple doesn't mean flat

Taken too literally, "less code" gives you a 400-line script with everything inline. That isn't simple, it's just short. What I want is code that stays pleasant as it grows: a handful of well-named functions and types, each owning one idea. An abstraction earns its place when it makes the code easier to read *and* harder to misuse. If it only does one, leave it out.

Most of the readability comes from names (`fragments_per_page` over `n`). If something takes a moment to work out, try restructuring it before explaining it.

## 3. Docstrings and comments say what the code can't

A docstring earns its place when the code isn't clear on first read. It shouldn't just restate the signature.

> `"""Encode x with matrix C and return the result."""` says nothing.
> `"""z = x^T C. C is (n, n + r), so the r redundant fragments sit past index n."""` tells you a shape convention you'd otherwise have to go find.

Comments follow the same idea, only smaller: the reason, the constraint, the gotcha, usually in one line. Don't explain a change to the reviewer from inside the source; that's what the commit message is for.

A comment also isn't the place to retell something that went wrong while testing ("this failed the first time we ran it, so every later call would too"), explain a default, or say why a value lives in this file. If the name and the code already say it, write nothing. Config files follow the same rule: no header block saying what a CI workflow or Makefile target does, how long it takes, or when it runs. The names and triggers carry that.

## 4. Change what was asked

Change what I asked for. Don't refactor the neighbours, add type hints to code you didn't touch, or tidy imports in a file you were only reading. If you notice something worth fixing, mention it afterwards and let me decide.

## 5. Get the system to talk back

Work goes faster when you find out sooner whether it worked. Before building something, ask how you'll know it's right. If the answer is "run it and see," make sure you can actually run it and see. That might mean a five-line probe, a `--dry-run` flag, or printing a shape where you're unsure. If the useful logs live on a machine you can't inspect, getting access to them may be the first job.

Tests earn their place the same way docstrings do. Test behaviour you'd otherwise verify by hand, integration points where two things must agree, and cases that have broken before. A test that only asserts the obvious is padding.

Fewer, denser tests read better than many thin ones: one table-driven test beats five near-copies, and a test that only repeats what a lower-level test already checks can go.

> About to write a kernel? Write the numpy version and a comparison check first. Now every change has a yes/no answer.

## 6. Talking to me

Talk to me like a peer, not like you're writing a report. Use plain prose, light formatting, and short answers to simple questions. Say what you did, what happened, and what it means. If something didn't work, say what specifically blocked it.

Don't sell. No "powerful", "robust", "seamless", "leverage". "The kernel runs at 93% of peak bandwidth" is enough.

Parentheses or commas rather than em-dashes. Make low-consequence calls yourself and mention them after; ask about the ones that change direction. Once I've said to commit, pushing is fine. Commit messages are one line.

For commit messages and PR descriptions, load the `git-writing` skill. Draft anything I'll post (a PR body, an issue, a message to someone) in chat for me to edit first. When you hand work to another agent, pass these preferences along in the brief, since it won't have them otherwise.

For anything longer than a chat reply (READMEs, docs, notebook prose, notes), load the `writing-style` skill first.
