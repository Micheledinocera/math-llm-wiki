---
name: query
description: Answer a mathematical question from the math wiki - read wiki/index.md first, then the linked pages, cite the slugs and statuses used, and offer to save new material as a wiki page. Read-only unless the author accepts the new page. Use when the user runs /query <question>.
---

# /query <question> — answer from the wiki

The rules are in `CLAUDE.md`. A query reads the wiki; it changes it only if the author accepts saving a new page.

## Example

```
/query Does the main theorem still hold for induced subgraphs of other Cayley graphs?
```

## 1. Find

1. Read `wiki/index.md`, then the pages that look relevant, following `depends_on` and links as needed. Read `notation.md` for the symbols.
2. Go to `raw/` only to check a precise point of a page (a statement number, a hypothesis).

## 2. Answer

- Use the notation of `notation.md`.
- Cite every page used as `[[slug]]`, with its status for results: "by [[thm-x]] (verified)".
- Say clearly when the answer rests on results that are not `cited` or `verified`, and which ones.
- If the wiki does not contain the answer, say so. You may add general knowledge, marked as **not in the wiki**, and suggest which source to add to `raw/sources/` to back it.
- Keep the source/interpretation separation: what the pages say vs your reasoning.

## 3. Offer to save

If the answer produces new material (a proof, a reformulation, an example, a connection, a question), propose a page: type, slug, status, provenance. Do not write it until the author says yes.

When the author accepts:

- **Status**: a complete proof you wrote is `proposed`; an argument with gaps is `sketch`; a claim without proof is `conjecture`. Never higher, and never above the weakest dependency.
- **Provenance**: the slugs of the pages the answer is derived from (and `raw/` files, if used).
- A question goes into `wiki/open-questions.md`.
- If a `proposed` proof looks complete, add it to *Ready for verification* in `log/changelog.md`.
- Update `wiki/index.md`, add a changelog entry (`query: <short question>`), run `python scripts/lint.py`, and suggest a commit message. Do not commit unless asked.
