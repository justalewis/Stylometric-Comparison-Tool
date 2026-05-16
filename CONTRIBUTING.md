# Contributing

Thanks for thinking about contributing. This is a small, single-author
codebase, so the workflow is informal — open an issue first if the
change is non-trivial.

---

## Development setup

```powershell
git clone https://github.com/justalewis/Stylometric-Comparison-Tool.git
cd Stylometric-Comparison-Tool

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python -m spacy download en_core_web_sm

$env:STYLOMETRIC_PASSWORD = "local-dev-only"
python app.py    # http://127.0.0.1:5050
```

The dev server runs with debug mode on and auto-reloads on edits.
Without `STYLOMETRIC_PASSWORD` set, the app fails closed with a 503 —
this is a safety property, not a bug.

---

## Project structure

Walked through in detail in [docs/architecture.md](docs/architecture.md).
The short version:

- `analyzer/` — pure Python, no Flask. Drop-in usable as a library.
  - `pipeline.py` is the orchestrator.
  - `lexical.py`, `syntactic.py`, `discourse.py`, `register.py` are the
    original 15-feature modules.
  - `aitext_signs.py` is the AI-writing-signs module.
  - `compare.py` runs the 15 comparators and produces the narrative.
  - `wordlists.py` holds every curated marker set in one place.
  - `glossary.py` holds plain-language definitions for the in-app
    tooltips and the docs/glossary.md reference.
  - `extract.py` handles uploaded-file text extraction.
  - `markdown_export.py` renders the comparison result as Markdown.
- `app.py` is the Flask layer: auth gate, routes, templates.
- `templates/` and `static/` are Jinja templates and CSS.
- `docs/` is the markdown documentation.

---

## Common kinds of changes

### Updating word lists

The most common kind of contribution. Every curated marker set lives in
`analyzer/wordlists.py`. Add entries lowercased, alphabetized within a
section, with a comment if the entry isn't obvious. Lists are
read-only at runtime so additions can't break anything else.

When updating the AI-writing-signs lists — especially the three
time-stratified vocabulary lists — open the Wikipedia source page and
follow what it currently catalogs. Note the access date in your commit
message so future maintainers know when the snapshot was taken.

### Adding a new comparison feature (16th feature, 17th...)

Follow the recipe in [docs/architecture.md](docs/architecture.md):

1. Decide which section it belongs to (lexical, syntactic, discourse,
   register, or AI-signs).
2. Add the analyzer function to the relevant module's `analyze()`
   aggregator.
3. If it uses a curated list, put it in `wordlists.py`.
4. Write a `_cmp_<feature>` comparator in `analyzer/compare.py` and
   append it to `_COMPARATORS` (skip this for AI-signs-style
   profile-only features).
5. Render it in [templates/report.html](templates/report.html) and
   [analyzer/markdown_export.py](analyzer/markdown_export.py).
6. Document the feature in [docs/methodology.md](docs/methodology.md)
   using the same "what / how / comparison rule" structure as the
   other features.
7. Add any new terms to [analyzer/glossary.py](analyzer/glossary.py)
   AND [docs/glossary.md](docs/glossary.md) — the two files mirror
   each other manually.

### Fixing a bug

If the bug is in an analyzer module, write a small reproduction first.
The `analyzer` package is pure Python and easy to exercise from a one-
liner:

```powershell
python -c "from analyzer import compare; r = compare('text a', 'text b'); print(r['comparison']['rows'][0])"
```

For app-layer bugs (auth, routing, template), the Flask test client is
the most reliable harness — see how `app.py`'s tests are exercised in
prior commits.

---

## Style

- Type hints throughout. `from __future__ import annotations` at the
  top of every module.
- Pure functions where reasonable. Modules under `analyzer/` should be
  free of I/O and global mutable state.
- Default to no comments. Add one only when the *why* is non-obvious.
- Match the existing dict-shape contract between modules. Changes to
  profile dict keys ripple through `compare.py`, `markdown_export.py`,
  and `report.html` — update all three together.
- Lowercase, alphabetized word lists. Single-word entries in `set`
  literals; multi-word phrases in `list[str]` because they're matched
  as regex sequences.

---

## Commits and pull requests

- Keep commits focused. One conceptual change per commit.
- Commit messages: short imperative-mood title (under 70 chars), then
  a blank line, then a paragraph or two explaining the *why* if the
  diff isn't self-explanatory.
- Reference any related issue or Wikipedia source section in the body.
- Test locally before pushing. The full test the maintainer runs:

  ```powershell
  STYLOMETRIC_PASSWORD=test python -c "
  import base64, app as appmod
  c = appmod.app.test_client()
  h = {'Authorization': 'Basic ' + base64.b64encode(b'user:test').decode()}
  r = c.post('/compare', headers=h, data={'text_a': '...', 'text_b': '...'},
             content_type='multipart/form-data')
  assert r.status_code == 200
  "
  ```

---

## What I'm unlikely to merge

- Anything that frames the tool as an AI detector or authorship-
  attribution system. The README, the docs, and the live UI all
  explicitly disclaim those uses, and the framing is load-bearing.
- New analyzer features that require heavy ML dependencies. spaCy
  small + regex is the whole stack and I want to keep it that way.
- Features that look identical to existing ones (TTR is already
  Section 1.1; em-dash density is already in Section 2.4).
- Breaking changes to the profile-dict contract without updating
  every consumer.

---

## Reporting issues

Open a GitHub issue with:

- What you submitted (the two text samples, or a minimal reproducer).
- What the tool reported.
- What you expected instead, and why.

For false positives or false negatives on the AI-signs metrics,
include which metric, which hits the tool flagged or missed, and what
the source text was so the curated list can be updated.

---

## License

Contributions are licensed under the same terms as the project
([GPL v3](LICENSE)). By submitting a PR you agree your contribution
can be redistributed under those terms.
