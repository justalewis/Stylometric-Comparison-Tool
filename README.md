# Stylometric Comparison

A Flask + spaCy tool for stylometric analysis of writing. Three modes:

- **Comparison mode (`/`)** — paste two samples; the tool produces a
  comparative profile across fifteen features and rates each as Strong /
  Partial / No / Indeterminate Match.
- **Single-text mode (`/analyze`)** — paste one sample; the tool produces
  the same stylometric profile without the comparison summary.
- **Deep Scan (`/deep-scan`)** — *localhost-only.* Runs all 26 AI-writing-
  signs metrics (the standard 8 plus 18 more from Wikipedia's full
  catalog) against a single text, with a profile view, a details view,
  and `.md` / `.docx` / `.pdf` export.

The first two modes cover lexis, syntax, discourse organization, register,
and the eight AI-writing-signs metrics. Designed for instructors, editors,
and researchers who want a transparent description of *what the text does
linguistically* rather than a black-box authorship verdict.

**Live:** <https://stylometric-compare.fly.dev/>

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

For a full plain-language walkthrough — including how to install
Python, set up a virtual environment, and troubleshoot common
problems — see **[docs/install.md](docs/install.md)**.

The compressed version, for those already familiar with Python
projects:

```powershell
git clone https://github.com/justalewis/Stylometric-Comparison-Tool.git
cd Stylometric-Comparison-Tool

python -m venv .venv
.venv\Scripts\Activate.ps1            # macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm

python app.py                          # → http://127.0.0.1:5050
```

The tool runs publicly with no authentication.

### Run analyses programmatically

For a single text:

```python
from analyzer import analyze

profile = analyze("<text>", topic="optional topic hint")

# profile["lexical"], profile["syntactic"], profile["discourse"],
# profile["register"], profile["ai_signs"]                          → feature blocks
# profile["meta"]                                                   → word count, paragraph count, quoted-material stats
```

For a comparison of two texts:

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
from analyzer.markdown_export import render_markdown, render_markdown_single
md_compare = render_markdown(result)        # comparison report
md_single  = render_markdown_single(profile, topic="...")  # single-text report
```

---

## Deploying your own copy

The project ships with a `Dockerfile` and `fly.toml` for Fly.io.
For a plain-language step-by-step — installing flyctl, signing up
for Fly, picking a unique app name, deploying, custom domains,
cost expectations — see **[docs/deploy.md](docs/deploy.md)**.

For ongoing operations on an already-deployed instance (logs,
scaling, region migration, troubleshooting), see
[docs/operations.md](docs/operations.md).

The compressed version:

```powershell
# Edit fly.toml: change app = "stylometric-compare" to your-chosen-name
fly apps create your-chosen-name
fly deploy --ha=false
# → https://your-chosen-name.fly.dev/
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
│   ├── index.html               Comparison-mode input form
│   ├── analyze.html             Single-text input form
│   ├── report.html              Comparison report (two profiles + summary)
│   ├── report_single.html       Single-text report (one profile, no summary)
│   └── glossary.html            In-app reference page
├── static/
│   └── style.css                Warm-neutral serif aesthetic
└── docs/
    ├── methodology.md           Feature-by-feature breakdown of what the tool measures
    ├── architecture.md          Module map, data flow, dependency rationale
    ├── install.md               Plain-language local install walkthrough
    ├── deploy.md                Plain-language Fly.io deploy walkthrough
    ├── operations.md            Fly.io operations / maintenance reference
    ├── limitations.md           Caveats, scope, what this tool is NOT
    └── spec.md                  Original specification (verbatim)
```

Deeper code walkthrough in [docs/architecture.md](docs/architecture.md).

---

## Documentation index

**Getting started**

- **[Install locally](docs/install.md)** — plain-language
  walkthrough for getting the tool running on your own machine.
  Covers prerequisites, virtual environments, dependencies, and
  common problems.
- **[Deploy your own copy](docs/deploy.md)** — plain-language
  walkthrough for putting your own copy on the internet using
  Fly.io. Covers signup, naming, deploying, custom domains, and
  cost expectations.

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
- **[Operations](docs/operations.md)** — Fly.io operations for an
  already-deployed instance: logs, scaling, region migration,
  troubleshooting, machine commands.
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
