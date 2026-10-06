# Roadmap

What is still open in v0.1: design questions, the test plan that will settle them, and the planned `/export`. The binding rules are in `CLAUDE.md`; this file holds what is not decided yet. After both tests, the rules move to v0.2 and this file is rewritten.

## Open questions

- [ ] **Granularity.** For now a page only for results that are reused; a technical lemma used once stays inside its proof. Check in the tests whether technical lemmas need their own pages.
- [ ] **PDF to Markdown.** How to convert PDF sources: decide after the first ingests, trying several tools.
- [ ] **Reliability levels.** Are the four levels enough, or should preprints be split, for example into those with and without feedback from the community?

## Test plan

Two tests in combinatorics, an area near the author's (algebra) but not the same: familiar enough to spot the agent's mistakes, far enough that the author does not work from memory. The first checks the basic mechanism, the second puts it under stress. Together they cover every status and every reliability level.

### Test 1: the Sensitivity Conjecture (Huang, 2019)

A short, elementary proof, published in the Annals of Mathematics.

| Source | Role | `reliability` |
| --- | --- | --- |
| Huang, *Induced subgraphs of hypercubes and a proof of the Sensitivity Conjecture* (2019) | main theorem | `refereed` |
| Gotsman–Linial (1992) | reduction of the conjecture to a statement on the hypercube | `refereed` |
| a linear algebra textbook | Cauchy interlacing | `standard` |
| lecture notes or an expository post on the proof | alternative presentation | `informal` |

What it checks:

- a small, complete dependency graph: hypercube, $s(f)$, $bs(f)$, signed matrix, interlacing, main theorem;
- consistent notation across sources that use different symbols;
- `/compile` of 2–3 personal ideas (for example analogues for other graphs) as `conjecture` or `sketch`;
- a short expository article written with `/draft`.

### Test 2: the bunkbed conjecture is false (Gladkov, Pak, Zimin, 2024)

A counterexample obtained by adapting to graphs a counterexample for hypergraphs (Hollom). Before the ingest, check whether the paper has been published and set `reliability` accordingly.

What it checks:

- status `refuted` and `cex-` counterexample pages;
- a longer dependency chain, from hypergraphs to graphs;
- `preprint` sources and their lint warnings;
- `partial` results, since some steps are heavy or computer-assisted and are unlikely to be checked in full.

Alternative to test 2, more probabilistic: Park–Pham, proof of the Kahn–Kalai conjecture.

### Procedure, for both tests

1. Collect the sources in `raw/sources/` and write 2–3 personal ideas in `raw/ideas/`.
2. Ingest one source at a time and check every page created by hand, noting the agent's mistakes.
3. Introduce on purpose a notation conflict and a `sketch` result used in a draft, to see whether the lint catches them.
4. Write the `plan.md` and a fragment of the article with `/draft`.
5. Record in `log/test-notes.md` what worked, what did not, and how long it took.
6. After both tests, update the rules to v0.2.

## Planned: `/export <article>`

Not in v0.1; planned after the first test. It generates the `.tex` and `.bib` in `articles/<slug>/build/` from `draft.md`:

- converts `[[...]]` links into internal references or citations;
- applies the LaTeX macros of the notation table in `wiki/notation.md`;
- attaches a report with the lint warnings still open.

The source stays the Markdown draft: fixes are made there and the article is exported again. `build/` is never edited by hand.
