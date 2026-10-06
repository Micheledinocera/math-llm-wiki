# Changelog

Log of the agent's operations. Format: `CLAUDE.md`, section *Changelog*.

## Ready for verification

Results with status `proposed` whose proof the agent considers complete. The author checks them and sets `partial` or `verified`; the agent removes the line when the status changes.

None.

## Log

### 2026-10-06 — source registry moved to the wiki

- `raw/sources/_registry.md` → `wiki/registry.md`: the registry is maintained by the agent, so `raw/` stays fully immutable. Spec, `CLAUDE.md`, `/ingest`, `scripts/lint.py` and README updated.

### 2026-10-06 — bootstrap

- Repository created from `docs/spec-v0.1.md`: folders, `CLAUDE.md`, templates, skills, `scripts/lint.py`. No mathematical content.
