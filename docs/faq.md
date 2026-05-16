# FAQ

Common questions about the tool, what it does, what it doesn't, and
how to think about its outputs.

---

## Use cases

### Can I use this to detect whether a student used AI?

No. The tool is not an AI detector. It describes the stylistic
patterns of two text samples and reports where they converge and
diverge. The AI-writing-signs section counts markers commonly found
in LLM output, but those markers also appear in human writing.

The intended use is to surface stylistic differences as the basis
for a conversation about voice. See [pedagogy.md](pedagogy.md) for
the framing the tool was built to support.

### Can I use the output in an academic-integrity proceeding?

Strongly discouraged. The tool produces no statistical confidence
estimates, no thresholds calibrated against ground truth, and no
mechanism for distinguishing AI-assisted writing from genre shifts,
register variation, or revision changes. Using descriptive
stylometric output to support a misconduct finding is the kind of
thing that produces miscarriages of judgment and disciplinary appeals
that overturn them.

If you're trying to have a difficult conversation with a student
about their writing, the tool can help structure that conversation.
It cannot substitute for the conversation, and it should not appear
as evidence in proceedings.

### Can I compare more than two texts at once?

Not in the current version. The comparison logic is built for
pairwise analysis. If you want to compare a student's work against
multiple known-author baselines, run several pairwise comparisons
and read the results together.

### Can I run this on text in other languages?

Only English at the moment. The spaCy model (`en_core_web_sm`) is
English-only, and the curated word lists (Latinate/Germanic, hedges,
AI vocabulary, etc.) are all English. Adding a second language would
require a parallel set of word lists, a language-specific spaCy
model, and language detection on input.

The tool is structured so a second language *could* be added without
restructuring the analyzer modules — see
[architecture.md](architecture.md). It's just not a small change.

### Can I save the report somewhere other than markdown?

Currently the only export format is Markdown. The HTML report is
self-contained and can be saved with the browser's "Save Page As"
feature, but that's not pretty. PDF export and structured JSON
output are possible additions; open an issue if you'd find them
useful.

---

## Methodology

### How accurate is it?

The tool is not measuring accuracy in the statistical sense. There
is no ground truth it's predicting. The metrics are *descriptive*:
they count well-defined linguistic features (sentence lengths, word
list hits, punctuation marks, sentence-opening categories) and
report the counts.

What can vary in accuracy is the feature *detection* — particularly
for the more inferential measurements:

- **Topic-sentence position** is a heuristic. Real prose distributes
  topic information in ways that don't always cluster around one
  sentence. The tool labels paragraphs as `distributed` when no
  sentence dominates, but the score-based detector can also miss
  topic sentences in unusual paragraph structures.
- **Comma splice detection** uses a regex heuristic. Treat the
  count as approximate.
- **Evidence-to-claim sequencing** depends on surface signals
  (citation patterns, interpretation markers). It will miss
  paraphrased sources without explicit attribution.
- **AI-signs metrics** are pattern-based and will produce false
  positives on writing that uses any of the patterns deliberately.
  Multiple metrics lighting up together is more meaningful than any
  single metric.

The TTR, vocabulary-stream, sentence-length, punctuation, and
pronoun-profile metrics are the most reliable: they count things
that are unambiguous to count.

### What counts as a "sentence"?

Whatever spaCy's sentence tokenizer says. The model handles
abbreviations and decimal numbers reasonably well; it occasionally
mis-splits on unusual punctuation or non-standard formatting. For
samples that look reasonable on the page, the count is reliable.

### Why are some word lists "illustrative, not exhaustive"?

The Latinate, Germanic, hedge, intensifier, transitional, and AI-
vocabulary lists are curated from the original specification and the
Wikipedia source page, then extended pragmatically. They aim to
catch high-frequency cases. Edge cases (uncommon synonyms, archaic
forms, technical jargon) will be missed.

The lists are in [`analyzer/wordlists.py`](../analyzer/wordlists.py)
and are easy to extend. See [CONTRIBUTING.md](../CONTRIBUTING.md).

### Why three time-stratified AI-vocabulary lists?

LLM vocabulary drifts. The Wikipedia source page documents
distinct vocabulary signatures for the 2023–mid-2024 era, the
mid-2024–mid-2025 era, and the mid-2025+ era. Earlier-era words
("delve", "tapestry") have partially leaked into general writing
through exposure, making them weaker signals; later-era words
remain more diagnostic. The tool tracks all three and shows
provenance per hit.

### What happens to quoted material?

It's stripped before analysis. The tool removes double-quoted spans
(both straight and curly) and block-quoted lines (those beginning
with `>` or indented four or more spaces). Quoted text would
contaminate the writer's profile — those words belong to the source
author. The report notes the number of removed spans and the word
count of the removed material, in case the analyst wants to consider
quotation density itself as a stylistic feature.

Single quotes are deliberately not stripped (they would collide with
contractions and possessives).

---

## Practical questions

### How long should the samples be?

400–1000 words is the sweet spot. Below 250 words the tool issues
a small-sample warning — the metrics get noisy at short lengths,
especially TTR (which is mechanically high for short texts) and the
per-500w rates (which magnify noise). Above ~1500 words you start
to get length-effects in the other direction: TTR mechanically
drops because common words start repeating.

For pairwise comparisons, samples of roughly equal length give the
most defensible results.

### What's the privacy story for uploaded text?

The tool runs in a single Fly.io container; the texts you submit
are processed in memory and discarded when the response is sent.
There's no database, no logs of submitted text, and no telemetry.
Gunicorn does log request paths and statuses (visible in `fly
logs`), but request bodies are not logged.

That said, **the tool's threat model assumes you're submitting your
own work or work you have permission to analyze.** Since the tool
is publicly accessible, the same caution applies as for any web
service: if you wouldn't paste the text into a search engine, don't
paste it into this tool.

### Does the tool require a password?

No. As of the current deployment, the tool is public — anyone with
the URL can use it. Earlier versions used HTTP Basic Auth with a
shared password; that gate was removed when the tool went fully
public. To re-enable auth, restore the `@app.before_request` handler
that was removed from `app.py` in commit history.

### Where are the texts stored after I submit them?

Nowhere. The submitted text lives in memory for the duration of the
request, gets analyzed, and the response is sent. No persistence.

### What if I want to add my own word lists?

`analyzer/wordlists.py` is the single source. Add new entries to the
relevant set or list. If you want a new *category* of word list
that's currently not measured (say, jargon from your field), you'd
need to add an analyzer function in the appropriate module and wire
it into the report. See [CONTRIBUTING.md](../CONTRIBUTING.md).

### How do I report a bug?

Open an issue at
<https://github.com/justalewis/Stylometric-Comparison-Tool/issues>
with:

- The two text samples (or minimal versions that reproduce the
  problem).
- What the tool reported.
- What you expected instead, and why.
- Browser and OS if the issue is in the UI.

---

## Licensing

### What license is the code under?

GPL v3. See [LICENSE](../LICENSE).

### Why GPL v3 and not MIT/Apache?

The license is intentionally copyleft. The tool exists for a
pedagogical purpose; if someone forks it into a commercial AI-
detection product (which would be a misuse of the tool's framing
and methodology), the license requires that derivative to remain
open source. The framing this tool was built around — descriptive
not diagnostic, conversation not adjudication — only survives if
the source stays accessible.

### Can I use this commercially?

GPL v3 allows commercial use, but any modifications you ship as
software must be made available under the same license. If you're
using the tool unchanged inside an institution, that's fine. If
you're building a product on top of it, the product source has to
be GPL-compatible too.

---

## Maintenance

### Will the word lists be updated as LLM output evolves?

The intent is yes, periodically. The Wikipedia "Signs of AI writing"
page is community-maintained and updates as patterns shift; the
plan is to revisit `wordlists.py` against that page every few
months. Pull requests against the lists are welcome — see
[CONTRIBUTING.md](../CONTRIBUTING.md).

### Where do I see what version is currently deployed?

`fly status --app stylometric-compare` shows the deployed image
tag. The repo's commit history is the canonical changelog.

### Who maintains this?

Justin Lewis. Email is in the GPL license file's header. Issues
filed on the GitHub repo are the preferred contact for anything
about the code or the methodology.
