---
name: lint
description: Health check of the math wiki and the articles - run scripts/lint.py for the mechanical checks, then the judgment checks (notation conflicts in wiki and drafts, definitions used before they are introduced, conjectures used as facts), and report errors and warnings without changing anything unless the author accepts the fixes. Use when the user runs /lint [article].
---

# /lint [article] — health check

The rules are in `CLAUDE.md`. Lint changes nothing on its own: it reports, proposes fixes, and applies them only after the author's ok.

## Example

```
/lint
/lint sensitivity-intro
```

With an article slug, the judgment checks focus on that article and the pages it uses; the mechanical checks always cover everything.

## 1. Mechanical checks

```bash
python scripts/lint.py
```

It prints `ERROR` and `WARN` lines and exits 1 on errors. It covers: frontmatter (fields, types, prefixes, kinds, dates), provenance present and existing, `[[...]]` links and question anchors, `depends_on` existing and acyclic, statuses not exceeding the weakest dependency, `partial` with `unchecked_steps`, `cited` with a statement anchor, `refuted` with a counterexample, pages missing from `index.md`, orphans, registry consistency, and in articles: statuses not allowed, `partial` and weak-source `cited` uses with or without a check comment, open gaps, `used_in` out of sync.

## 2. Judgment checks

Do them by reading, on the wiki pages (start from those with `notation_checked: false`) and on the drafts:

1. **Notation**: every symbol used is in `notation.md` with the same meaning; no symbol used with two meanings; no meaning with two symbols. Conflicts are **errors**.
2. **Order of definitions** in each draft: no term or symbol used before it is defined or referenced. **Error**.
3. **Conjectures** in drafts: every use of a `conjecture` result states it as a conjecture, and nothing is derived from it as a fact. **Error** if used as a fact.
4. **Source vs interpretation** (spot check): on a few `cited` pages, the anchored statement in `raw/sources/` says what the page says, and comments are under `*Interpretation (agent):*`. **Error** for a mismatch.
5. **Status drops**: if a result went down in status since its last `updated`, list every page and article that uses it (`depends_on`, `used_in`).

## 3. Report

Two sections:

- **Errors**: from the script and from the judgment checks, each with file and fix proposal.
- **Warnings**: the complete list, never truncated. Before an article is closed, the author must see all of its warnings.

Then ask which fixes to apply. After applying accepted fixes: run the script again, add a changelog entry (`lint: <what was fixed>`), update `wiki/index.md` if needed, and suggest a commit message. Never change a status to fix an error unless the author asks: lower statuses are theirs to decide too.
