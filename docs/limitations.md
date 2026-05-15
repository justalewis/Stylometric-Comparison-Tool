# Limitations

This tool describes patterns. It does not determine truth. Read this
page before drawing any conclusion from a comparison.

---

## What the tool is not

### Not an AI-generated-text detector

The tool does not classify text as human-written or AI-generated. It
cannot, and it should not be used as if it could. AI-generated text in
2025 spans virtually the full range of registers and styles, and the
features measured here — vocabulary tilt, sentence rhythm, transition
strategy — overlap heavily with human prose at every formality level.

A comparison can surface convergence or divergence between two samples,
but interpreting that as AI involvement requires evidence the tool does
not provide: known baselines for the writer, contextual signals,
metadata, conversation with the student or author, and so on.

### Not a plagiarism detector

The tool does not compare against any corpus of existing texts. It only
compares the two samples submitted. Plagiarism detection requires a
reference database (e.g., Turnitin's index), which this tool deliberately
does not maintain.

### Not an authorship attribution system

Genuine forensic authorship attribution requires:

- Multiple known-author samples to establish a baseline profile.
- Statistical modeling (e.g., Burrows's Delta, cosine similarity over
  function-word frequency vectors, support-vector classification).
- Validation against ground-truth cases.
- Domain expertise to interpret results.

This tool computes a description of two samples and reports overlap. A
forensic conclusion is the analyst's job, and it requires more evidence
and method than this tool provides.

### Not an academic-integrity arbiter

The tool intentionally produces *descriptions*, not *verdicts*. Even a
"15 No Match" result is not evidence of dishonesty — two texts by the
same author writing in different genres or moods can diverge across
nearly every feature.

---

## Where results are most reliable

The tool's measurements are most defensible when:

- **Both samples are 400–1000 words.** Below 250 words the small-sample
  warning fires; below 400 words the type-token ratio is increasingly
  noisy. Above 1500 words the TTR drops mechanically (vocabulary
  repetition becomes inevitable) and per-paragraph features become more
  meaningful than aggregate counts.

- **Both samples are in the same genre.** Comparing an academic essay to
  a personal narrative will yield divergence on most features even from
  the same author, because the *genre* drives many of the choices the
  tool measures. Comparison is most informative when genre, register
  intent, and audience are roughly held constant.

- **Both samples are by single authors writing without intermediary
  rewriting.** Collaboratively written or heavily edited text averages
  out features that single-author prose preserves.

- **The topic hint is supplied.** Without it, "pet words" mixes topical
  necessity with genuine habit. A hint enables a topical/habitual split
  that's far more useful for comparison.

- **Quoted material has been left intact in the input.** The tool will
  strip it; users should not pre-edit it out, since the original quote
  boundaries provide useful signal about quotation length and density.

---

## Known feature-level caveats

### Type-token ratio is length-sensitive

TTR drops as text grows. The comparator flags **Indeterminate** when
texts differ in length by more than 2×, but more subtle length effects
remain. Two texts of 500 and 1200 words by the same writer will likely
show different TTRs purely from this effect. If exact comparability
matters, truncate the longer sample to the shorter sample's length and
re-run.

### Latinate / Germanic lists are curated, not exhaustive

`analyzer/wordlists.py` includes a few hundred high-frequency forms in
each category. The lists were extended from the spec's illustrative
examples but cannot cover the full English lexicon. Texts heavy in
domain-specific vocabulary (medicine, law, engineering) may have a
large fraction of uncategorized terms, lowering both counts. The
*ratio* remains a fair measure of relative lean as long as enough terms
are categorized.

A text with **zero** categorized terms (very rare, usually a sign of
heavy jargon or a non-English-resembling sample) is reported as
Indeterminate on this feature.

### Pet-word detection cannot distinguish habit from topic without help

Without a topic hint, every flagged word is reported as candidate-
habitual. The analyst has to do the topical/habitual split by eye. The
tool partially automates this when a hint is provided, but only via
literal substring match on the hint — it cannot expand to synonyms or
related concepts.

### Sentence-opener classification depends on spaCy's parse

spaCy's small English model is fast but imperfect. Occasional
misclassifications (e.g., a noun phrase tagged as a verb form, a
demonstrative miscounted as a pronoun) will skew opener counts. The
effect is usually small on multi-paragraph texts but can dominate on
very short samples.

### Coordination/subordination ratio uses heuristics, not full parsing

The coordinating-clause count fires only when spaCy's dependency parse
identifies a verb-to-verb conjunction. The subordinating count uses
both spaCy's `SCONJ` tag and a curated subordinator list, which can
overlap. The comma-splice detector is intentionally rough — it produces
useful flags on clearly informal prose but should not be cited as a
precise count.

### Topic-sentence position is a heuristic, period

The score-based approach (interpretation markers, claim verbs, topic-
term density) is a coarse proxy for paragraph organization. Texts that
distribute their argument across multiple sentences, or use implicit
topic sentences, will be classified as `distributed` — which is often
correct but not always informative. The report labels the position as
a heuristic estimate and recommends human review.

### Evidence-to-claim sequencing relies on surface signals

The tool detects citation patterns (APA-style parentheticals, numeric
brackets) and interpretation markers (`this shows`, `the implication`).
It will miss:

- Paraphrased sources without parenthetical attribution.
- Footnote-style citations (`¹`, `[note 3]`).
- Embedded evidence that doesn't surface as quoted material or a stock
  marker.
- MLA in-text citation style if the parenthetical doesn't include a
  year.

The "primary evidence type" is similarly only as good as the regex.

### Metadiscourse counts use a finite phrase list

The textual and interpersonal metadiscourse lists in `wordlists.py` cover
common forms but miss novel constructions and rarer academic conventions.
A writer who uses an unusual metadiscursive phrase (`The aim of this
section is…`) will show a lower count than the prose actually warrants.
Expand the lists in `wordlists.py` if your domain demands it.

### Register classification is a synthesis, not a measurement

The `formal / semi-formal / mixed / informal` label comes from summing
indicator counts and thresholding. Borderline texts may sit between
labels and the result can flip on a single contraction or hedge. The
evidence markers shown alongside the label are what to focus on; the
single-word label is a convenience.

### Pronoun categorization treats "it" as third person

The third-person count includes all instances of "it" except those
spaCy tags as expletives (`it is important that…`). Pronoun-heavy
informal writing thus often shows third-person dominant even when the
writer is heavily using "I" — because "it" outpaces "I". The pronoun
profile reports raw counts for every category; consult those rather
than relying on the dominant label.

---

## Caveats about file extraction

| Format | Caveat |
|---|---|
| `.pdf` | No OCR. Scanned-image PDFs return an extraction error. Encrypted PDFs return an error unless the password is empty. Multi-column layouts may interleave columns; tables may collapse. |
| `.docx` | Paragraph order is preserved; comments, footnotes, and tracked changes are not extracted. Table cell text is included but loses tabular structure. |
| `.json` | All string values are extracted recursively, in traversal order. The order is deterministic for objects but may not match the analyst's intended reading order. Keys are not extracted, only values. |
| `.html` | `<script>` and `<style>` are dropped. Block tags become paragraph breaks. Inline whitespace is collapsed. CSS-styled visual structure (columns, sidebars) is flattened. |
| `.md` | Markdown syntax is left intact. spaCy's tokenizer treats most markdown punctuation as punctuation, so the analysis is largely unaffected, but heading lines (`# Heading`) appear as their own paragraphs. |
| `.txt` | UTF-8 decoded with a Latin-1 fallback. Mojibake from misencoded files may survive into the analysis. |

---

## Sample-size warnings

The tool emits a small-sample warning when a text falls below 250 words
*after* quote stripping. Below this threshold:

- Per-500-word normalizations magnify noise.
- TTR is artificially high.
- Sentence-length distributions are heavily influenced by single
  outliers.
- Paragraph-level features (consistency, topic position) may have only
  one or two paragraphs to work with.

Take any feature on a sub-250-word sample with a grain of salt.

---

## Statistical disclaimer

This tool produces no p-values, no confidence intervals, no significance
tests. The feature ratings (Strong / Partial / No / Indeterminate) are
based on **descriptive thresholds** from the spec, not statistical
inference. They are useful for guiding the analyst's attention; they
are not measurements of how *likely* the texts share an author. For
that you want forensic stylometry with cross-validated classifiers and
a baseline corpus.
