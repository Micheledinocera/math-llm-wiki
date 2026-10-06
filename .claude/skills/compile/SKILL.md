---
name: compile
description: Bring one of the author's ideas from raw/ideas/ into the math wiki - definitions, results as conjecture or sketch, open questions, with provenance in raw/ideas/ - report conflicts, log the operation. Use when the user runs /compile <idea>.
---

# /compile <idea> — bring an idea into the wiki

Like `/ingest`, but for the author's ideas: they are not facts. The rules are in `CLAUDE.md`; read it first. One idea per run.

## Example

```
/compile raw/ideas/2026-10-06-other-graphs.md
```

## 1. Checks — stop if any fails

1. **One idea**: the argument is one file in `raw/ideas/`. Without an argument, list the ideas not yet referenced by any page's provenance and ask which one.
2. **Name**: `YYYY-MM-DD-title.md`. If not, ask the author to rename it (raw files are theirs to change).
3. **Re-compile**: if pages already cite this idea in their provenance, update them in place.

## 2. Read

- `wiki/index.md`, `wiki/notation.md`, the pages the idea refers to.
- The whole idea. If it is ambiguous (which hypothesis, which object), ask before writing; do not choose a reading on the author's behalf.

## 3. Pages

- **Results**: `conjecture` when the idea states something without a proof, `sketch` when it gives a proof idea. Never `cited`, never `proposed`: compile does not write proofs. If the author wants one, they ask for it (via `/query`), and it enters as `proposed`.
- **Status vs dependencies**: a result cannot be stronger than its weakest dependency, which here is rarely a problem; still check that `depends_on` lists the wiki pages the idea relies on.
- **Definitions** introduced by the idea: a `def-` page with provenance in `raw/ideas/`.
- **Questions**: a question without a proposed answer becomes a `## q-<slug>` section in `wiki/open-questions.md` (`templates/question.md`), with the idea as provenance.
- **Provenance**: the idea file, plus the slugs of the wiki pages it builds on.
- **Interpretation**: what you add (a reformulation, a link the author did not make) goes in Notes under `*Interpretation (agent):*`.
- **Notation and conflicts**: as in `/ingest`. An idea that contradicts a `cited` or `verified` page is worth flagging clearly: record the `*Conflict:*` and report it first in the summary.

## 4. Close

1. Update `wiki/index.md` and add the entry to `log/changelog.md`.
2. Run `python scripts/lint.py` and fix the mechanical errors you introduced.
3. Report: pages created and updated with statuses, questions added, conflicts, notation proposals, lint result, suggested commit message `compile: <idea file name>`. Do not commit unless asked.
