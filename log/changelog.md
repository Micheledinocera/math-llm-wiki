# Changelog

Log of the agent's operations. Format: `CLAUDE.md`, section *Changelog*.

## Ready for verification

Results with status `proposed` whose proof the agent considers complete. The author checks them and sets `partial` or `verified`; the agent removes the line when the status changes.

None.

## Log

### 2026-10-06 — spec retired

- `docs/spec-v0.1.md` removed: the rules live only in `CLAUDE.md`; open questions, test plan and the planned `/export` moved to `docs/roadmap.md` (in English).
- `cited` is set only by `/ingest`, which checks that the source proves the result and that the page states it faithfully; no separate confirmation by the author. `CLAUDE.md` and `/ingest` updated.
- Conjectures in articles: allowed only as declared conjectures, listed among the lint warnings (rule 9 aligned with the statuses table).
- README points to `docs/roadmap.md`.

### 2026-10-06 — source registry moved to the wiki

- `raw/sources/_registry.md` → `wiki/registry.md`: the registry is maintained by the agent, so `raw/` stays fully immutable. Spec, `CLAUDE.md`, `/ingest`, `scripts/lint.py` and README updated.

### 2026-10-06 — bootstrap

- Repository created from `docs/spec-v0.1.md`: folders, `CLAUDE.md`, templates, skills, `scripts/lint.py`. No mathematical content.
