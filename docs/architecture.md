# Architecture

A walkthrough of how the code is organized, how data flows from a
request to a rendered report, and the rationale behind each dependency.

---

## Module map

```
stylometric-compare/
├── app.py                       Flask routes, auth, request handling
├── analyzer/
│   ├── __init__.py              Re-exports pipeline.compare and pipeline.analyze
│   ├── pipeline.py              Orchestrator: builds the per-text profile
│   ├── preprocess.py            Quote stripping and paragraph splitting
│   ├── wordlists.py             All curated lexical marker sets
│   ├── lexical.py               Section 1 features
│   ├── syntactic.py             Section 2 features
│   ├── discourse.py             Section 3 features
│   ├── register.py              Section 4 features
│   ├── compare.py               Section 5: 15 feature comparators + narrative
│   ├── markdown_export.py       Markdown rendering of the comparison result
│   └── extract.py               File-upload text extraction
├── templates/
│   ├── index.html               Input form (paste or upload)
│   └── report.html              Per-text profiles + comparison table
└── static/
    └── style.css                Stylesheet
```

The analyzer package is intentionally framework-free: it imports only
spaCy and the Python standard library. The Flask app is the *only* part
of the codebase that knows about HTTP, sessions, files, and templates.
You can drop `analyzer/` into a notebook, a script, or another web
framework without touching it.

---

## Data flow

```
┌──────────────────────────────────────────────────────────────────────┐
│  HTTP request to /compare (multipart/form-data)                      │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  app.py                                                               │
│    @app.before_request → HTTP Basic Auth gate                         │
│    _resolve_text(form_key, file_key) for each text:                   │
│        if upload present → extract.extract_text(filename, bytes)      │
│        else              → request.form[form_key]                     │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  analyzer/pipeline.py — compare(text_a, text_b, topic)                │
│    load_nlp() (cached spaCy en_core_web_sm)                           │
│    profile_a = analyze(text_a, topic, "Text A")                       │
│    profile_b = analyze(text_b, topic, "Text B")                       │
│    comparison = compare.compare(profile_a, profile_b)                 │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (per text)
┌──────────────────────────────────────────────────────────────────────┐
│  analyzer/pipeline.py — analyze(text, topic, label)                   │
│                                                                       │
│    preprocess.strip_quotes(text)         → stripped + quote metadata  │
│    preprocess.split_paragraphs(stripped) → list[str]                  │
│    doc           = nlp(stripped)         → one spaCy Doc              │
│    paragraph_docs = [nlp(p) for p in …]  → per-paragraph Docs         │
│                                                                       │
│    lexical.analyze(doc, topic)           → §1                         │
│    syntactic.analyze(doc)                → §2                         │
│    discourse.analyze(doc, paragraphs,                                 │
│                      paragraph_docs)     → §3                         │
│    register.analyze(doc, paragraph_docs,                              │
│                     lex, syn)            → §4 (consumes §1, §2)       │
│                                                                       │
│    return {label, meta, lexical, syntactic, discourse, register}      │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  analyzer/compare.py — compare(profile_a, profile_b)                  │
│    For each of 15 _cmp_* functions:                                   │
│        row = cmp(profile_a, profile_b)                                │
│        rows.append(row)                                               │
│    narrative = _narrative(rows)                                       │
│    return {rows, counts, narrative}                                   │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Response branch in app.py                                            │
│    if format == "markdown":                                           │
│        render_markdown(result)  →  text/markdown attachment           │
│    else:                                                              │
│        render_template("report.html", result=result, …)               │
└──────────────────────────────────────────────────────────────────────┘
```

The dependency arrows are one-way. Lexical and syntactic don't know
about discourse or register; register depends on the *outputs* of
lexical and syntactic (because the overall register classification
synthesizes their numbers). Nothing depends on `compare`, which only
consumes profile dicts.

---

## Module responsibilities

### `analyzer/pipeline.py`

The only module that calls `spacy.load`. `load_nlp` is decorated with
`functools.lru_cache(maxsize=1)`, so the model loads once per process
and is reused for every subsequent request. spaCy's `ner` and
`lemmatizer` pipeline components are disabled — they're not used and
they slow analysis substantially.

`analyze(text, topic, label)` is the public entry point for a single
text. `compare(text_a, text_b, topic)` is the public entry point for a
pair.

### `analyzer/preprocess.py`

Two pure functions:

- `strip_quotes(text)` returns a `QuoteReport` dataclass containing the
  stripped text, the list of removed spans, and word counts. Used by the
  pipeline before any feature analysis runs.
- `split_paragraphs(text)` splits on blank lines and returns
  non-empty paragraph strings. Used to produce the per-paragraph spaCy
  docs that the discourse module needs.

### `analyzer/wordlists.py`

The single source of truth for every curated set in the project. Lists
are kept here so they can be edited in one place and reviewed without
spelunking through the feature modules. Each list comments its purpose
in the module docstring.

Conventions:

- Single-word lists use Python `set` literals.
- Multiword phrases use `list[str]` because they're matched as regex
  sequences in lowered text.
- All entries are lowercase.

### `analyzer/lexical.py`, `syntactic.py`, `discourse.py`, `register.py`

Each module exposes a top-level `analyze()` function that takes the
necessary inputs and returns a nested dict. The dict keys are stable
and used directly by `compare.py`, `markdown_export.py`, and the Jinja
templates — changes to dict shape ripple through those consumers.

Within each module, helper functions are prefixed `_` and not part of
the public surface.

### `analyzer/compare.py`

Fifteen `_cmp_*` functions, one per feature. Each accepts the full
profile dicts (so a comparator can read any field it needs) and returns
a row dict:

```python
{
    "feature": "1.1 Type-Token Ratio",
    "a":        "0.753 (149/198)",
    "b":        "0.545 (104/191)",
    "rating":   "No Match",
    "explanation": "Ratios differ by 0.208 (greater than 0.10).",
}
```

`_COMPARATORS` is the ordered list of these functions. `compare()` runs
each, tallies the ratings, and produces the narrative summary.

To add a new feature, write a new `_cmp_new_feature` function and
append it to `_COMPARATORS`. The Markdown exporter and HTML template
will pick it up automatically because they iterate over `rows`.

### `analyzer/markdown_export.py`

A pure rendering layer over the compare result. No state, no I/O. It
walks the profile dicts in the same order as the HTML template so the
two outputs stay aligned.

### `analyzer/extract.py`

Maps file extensions to plain-text extractors. Each extractor takes
`bytes` (the file content) and returns a `str` (paragraphs joined with
`\n\n`). The dispatcher raises:

- `UnsupportedFileError` for unknown extensions — surfaced to the
  user via a form-level error message.
- `ExtractionError` for known formats that fail to parse (corrupt
  `.docx`, encrypted PDFs, scanned PDFs with no text layer, malformed
  JSON, …) — also surfaced cleanly to the user.

### `app.py`

The Flask app, with the auth gate as a `@app.before_request` handler.
Three routes:

| Route | Methods | Behavior |
|---|---|---|
| `/healthz` | GET | Returns `200 OK` with body `ok`. Unauthenticated. Used by Fly's health checks. |
| `/` | GET | Renders the input form. Auth required. |
| `/compare` | POST | Runs analysis, returns HTML report or Markdown attachment based on form's `format` field. Auth required. |

`_resolve_text(form_key, file_key, label, errors)` is the helper that
prefers an uploaded file over the textarea on the same panel. Both
panels can use either method independently.

### Templates and CSS

`templates/index.html` is the form. `templates/report.html` renders the
comparison table and per-text profiles, with collapsible `<details>`
blocks for long lists (top Latinate words, top subordinators, sentence
buckets, etc.). The download button on the report is a tiny hidden
form that re-posts the same texts with `format=markdown`.

`static/style.css` defines a warm-neutral palette (off-white paper,
brown ink, serif body, monospace inputs) and the rating chip colors:

| Rating | Color |
|---|---|
| Strong Match | muted green |
| Partial Match | warm amber |
| No Match | muted brick red |
| Indeterminate | neutral gray |

---

## Dependencies

| Package | Why |
|---|---|
| **Flask** ≥ 3.0 | Web framework. The whole HTTP surface is ~120 lines. |
| **spaCy** ≥ 3.7 | Sentence segmentation, POS tags, dependency parse. Used heavily by `syntactic.py`, `discourse.py`, `register.py`. We disable `ner` and `lemmatizer` for speed. |
| **en_core_web_sm** | The small English model. ~12 MB; sufficient for the parse-level features we need. |
| **gunicorn** ≥ 21.2 | Production WSGI server in the Docker image. Single worker / 2 threads matches the always-on Fly machine. |
| **python-docx** ≥ 1.1 | `.docx` extraction. Iterates paragraphs and table cells. |
| **pypdf** ≥ 4.0 | `.pdf` extraction. Pure-Python, no native deps. |

Standard-library only for `.json`, `.html`, `.txt`, `.md` extraction.

---

## Performance notes

- spaCy model load is the slow step (~1–3 seconds). The `lru_cache` on
  `load_nlp` keeps it warm for the lifetime of the worker process. In
  the Fly deployment, the machine is always-on, so the model is loaded
  once at start and not on the request path.
- A typical 1000-word comparison runs in well under a second on
  shared-cpu-1x. The 60-second gunicorn timeout is comfortably loose
  for any text within the 2 MB request limit.
- Memory: the model resident set is ~150–200 MB. With one gunicorn
  worker the 512 MB Fly machine has ample headroom.

---

## Conventions

- **Type hints** are used throughout. `from __future__ import
  annotations` is at the top of every module so forward references
  work without quoting.
- **Pure functions** wherever possible. Modules under `analyzer/`
  contain only functions and dataclasses; no class state, no globals
  outside the curated lists.
- **No I/O in analysis code.** File reads, network calls, and template
  rendering live in `app.py` and `extract.py`. Everything in
  `analyzer/lexical.py` through `analyzer/compare.py` is in-memory.
- **Stable dict shapes.** The shape of the profile dicts is the
  contract between modules. Changes require updating the Jinja
  templates and the Markdown exporter together.

---

## Adding a new feature

1. Decide which section it belongs to (lexical / syntactic / discourse
   / register) and add the analyzer function in that module's
   `analyze()` aggregator.
2. If it uses curated word lists or phrase sets, put them in
   `wordlists.py`.
3. Add a `_cmp_new_feature` comparator in `compare.py` and append it
   to `_COMPARATORS`.
4. Add a section to the report template
   ([report.html](../templates/report.html)) to render the new metric.
5. Add a corresponding section to
   [markdown_export.py](../analyzer/markdown_export.py).
6. Document the feature in [methodology.md](methodology.md) using the
   "what / how / comparison rule" structure used for the existing
   fifteen.
