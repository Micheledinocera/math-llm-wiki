---
name: draft
description: Work on an article in articles/<slug>/ - create its plan.md with the author, then write or revise draft.md in Markdown using only results allowed in articles, with check and gap comments, notation from notation.md, and used_in kept in sync on the wiki pages. Use when the user runs /draft <article> [instruction].
---

# /draft <article> [instruction] — work on an article

The rules are in `CLAUDE.md`, especially the statuses table and rule 9. The article is the shop window: it draws from the wiki, it does not produce new mathematics.

## Example

```
/draft sensitivity-intro
/draft sensitivity-intro write section 2 from the outline
```

## 1. Plan

If `articles/<slug>/plan.md` does not exist, create it from `templates/article-plan.md` together with the author: ask for the goal and the audience, then propose the outline and the results used, picked from `wiki/index.md`. Do not write the draft in the same run unless the author asks.

If the plan exists, read it. The instruction says what to do (a section, a revision); without one, ask.

## 2. Check the material

For every result the work needs, read its page and status:

| Status | In the draft |
| --- | --- |
| `cited`, `verified` | use it, with `[[slug]]` where it is used; for `cited`, the citation |
| `cited` from a `preprint` or `informal` source | use it, and add `<!-- check: [[slug]] source is <reliability> -->` |
| `partial` | use it, and add `<!-- check: [[slug]] unchecked: <steps> -->` |
| `conjecture` | only stated as a conjecture, never used as a fact |
| `sketch`, `proposed`, `refuted` | do not use: write `<!-- gap: [[slug]] is <status> -->` and report it |

A result the article needs and that the wiki does not have: do not prove it in the draft. Write a gap and suggest how it enters the wiki first (`/compile` of an idea, `/query` for a proposed proof, `/ingest` of a source).

## 3. Write

- `draft.md` is Markdown with LaTeX (`$...$`, `$$...$$`), starting with a frontmatter `article`, `title`, `updated`.
- Use the notation of `notation.md`. Deviations must be agreed with the author and listed in the plan.
- Introduce every definition before its first use (or point to where the reader finds it).
- Keep the `[[slug]]` links where results and definitions are used: they are the traceability that `/lint` and the future export use.
- Write the requested part only; do not rewrite other sections without being asked.

## 4. Sync and close

1. Add `articles/<slug>` to `used_in` of every page the draft now links; remove it from pages it no longer links.
2. Update the plan's *Open gaps* and *Results used* if they changed.
3. Add the entry to `log/changelog.md` (`draft <slug>: <what changed>`).
4. Run `python scripts/lint.py` and fix the mechanical errors you introduced.
5. Report: what was written, gaps, check comments added, lint warnings for this article, suggested commit message `draft: <slug>`. Do not commit unless asked.
