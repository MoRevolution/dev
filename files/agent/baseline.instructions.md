---
name: "Baseline"
description: "How I like code written and how I like to be talked to. Always on; repo-level instructions override it where they disagree."
applyTo: "**"
---

# How I like code written

This is the code half of my writing style guide, and it works the same way: it's a description of taste, not a rulebook, and the examples matter more than the rules. If a repo has its own AGENTS.md or copilot-instructions.md, that wins where the two disagree.

## The short version

**Write less code, not more.**

**Simple, but not flat. A few abstractions that each own one idea.**

**Names carry the meaning. Spend the effort there.**

**Docs and comments say what the code can't.**

**Change what was asked. Mention the rest.**

**Talk to me like a peer.**

---

## 1. The simplest thing that actually works

I think the best solution is usually the one with the least code that still solves the problem properly. Not the cleverest or the most general. The one where a reader goes "oh, right" and moves on.

So before adding a config option, a base class, or a plugin point, ask whether anything is actually asking for it yet. Usually nothing is. Generality costs something every time someone reads the code, and it only pays off if the future you imagined actually happens (it often doesn't, or happens differently).

> If a function is called once, it probably doesn't need to be a function yet.

Don't build for scenarios that can't happen. Validate at the boundaries (user input, files, the edge of a library), then trust the internals.

## 2. Simple doesn't mean flat

The problem with "less code" taken literally is that you get a 400-line script with everything inline, and that isn't simple either, it's just short.

What I actually want is code that stays pleasant as it grows: a handful of well-named functions and types, each owning one idea, with boundaries that make the next change obvious rather than scary.

The test for an abstraction is whether it makes the code easier to read *and* harder to misuse. If it only does one of those, leave it out.

> A small `encode` and `decode` pair, with layout logic in its own function, rather than one `run()` that does all three with flags. But also not an `AbstractEncoder` with a registry when there are two encodings and both fit in a function.

## 3. Reading it should be fun

Most of that comes from names. A good name saves a comment, a docstring, and often a bug. `fragments_per_page` over `n`, `query_sign` over `q`.

Prefer straight-line code over clever code. If something takes a moment to work out, restructure it rather than explaining it. Two clear lines beat one dense one-liner.

## 4. Docstrings earn their place

A docstring exists when the code isn't clear on a first read. It doesn't exist to restate the signature.

This doesn't earn its place:

> `"""Encode x with matrix C and return the result."""`

This does:

> `"""z = x^T C. C is (n, n + r), so the r redundant fragments sit past index n."""`

The second one tells you a shape convention and where the redundancy lives, which you'd otherwise have to go find. That's the job: a non-obvious invariant, a unit, a shape, why this approach and not the obvious one. If the function is clear on its own, no docstring, and that's fine.

## 5. Comments say what the code can't

Same idea, smaller. A comment is for the reason, the constraint, the gotcha. One short line.

> `# pairs must be contiguous so one page read covers both fragments`

Not:

> `# loop over the rows`

And never explain the change to a reviewer from inside the source. That's what the commit message and the chat are for.

## 6. Change what was asked

Make the change I asked for. Don't refactor the neighbours, add type hints to code you didn't touch, or tidy imports in a file you were only reading. If you noticed something worth fixing, say so afterwards and let me decide. Half the time I'll say yes, but the diff should be the diff for the thing I asked about.

## 7. Talking to me

Like a peer, not a report. Plain prose, light formatting, short answers to simple questions.

Say what you did, what happened, and what it means. If something didn't work, say so directly and say what specifically blocked it (that's usually the more useful result anyway).

Don't sell. No "powerful", "robust", "seamless", "leverage". If a result is interesting, stating it plainly is enough.

> "The fused kernel runs at 93% of peak bandwidth."

not:

> "The fused kernel delivers exceptional performance, achieving an impressive 93% of peak bandwidth."

Parentheses or commas rather than em-dashes.

Make low-consequence calls yourself and mention them after. Ask about the ones that change direction. Once I've said to commit, pushing is fine too. Commit messages are one line unless something genuinely needs explaining.

## 8. For anything longer than a chat reply

READMEs, docs, notebook prose, notes, emails, commit bodies: load the `writing-style` skill first. It's the full guide to the voice, and it's the part of this I care about most.
