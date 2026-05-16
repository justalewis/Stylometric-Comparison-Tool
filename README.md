# Stylometric Comparison

A Flask + spaCy tool that takes two text samples and produces a structured
comparative stylometric profile across fifteen features spanning lexis,
syntax, discourse organization, and register. Designed for instructors,
editors, and researchers who want a transparent description of *what each
text does linguistically* rather than a black-box authorship verdict.

**Live (private):** <https://stylometric-compare.fly.dev/>

This tool is **not** a plagiarism detector and **not** an AI-generated-text
classifier. It describes lexical and structural patterns and reports the
degree of convergence or divergence between two profiles. The analyst draws
their own conclusions. See [docs/limitations.md](docs/limitations.md).

> **For instructors:** the tool was built specifically to support
> classroom conversations about voice, style, and stylistic
> consistency — including the conversation that opens when a student's
> draft suddenly sounds nothing like their in-class work. The framing
> and the suggested workflows are in **[docs/pedagogy.md](docs/pedagogy.md)**.
> Read that first if you plan to use the tool with students.

---

## What it does

For each text, the tool computes a profile across these dimensions:

| Section | Features |
|---|---|
| **1. Lexical** | Type-token ratio · Latinate vs. Germanic lean · Habitual words and phrases · Hedges / fillers / intensifiers |
| **2. Syntactic** | Sentence length distribution · Sentence-opening patterns (6 categories) · Coordination vs. subordination · Punctuation rates |
| **3. Discourse** | Paragraph structure and topic-sentence position · Transition strategy · Evidence-to-claim sequencing · Metadiscourse |
| **4. Register** | Overall register classification · Register consistency across paragraphs · Pronoun profile |
| **6. AI-writing signs** *(profile-only)* | 8 metrics drawn from Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing): AI vocabulary density · Promotional phrasing · Significance/legacy emphasis · Vague attribution · Negative parallelisms · Participial pseudo-analysis · Rule of three · Conclusion formulas |

It then runs fifteen pairwise comparators (sections 1-4) and rates each as
**Strong Match**, **Partial Match**, **No Match**, or **Indeterminate**,
with a brief explanation. Section 6 is descriptive only — counts per
500 words alongside example hits — to keep the framing honest about what
these markers do and don't tell you.

The output includes the per-text profiles, a comparison table, and a
narrative summary. In the browser, every key term carries a dotted
underline; hovering shows a plain-language definition pulled from the
glossary.

Full feature-by-feature methodology: [docs/methodology.md](docs/methodology.md).
AI-writing-signs catalog and Wikipedia crosswalk: [docs/ai-signs.md](docs/ai-signs.md).
Plain-language glossary of every term: [docs/glossary.md](docs/glossary.md).
Original specification: [docs/spec.md](docs/spec.md).

---

## Input

Either paste prose into the textareas or upload a file. Supported file
formats:

- `.txt`, `.md` / `.markdown` — plain text
- `.docx` — Microsoft Word
- `.pdf` — text-based PDFs (scanned/image PDFs are not OCR'd)
- `.json` — every string value is extracted and joined with paragraph breaks
- `.html` / `.htm` — tags stripped, `<script>` / `<style>` discarded

Each panel can independently use paste or upload. A file overrides anything
typed into the same panel's textarea.

**Recommended sample size**: 400–1000 words of the writer's own prose per
text. Below 250 words the tool emits a small-sample warning. Quoted
material is automatically stripped before analysis (double-quoted spans
and indented or `>`-prefixed block quotes) so the writer's own choices are
what get measured.

---

## Output

Two delivery formats:

1. **HTML report in the browser** — color-coded rating chips, the
   comparison table, per-text profiles with collapsible details, and a
   short narrative.
2. **Markdown download** — a self-contained `.md` file with the same
   content, suitable for archiving, annotating, or pasting into a
   conversation. Click *Run & download as Markdown* on the form, or the
   *Download as Markdown* button on the report page.

---

## Running locally

### Prerequisites

- Python 3.12 (3.10+ works; tested on 3.12)
- pip

### Setup

```powershell
git clone https://github.com/justalewis/stylometric-compare.git
cd stylometric-compare

# Optional but recommended: virtualenv
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Run the dev server

```powershell
$env:STYLOMETRIC_PASSWORD = "pick-anything-for-local-dev"
python app.py
```

Visit <http://127.0.0.1:5050> and authenticate with username `user` and
the password you just set. To change the username, also set
`STYLOMETRIC_USERNAME`.

Without `STYLOMETRIC_PASSWORD` set, the app fails closed with a 503 — the
auth gate is a safety property, not opt-in.

### Run analyses programmatically

```python
from analyzer import compare

result = compare(
    text_a="<first sample>",
    text_b="<second sample>",
    topic="optional topic hint",
)

# result["profile_a"], result["profile_b"]  → per-text profiles
# result["comparison"]["rows"]              → 15 feature comparators
# result["comparison"]["narrative"]         → short prose summary
```

To emit Markdown:

```python
from analyzer.markdown_export import render_markdown
md_string = render_markdown(result)
```

---

## Deployment

The project ships with a `Dockerfile` and `fly.toml` for Fly.io. Full
guide: [docs/deployment.md](docs/deployment.md).

Short version:

```powershell
fly apps create stylometric-compare
fly secrets set STYLOMETRIC_PASSWORD="<strong-password>" --app stylometric-compare
fly deploy --app stylometric-compare --ha=false
```

The Docker image is ~130 MB. The default `fly.toml` provisions a single
shared-cpu-1x machine with 512 MB RAM in `sjc` (San Jose), always-on, with
HTTPS enforced and a `/healthz` health check every 30 seconds.

---

## Project layout

```
stylometric-compare/
├── app.py                       Flask entry point (auth + routes)
├── requirements.txt
├── Dockerfile                   Production container (gunicorn + spaCy model)
├── fly.toml                     Fly.io deployment config
├── .dockerignore
├── analyzer/
│   ├── __init__.py
│   ├── pipeline.py              Orchestrator: load model, build profile, run compare
│   ├── preprocess.py            Quote stripping, paragraph splitting
│   ├── wordlists.py             Curated lexical markers
│   ├── lexical.py               Section 1 (TTR, Latinate/Germanic, pet words, hedges)
│   ├── syntactic.py             Section 2 (length, openers, coord/subord, punctuation)
│   ├── discourse.py             Section 3 (paragraphs, transitions, evidence, metadiscourse)
│   ├── register.py              Section 4 (classification, consistency, pronouns)
│   ├── compare.py               Section 5 (15 feature comparators + narrative)
│   ├── aitext_signs.py          Section 6 (8 AI-writing-signs metrics)
│   ├── glossary.py              Plain-language term definitions
│   ├── markdown_export.py       Markdown rendering
│   └── extract.py               File-upload text extraction
├── templates/
│   ├── index.html               Input form
│   └── report.html              Comparison report
├── static/
│   └── style.css                Warm-neutral serif aesthetic
└── docs/
    ├── methodology.md           Feature-by-feature breakdown of what the tool measures
    ├── architecture.md          Module map, data flow, dependency rationale
    ├── deployment.md            Fly.io operations
    ├── limitations.md           Caveats, scope, what this tool is NOT
    └── spec.md                  Original specification (verbatim)
```

Deeper code walkthrough in [docs/architecture.md](docs/architecture.md).

---

## Documentation index

**For users**

- **[Pedagogy](docs/pedagogy.md)** — the instructor's guide.
  Classroom workflows (self-comparison across drafts, cross-genre
  comparison, AI-augmentation conversations), framings for talking
  to students about voice, sample reflection prompts. The framing
  the tool was built to support.
- **[Worked examples](docs/examples.md)** — two end-to-end
  comparisons with real numbers. Formal-vs-informal human prose,
  and an AI-flavored sample that exercises every AI-writing-signs
  metric.
- **[FAQ](docs/faq.md)** — use cases, methodology accuracy,
  privacy, licensing, common questions about the output.
- **[Glossary](docs/glossary.md)** — plain-language definitions
  of every term used in the report. Same content appears as hover
  tooltips on dotted-underlined terms in the browser.

**For maintainers**

- **[Methodology](docs/methodology.md)** — every feature explained: what
  the spec asked for, what the code does, how the comparison rating is
  computed, and what each rating means. Includes Wikipedia "Signs of AI
  writing" crosswalk for the original 15 features.
- **[AI-writing signs](docs/ai-signs.md)** — the 8 profile-only
  metrics drawn from Wikipedia's catalog: detection rules, per-metric
  word lists, limitations, calibration guidance, and Wikipedia source
  links for each sign.
- **[Architecture](docs/architecture.md)** — module map, data flow,
  dependency rationale, and conventions.
- **[Deployment](docs/deployment.md)** — Fly.io operations: provisioning,
  secrets, scaling, region selection, troubleshooting.
- **[Limitations](docs/limitations.md)** — what the tool is *not*, where
  results are most reliable, and known caveats per feature.
- **[Contributing](CONTRIBUTING.md)** — development setup, the
  recipe for adding a new feature, style conventions, what kinds of
  PRs are likely to merge.
- **[Changelog](CHANGELOG.md)** — version history.
- **[Specification](docs/spec.md)** — the original feature spec, kept
  verbatim as the source of truth for what the tool implements.

---

## License

[GPL v3](LICENSE). Intentionally copyleft — see
[docs/faq.md](docs/faq.md) for the reasoning.
