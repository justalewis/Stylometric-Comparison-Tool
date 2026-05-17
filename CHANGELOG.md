# Changelog

All notable changes to this project are listed below in reverse
chronological order. Versions use loose semver — minor versions add
features, patch versions are bug fixes.

---

## [Unreleased]

### Added
- `docs/install.md` — plain-language walkthrough for installing the
  tool on your own machine. Covers prerequisites, virtual
  environments, dependencies, common errors.
- `docs/deploy.md` — plain-language walkthrough for deploying a
  fork to Fly.io. Covers flyctl install, app naming, region
  selection, custom domains, optional re-adding of auth, cost
  expectations, common errors.

### Changed
- Renamed `docs/deployment.md` to `docs/operations.md` to reflect
  what its content actually covers (maintenance of an already-
  deployed instance) and to make room for the new `deploy.md`
  walkthrough. References updated in README and elsewhere.

### Removed
- HTTP Basic Auth gate. The tool is now publicly accessible — no
  `STYLOMETRIC_PASSWORD` required. The `@app.before_request` handler,
  `_credentials_ok` helper, and the two `STYLOMETRIC_USERNAME` /
  `STYLOMETRIC_PASSWORD` environment-variable reads are deleted.
  README, FAQ, operations.md, and architecture.md updated to reflect
  public access. To re-introduce authentication later, restore the
  removed handler from git history.

### Added
- `templates/glossary.html` and `/glossary` route — an in-app reference
  page reachable from the form and the report. Walks through every
  metric the tool produces (4 lexical, 4 syntactic, 4 discourse, 3
  register, 4 comparison ratings, 8 AI-writing signs) with plain-
  language definitions and side-by-side example blocks.
- `CONTRIBUTING.md` — development setup, contribution recipe, style
  conventions.
- `docs/pedagogy.md` — instructor's guide for using the tool in
  writing classrooms (the framing the tool was built to support).
- `docs/faq.md` — common questions about use cases, methodology,
  privacy, and licensing.
- `docs/examples.md` — two end-to-end worked comparisons with real
  numbers, including an AI-flavored sample that exercises all eight
  AI-writing-signs metrics.
- `CHANGELOG.md` — this file.

---

## [0.3.0] — 2026-05-16

### Added
- Section 6 of the report: eight AI-writing-signs metrics drawn from
  Wikipedia's *Signs of AI writing* catalog. Profile-only (no
  comparator ratings); each metric reports raw count, per-500w rate,
  top hits, and a deep link to its Wikipedia source section.
  - AI vocabulary density (three time-stratified lists: 2023–mid-2024,
    mid-2024–mid-2025, mid-2025+).
  - Promotional / advertisement-like phrasing.
  - Significance / legacy emphasis.
  - Vague attribution patterns.
  - Negative parallelisms ("not just X but Y", "not only…but also").
  - Participial pseudo-analysis (sentences ending in `, highlighting…`
    / `, ensuring…` clauses).
  - Rule of three (three-item parallel lists with shared POS).
  - Conclusion / outlook formulas.
- Inline glossary tooltips on report pages. ~50 plain-language
  definitions exposed as dotted-underlined hover/focus tooltips
  throughout the per-text profiles and the comparison table.
  `analyzer/glossary.py` is the single source; same content lives in
  `docs/glossary.md` as long-form reference.
- `docs/ai-signs.md` — methodology for the eight new metrics, the
  Wikipedia crosswalk for each, what's deliberately not implemented
  and why, and calibration guidance.
- `docs/glossary.md` — plain-language definitions for every term used
  in the report.
- Wikipedia crosswalk table in `docs/methodology.md` showing where the
  original fifteen features overlap with signs from the catalog.

### Changed
- `analyzer/pipeline.py` now calls `aitext_signs.analyze()` and
  includes `ai_signs` in the per-text profile dict.
- `analyzer/markdown_export.py` renders an `### AI-Writing Signs`
  section for each text with Wikipedia links.
- `app.py` injects the glossary into the Jinja context via
  `@app.context_processor`.
- `README.md` adds a row for Section 6 in the feature overview table
  and updates the doc index.

---

## [0.2.0] — 2026-05-15

### Added
- File-upload support. Per-panel `<input type="file">` accepting
  `.txt`, `.md`, `.markdown`, `.docx`, `.pdf`, `.json`, `.html`,
  `.htm`. An uploaded file overrides the textarea on the same panel.
- `analyzer/extract.py` — text extraction from each supported format.
  Pure stdlib for `.txt`, `.md`, `.json`, `.html`; `python-docx` and
  `pypdf` for `.docx` and `.pdf`.
- Graceful error surfacing for unsupported extensions, corrupt
  uploads, encrypted PDFs, and scanned (no-OCR) PDFs.

### Changed
- `requirements.txt` adds `python-docx>=1.1` and `pypdf>=4.0`.
- `Dockerfile` builds with the new dependencies; image size grows
  from ~127 MB to ~132 MB.
- `app.py` adds `_resolve_text(form_key, file_key, ...)` to prefer an
  uploaded file over the textarea on the same panel.

---

## [0.1.0] — 2026-05-15

### Initial release
- Fifteen comparison features across four sections:
  1. **Lexical** — type-token ratio, Latinate/Germanic lean, pet
     words and habitual phrases, hedges/fillers/intensifiers.
  2. **Syntactic** — sentence length distribution, sentence-opening
     patterns (six categories), coordination/subordination
     tendency, punctuation rates.
  3. **Discourse** — paragraph structure with topic-sentence
     position, transition strategy, evidence-to-claim sequencing,
     metadiscourse (textual and interpersonal).
  4. **Register** — overall register classification (formal,
     semi-formal, mixed, informal), register consistency across
     paragraphs, pronoun profile.
- Comparison ratings (Strong / Partial / No / Indeterminate) per
  feature, with explanations, plus a narrative summary.
- HTML report with collapsible details and downloadable Markdown
  export.
- Quote stripping before analysis; raw counts and per-500-word
  normalized rates throughout.
- Flask + spaCy stack with `en_core_web_sm`. Containerized via
  Docker with gunicorn (single worker, two threads, 120s timeout).
- Deployed to Fly.io with HTTP Basic Auth (single shared password),
  HTTPS forced, `/healthz` health check, always-on machine in `sjc`.
- GPL v3 license.

### Initial documentation
- `README.md` — overview, install, run, deploy.
- `docs/methodology.md` — feature-by-feature breakdown.
- `docs/architecture.md` — module map and data flow.
- `docs/operations.md` — Fly.io operations (formerly
  `deployment.md`; renamed to make room for `deploy.md` as the
  plain-language deploy walkthrough).
- `docs/limitations.md` — what the tool is not.
- `docs/spec.md` — the original specification.

---

[Unreleased]: https://github.com/justalewis/Stylometric-Comparison-Tool/compare/main...HEAD
[0.3.0]: https://github.com/justalewis/Stylometric-Comparison-Tool/commit/15b20ca
[0.2.0]: https://github.com/justalewis/Stylometric-Comparison-Tool/commit/ea0a96d
[0.1.0]: https://github.com/justalewis/Stylometric-Comparison-Tool/commit/a86283c
