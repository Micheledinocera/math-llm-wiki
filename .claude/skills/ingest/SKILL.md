---
name: ingest
description: Bring one external source from raw/sources/ into the math wiki - add its registry row, write its src- page, create or update the definitions, results and examples it proves with status cited, report notation and page conflicts, log the operation. Use when the user runs /ingest <file>.
---

# /ingest <file> — bring a source into the wiki

The rules (page types, frontmatter, statuses, reliability, agent rules) are in `CLAUDE.md`. Read it first. One source per run.

## Example

```
/ingest raw/sources/huang2019.md
```

## 1. Checks — stop if any fails

1. **One source**: the argument is one file in `raw/sources/`. Without an argument, list the sources `python scripts/lint.py` reports as not ingested and ask which one.
2. **Text**: the file must be Markdown. If it is a PDF, stop: how to convert PDFs is still open (`docs/roadmap.md`); ask the author for a Markdown version.
3. **Id**: the file name without extension is the source id (`<firstauthor><year>`). If it does not follow the convention, ask the author before going on: renaming a raw file is theirs to do.
4. **Re-ingest**: if the id is already in `wiki/registry.md`, update the existing pages in place; never create duplicates.
5. **Reliability**: ask the author when it is not certain. Book → `standard`; journal paper → `refereed`; arXiv or recent paper not yet published → `preprint`; notes, slides, blog, personal communication → `informal`. For a preprint, ask whether it has since been published.

## 2. Read

- `wiki/index.md`, `wiki/notation.md`, and the existing pages the source touches (search by key terms and likely slugs).
- The whole source.

## 3. Register and summarise

1. Append the row to `wiki/registry.md`: `| id | full citation | reliability | raw/sources/<id>.md | today |`, and update its `updated` date.
2. Create or update `wiki/sources/src-<id>.md` from `templates/source.md`: summary, extracted pages with their statement numbers, results quoted but not proved, notation map.

## 4. Pages

For each definition, result or example worth a page (granularity: results that are reused; a technical lemma used once stays inside its proof):

- Start from the template; reuse the existing page if there is one.
- **Status**: `cited` only when the source proves the result, with the statement number in the provenance anchor (`raw/sources/<id>.md#theorem-3.1`, `#p-12`). The number must appear in the source. `/ingest` is the only operation that sets `cited`, so check it here: the source gives a complete proof (not "we omit", not "see [12]"), and the page states the result faithfully (same hypotheses, same quantifiers, same conclusion, translated into `notation.md`). You check coherence with the source, not the proof's mathematics; the source's `reliability` covers that. If the source only sketches the proof: `sketch`. If it quotes the result from another work: no page; list it under *Quoted, not proved* on the `src-` page and suggest adding the original work.
- **Dependencies**: `depends_on` lists the definitions and results the statement or proof uses. A missing dependency that the same source provides gets its own page; otherwise report it.
- **Statement vs interpretation**: the body says what the source says; your comments go in **Notes** under `*Interpretation (agent):*`.
- **Notation**: write in the symbols of `notation.md`, translating the source's symbols (record the mapping on the `src-` page). A symbol missing from `notation.md`: collect a proposal for the summary and add it only after the author's ok. A symbol that conflicts: stop and report.
- **Conflicts with existing pages** (different statement, different hypotheses, different definition): keep the existing text, add a `*Conflict:*` paragraph in Notes with both provenances, list it in the summary.
- `notation_checked: true` only when every symbol on the page is in `notation.md` with the same meaning.

## 5. Close

1. Update `wiki/index.md`: one line per new page, statuses for results.
2. Add the entry to `log/changelog.md` (format in `CLAUDE.md`).
3. Run `python scripts/lint.py` and fix the mechanical errors you introduced. Leave the others for the summary.
4. Report to the author:
   - pages created and updated (slugs, statuses), with the new `cited` results listed separately so the author can review them in the diff;
   - conflicts and where they are recorded;
   - notation proposals waiting for an ok;
   - results quoted but not proved, and suggested sources;
   - lint result;
   - suggested commit message: `ingest: <id>`. Do not commit unless asked.
