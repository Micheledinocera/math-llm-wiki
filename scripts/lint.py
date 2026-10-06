#!/usr/bin/env python3
"""Mechanical checks on the wiki and the articles. Rules: CLAUDE.md.

Usage: python scripts/lint.py   (from any directory; no dependencies)
Exit code 1 if there are errors; warnings alone exit 0.

Checks that need judgment (notation conflicts, definitions used before they
are introduced, conjectures stated as conjectures) belong to the /lint skill.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
RAW = ROOT / "raw"
SOURCES = RAW / "sources"
IDEAS = RAW / "ideas"
ARTICLES = ROOT / "articles"
REGISTRY = WIKI / "registry.md"

SPECIAL = {"index": "index", "notation": "notation", "open-questions": "questions", "registry": "registry"}
FOLDERS = {  # folder -> (type, {slug prefix: kind})
    "definitions": ("definition", {"def-": None}),
    "results": ("result", {"lem-": "lemma", "prop-": "proposition", "thm-": "theorem", "conj-": "conjecture"}),
    "examples": ("example", {"ex-": "example", "cex-": "counterexample"}),
    "concepts": ("concept", {"con-": None}),
    "sources": ("source", {"src-": None}),
}
REQUIRED = {
    "definition": ["id", "type", "provenance", "depends_on", "used_in", "notation_checked", "updated"],
    "result": ["id", "type", "kind", "status", "provenance", "depends_on", "used_in", "notation_checked", "updated"],
    "example": ["id", "type", "kind", "provenance", "depends_on", "used_in", "notation_checked", "updated"],
    "concept": ["id", "type", "provenance", "updated"],
    "source": ["id", "type", "source_id", "citation", "reliability", "provenance", "ingested", "updated"],
}
LIST_FIELDS = {"provenance", "depends_on", "used_in", "unchecked_steps", "illustrates", "refutes"}
RANK = {"refuted": 0, "conjecture": 1, "sketch": 2, "proposed": 3, "partial": 4, "cited": 5, "verified": 5}
ARTICLE_OK = {"cited", "verified"}
ARTICLE_WARN = {"partial", "conjecture"}
RELIABILITY = {"standard", "refereed", "preprint", "informal"}
WEAK_RELIABILITY = {"preprint", "informal"}

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IDEA_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*\.md$")
FRONTMATTER = re.compile(r"^---\r?\n(.*?)\r?\n---[ \t]*(\r?\n|$)", re.S)
LINK = re.compile(r"\[\[([^\]|#]*)(?:#([^\]|]*))?(?:\|[^\]]*)?\]\]")
COMMENT = re.compile(r"<!--(.*?)-->", re.S)
QUESTION = re.compile(r"^## (q-[a-z0-9]+(?:-[a-z0-9]+)*)\s*$", re.M)

errors: list[str] = []
warnings: list[str] = []


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def error(path: Path, msg: str) -> None:
    errors.append(f"{rel(path)}: {msg}")


def warn(path: Path, msg: str) -> None:
    warnings.append(f"{rel(path)}: {msg}")


# --- parsing ----------------------------------------------------------------


def strip_comment(value: str) -> str:
    return re.sub(r"\s+#.*$", "", value).strip()


def unquote(value: str) -> str:
    return re.sub(r"^([\"'])(.*)\1$", r"\2", value)


def parse(text: str) -> tuple[dict | None, str]:
    """Flat YAML frontmatter: scalars, inline lists [a, b] and block lists."""
    m = FRONTMATTER.match(text)
    if not m:
        return None, text
    data: dict = {}
    list_key = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and list_key:
            data[list_key].append(unquote(strip_comment(item.group(1))))
            continue
        kv = re.match(r"^([\w-]+):\s*(.*)$", line)
        if not kv:
            list_key = None
            continue
        key, value = kv.group(1), strip_comment(kv.group(2))
        if value == "":
            data[key], list_key = [], key
        elif value.startswith("[") and value.endswith("]"):
            data[key] = [unquote(s.strip()) for s in value[1:-1].split(",") if s.strip()]
            list_key = None
        else:
            data[key], list_key = unquote(value), None
    return data, text[m.end():]


def as_list(value) -> list[str]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def strip_code_and_math(text: str) -> str:
    text = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
    return re.sub(r"(?<!\\)\$[^$\n]+?(?<!\\)\$", "", text)


def links(text: str) -> list[tuple[str, str | None]]:
    return [(m.group(1).strip(), m.group(2)) for m in LINK.finditer(strip_code_and_math(text))]


# --- collect ----------------------------------------------------------------


class Page:
    def __init__(self, path: Path, ptype: str, prefixes: dict):
        self.path = path
        self.slug = path.stem
        self.ptype = ptype
        self.prefixes = prefixes
        self.fm, self.body = parse(path.read_text(encoding="utf-8"))
        self.fm = self.fm or {}

    def get(self, key: str) -> list[str]:
        return as_list(self.fm.get(key))

    @property
    def status(self) -> str | None:
        status = self.fm.get("status")
        return status if isinstance(status, str) else None


if not WIKI.is_dir():
    print("wiki/ not found next to scripts/.", file=sys.stderr)
    sys.exit(2)

pages: dict[str, Page] = {}
special: dict[str, tuple[Path, dict | None, str]] = {}

for path in sorted(WIKI.rglob("*.md")):
    parts = path.relative_to(WIKI).parts
    if len(parts) == 1 and path.stem in SPECIAL:
        fm, body = parse(path.read_text(encoding="utf-8"))
        special[path.stem] = (path, fm, body)
    elif len(parts) == 2 and parts[0] in FOLDERS:
        ptype, prefixes = FOLDERS[parts[0]]
        page = Page(path, ptype, prefixes)
        if page.slug in pages:
            error(path, f"duplicate slug '{page.slug}' (also {rel(pages[page.slug].path)})")
        pages[page.slug] = page
    else:
        error(path, "unexpected location: wiki pages live in " + ", ".join(f"wiki/{f}/" for f in FOLDERS))

for stem, ptype in SPECIAL.items():
    if stem not in special:
        error(WIKI / f"{stem}.md", "missing")
        continue
    path, fm, _ = special[stem]
    if fm is None:
        error(path, "missing frontmatter")
    else:
        if fm.get("type") != ptype:
            error(path, f"type must be '{ptype}'")
        if not DATE.match(str(fm.get("updated", ""))):
            error(path, "updated must be a YYYY-MM-DD date")

questions: set[str] = set()
if "open-questions" in special:
    path, _, body = special["open-questions"]
    sections = QUESTION.split(body)
    for i in range(1, len(sections), 2):
        anchor, content = sections[i], sections[i + 1]
        if anchor in questions:
            error(path, f"duplicate question anchor '{anchor}'")
        questions.add(anchor)
        if "**Provenance.**" not in content:
            error(path, f"question '{anchor}' has no **Provenance.** line")
    for line in body.splitlines():
        if line.startswith("## ") and not QUESTION.match(line):
            error(path, f"heading '{line}' is not a valid q-<slug> anchor")

registry: dict[str, list[str]] = {}
if "registry" in special:
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells[0] or cells[0] == "id" or set(cells[0]) <= set("-: "):
            continue
        registry[cells[0]] = cells


def resolve(slug: str) -> bool:
    return slug in pages or slug in SPECIAL


# --- page checks ------------------------------------------------------------

for page in pages.values():
    fm, path = page.fm, page.path
    if not fm:
        error(path, "missing frontmatter")
        continue
    for key in REQUIRED[page.ptype]:
        value = fm.get(key)
        if key not in fm:
            error(path, f"missing field '{key}'")
        elif key not in LIST_FIELDS and value == []:
            error(path, f"empty field '{key}'")
    for key in LIST_FIELDS & fm.keys():
        if not isinstance(fm[key], list):
            error(path, f"'{key}' must be a list")

    if fm.get("id") != page.slug:
        error(path, f"id '{fm.get('id')}' must equal the file name '{page.slug}'")
    if fm.get("type") != page.ptype:
        error(path, f"type '{fm.get('type')}' must be '{page.ptype}' in this folder")
    prefix = next((p for p in page.prefixes if page.slug.startswith(p)), None)
    if prefix is None:
        error(path, "slug prefix must be one of " + ", ".join(page.prefixes))
    elif page.prefixes[prefix] and fm.get("kind") != page.prefixes[prefix]:
        error(path, f"kind '{fm.get('kind')}' does not match the prefix '{prefix}' ({page.prefixes[prefix]})")
    if page.slug != page.slug.lower() or " " in page.slug:
        error(path, "slug must be lowercase with hyphens")
    for key in ("updated", "ingested"):
        if key in fm and not DATE.match(str(fm[key])):
            error(path, f"{key} must be a YYYY-MM-DD date")
    if "notation_checked" in fm and fm["notation_checked"] not in ("true", "false"):
        error(path, "notation_checked must be true or false")

    # provenance
    provenance = page.get("provenance")
    if not provenance:
        error(path, "no provenance")
    for entry in provenance:
        target = entry.split("#", 1)[0]
        if entry.startswith("raw/"):
            if not (ROOT / target).is_file():
                error(path, f"provenance file not found: {target}")
            elif not (target.startswith("raw/sources/") or target.startswith("raw/ideas/")):
                error(path, f"provenance must point to raw/sources/ or raw/ideas/: {entry}")
        elif not resolve(entry):
            error(path, f"provenance is neither a raw/ file nor a wiki slug: {entry}")

    for dep in page.get("depends_on"):
        if dep == page.slug:
            error(path, "depends on itself")
        elif dep not in pages:
            error(path, f"depends_on: page not found: {dep}")
    for key in ("illustrates", "refutes"):
        for slug in page.get(key):
            if slug not in pages:
                error(path, f"{key}: page not found: {slug}")
    for article in page.get("used_in"):
        if not re.match(r"^articles/[^/]+$", article) or not (ROOT / article).is_dir():
            error(path, f"used_in: article not found: {article}")

    # results
    if page.ptype == "result":
        status = page.status
        if status not in RANK:
            error(path, f"status '{status}' is not one of " + ", ".join(RANK))
        if status == "partial" and not page.get("unchecked_steps"):
            error(path, "status partial needs unchecked_steps")
        if status != "partial" and page.get("unchecked_steps"):
            warn(path, "unchecked_steps is only meaningful for status partial")
        if status == "cited" and not any(p.startswith("raw/sources/") and "#" in p and p.split("#", 1)[1] for p in provenance):
            error(path, "status cited needs a provenance raw/sources/<id>.md#<statement>")
        if status == "refuted":
            linked = any(t.startswith("cex-") or t.startswith("ex-") for t, _ in links(page.body))
            refuter = any(page.slug in other.get("refutes") for other in pages.values())
            if not (linked or refuter):
                error(path, "status refuted needs a link to its counterexample, or an example page that refutes it")

    if page.ptype == "example":
        for slug in page.get("refutes"):
            target = pages.get(slug)
            if target and target.ptype == "result" and target.status != "refuted":
                error(path, f"refutes {slug}, whose status is '{target.status}', not refuted")

    if page.ptype == "source":
        reliability = fm.get("reliability")
        if reliability not in RELIABILITY:
            error(path, f"reliability '{reliability}' is not one of " + ", ".join(sorted(RELIABILITY)))
        source_id = fm.get("source_id")
        if page.slug != f"src-{source_id}":
            error(path, f"slug must be src-{source_id}")
        if not any(p.split("#", 1)[0] == f"raw/sources/{source_id}.md" for p in provenance):
            warn(path, f"provenance does not include raw/sources/{source_id}.md")
        row = registry.get(str(source_id))
        if row is None:
            error(path, f"source '{source_id}' is not in wiki/registry.md")
        elif len(row) > 2 and row[2] != reliability:
            error(path, f"reliability '{reliability}' differs from the registry ('{row[2]}')")

# --- links, index, orphans --------------------------------------------------

inbound: dict[str, set[str]] = {slug: set() for slug in pages}


def check_links(path: Path, text: str, source: str | None) -> None:
    for target, anchor in links(text):
        if "/" in target or target.endswith(".md"):
            error(path, f"link [[{target}]]: use the bare slug")
        elif not resolve(target):
            error(path, f"broken link [[{target}]]")
        elif target == "open-questions" and anchor and anchor not in questions:
            error(path, f"broken link [[open-questions#{anchor}]]")
        elif source and target in inbound and target != source:
            inbound[target].add(source)


for page in pages.values():
    check_links(page.path, page.body, page.slug)
    for key in ("depends_on", "illustrates", "refutes"):
        for slug in page.get(key):
            if slug in inbound and slug != page.slug:
                inbound[slug].add(page.slug)
for stem, (path, _, body) in special.items():
    check_links(path, body, None if stem == "index" else stem)

if "index" in special:
    path, _, body = special["index"]
    listed = {target for target, _ in links(body)}
    for slug, page in pages.items():
        if slug not in listed:
            error(page.path, "missing from wiki/index.md")

for slug, page in pages.items():
    if page.ptype != "source" and not inbound[slug] and not page.get("used_in"):
        warn(page.path, "orphan: no other page links to it or depends on it")

# --- dependency graph -------------------------------------------------------

state: dict[str, int] = {}  # 1 visiting, 2 done
reported: set[frozenset] = set()


def visit(slug: str, stack: list[str]) -> None:
    state[slug] = 1
    stack.append(slug)
    for dep in pages[slug].get("depends_on"):
        if dep not in pages or dep == slug:
            continue
        if state.get(dep) == 1:
            cycle = stack[stack.index(dep):] + [dep]
            key = frozenset(cycle)
            if key not in reported:
                reported.add(key)
                error(pages[dep].path, "circular dependency: " + " -> ".join(cycle))
        elif dep not in state:
            visit(dep, stack)
    stack.pop()
    state[slug] = 2


for slug in pages:
    if slug not in state:
        visit(slug, [])

def weakest(slug: str) -> tuple[int, str] | None:
    """Weakest (rank, slug) among the results slug depends on, transitively."""
    best, seen, queue = None, {slug}, list(pages[slug].get("depends_on"))
    while queue:
        dep = queue.pop()
        if dep in seen or dep not in pages:
            continue
        seen.add(dep)
        queue.extend(pages[dep].get("depends_on"))
        status = pages[dep].status
        if pages[dep].ptype == "result" and status in RANK and (best is None or RANK[status] < best[0]):
            best = (RANK[status], dep)
    return best


for slug, page in pages.items():
    if page.ptype != "result" or page.status not in RANK or page.status == "refuted":
        continue
    weak = weakest(slug)
    if weak and RANK[page.status] > weak[0]:
        dep_status = pages[weak[1]].status
        error(page.path, f"status '{page.status}' exceeds its weakest dependency: {weak[1]} ({dep_status})")

# --- articles ---------------------------------------------------------------


def reliability_of(page: Page) -> set[str]:
    """Reliability levels of the raw/sources files a cited result comes from."""
    levels = set()
    for entry in page.get("provenance"):
        target = entry.split("#", 1)[0]
        if not target.startswith("raw/sources/"):
            continue
        source_id = Path(target).stem
        src = pages.get(f"src-{source_id}")
        levels.add(src.fm.get("reliability", "unknown") if src else "unknown")
    return levels


if ARTICLES.is_dir():
    for folder in sorted(p for p in ARTICLES.iterdir() if p.is_dir()):
        name = f"articles/{folder.name}"
        plan, draft = folder / "plan.md", folder / "draft.md"
        if not plan.is_file():
            error(folder, "missing plan.md")
        else:
            text = plan.read_text(encoding="utf-8")
            check_links(plan, text, None)
            for target, _ in links(text):
                page = pages.get(target)
                if page and page.ptype == "result" and page.status not in ARTICLE_OK | ARTICLE_WARN:
                    warn(plan, f"plans to use [[{target}]], status '{page.status}' is not usable in an article")
        if not draft.is_file():
            continue
        text = draft.read_text(encoding="utf-8")
        check_links(draft, text, None)
        comments = [c.strip() for c in COMMENT.findall(text)]
        checks = [c for c in comments if c.startswith("check:")]
        for gap in (c for c in comments if c.startswith("gap:")):
            warn(draft, f"open gap: {gap[4:].strip()}")
        used = {target for target, _ in links(COMMENT.sub("", text))}
        for target in sorted(used):
            page = pages.get(target)
            if not page:
                continue
            if page.ptype in ("definition", "result", "example") and name not in page.get("used_in"):
                warn(page.path, f"used in {name} but used_in does not list it")
            if page.ptype != "result":
                continue
            status = page.status
            has_check = any(target in c for c in checks)
            if status not in ARTICLE_OK | ARTICLE_WARN:
                error(draft, f"uses [[{target}]], status '{status}' is not allowed in an article")
            elif status == "conjecture":
                warn(draft, f"uses [[{target}]] (conjecture): allowed only as a declared conjecture")
            elif status == "partial":
                warn(draft, f"uses [[{target}]] (partial)" + ("" if has_check else ", missing <!-- check --> comment"))
            elif status == "cited":
                levels = reliability_of(page)
                if "unknown" in levels:
                    error(draft, f"uses [[{target}]] (cited), but its source has no src- page")
                weak = levels & WEAK_RELIABILITY
                if weak:
                    warn(draft, f"uses [[{target}]] (cited from a {'/'.join(sorted(weak))} source)"
                         + ("" if has_check else ", missing <!-- check --> comment"))
        for page in pages.values():
            if name in page.get("used_in") and page.slug not in used:
                warn(page.path, f"used_in lists {name}, but its draft does not link it")

# --- raw --------------------------------------------------------------------

if IDEAS.is_dir():
    for path in sorted(IDEAS.glob("*.md")):
        if not IDEA_NAME.match(path.name):
            warn(path, "idea file name should be YYYY-MM-DD-title.md")
if SOURCES.is_dir():
    for path in sorted(SOURCES.glob("*.md")):
        if path.stem not in registry:
            warn(path, "source not ingested yet (not in the registry)")
for source_id in registry:
    if f"src-{source_id}" not in pages:
        warn(REGISTRY, f"source '{source_id}' has no wiki/sources/src-{source_id}.md page")

# --- report -----------------------------------------------------------------

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass
for line in errors:
    print(f"ERROR {line}")
for line in warnings:
    print(f"WARN  {line}")
print(f"\n{len(pages)} pages, {len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
