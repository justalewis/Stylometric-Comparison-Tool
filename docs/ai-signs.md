# AI-Writing Signs

Section 6 of the analyzer measures eight stylistic patterns drawn
directly from Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
catalog. Each metric is **profile-only**: it appears in the per-text
profile section of the report, but is not part of the 15-feature
comparative summary. The framing matters:

- These are **descriptive markers**. High rates suggest the writer
  reaches for these patterns; they are not proof of AI authorship.
- Humans use every one of these patterns. The Wikipedia page itself
  says "no single sign is determinative" — clusters of signs at high
  rates are the actionable signal, not any individual hit.
- The tool reports *what is there*; the analyst draws the inference.

This document covers the methodology for the eight metrics and links
each one to its Wikipedia source section. For a higher-level
overview of the original spec, see
[methodology.md](methodology.md). For shorter plain-language
definitions, see [glossary.md](glossary.md).

---

## How the metrics work

Every metric produces three pieces of data:

1. **Raw count** — how many hits in the stripped text.
2. **Per-500-word rate** — normalized so samples of different lengths
   can be compared.
3. **Top hits / examples** — specific words, phrases, triplets, or
   sentences that triggered the count.

Some metrics also surface metadata. AI vocabulary provenance, for
example, records which of the three time-stratified lists each hit
appeared on.

The headline number for the section is the **total markers** —
the sum of the eight raw counts, also reported per 500 words. There
is no threshold above which a text "counts as" AI-written. The
intended use is comparative: contrast Text A's total against Text
B's, or against a baseline you've calibrated on known-human work.

---

## The eight metrics

### 1. AI vocabulary density

- **Wikipedia source:** [High density of "AI vocabulary" words](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#High_density_of_%22AI_vocabulary%22_words)
- **What it captures:** words documented as statistically over-
  represented in LLM output.
- **How it's computed:** every alphabetic token is checked against
  three time-stratified word lists from the Wikipedia page:

  | List | Era | Sample words |
  |---|---|---|
  | `AI_VOCAB_2023_MID2024` | 2023 – mid 2024 | additionally, boasts, bolstered, crucial, delve, emphasizing, enduring, garner, intricate, interplay, key, landscape, meticulous, pivotal, underscore, tapestry, testament, valuable, vibrant |
  | `AI_VOCAB_MID2024_MID2025` | mid 2024 – mid 2025 | align with, bolstered, crucial, emphasizing, enhance, enduring, fostering, highlighting, pivotal, showcasing, underscore, vibrant |
  | `AI_VOCAB_MID2025_PLUS` | mid 2025+ | emphasizing, enhance, highlighting, showcasing |

  Plus a small set of multiword phrases (`align with`, `aligns
  with`, ...) matched on the lowered text. Lists overlap; each
  distinct hit is counted once and tagged with the list(s) it appears
  on (so the report can show "this hit is on the mid-2025+ list" —
  more recent lists are more diagnostic because the older words have
  partially leaked into general writing through repeated exposure).
- **Reported:** raw count, per-500w rate, top 10 hits with frequency
  and provenance, top phrase hits.

### 2. Promotional / advertisement-like phrasing

- **Wikipedia source:** [Promotional and advertisement-like language](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Promotional_and_advertisement-like_language)
- **What it captures:** travel-guide / press-release tone.
- **How it's computed:** phrase matches against
  `AI_PROMOTIONAL_PHRASES` (`boasts a`, `nestled in`, `in the heart
  of`, `diverse array`, `natural beauty`, `commitment to
  excellence`, `groundbreaking`, `state-of-the-art`, `world-class`,
  `renowned for`, ...) plus single-word matches against
  `AI_PROMOTIONAL_SINGLES` (`vibrant`, `renowned`, `profound`,
  `exemplifies`, `showcases`).
- **Reported:** raw count, per-500w rate, top hits, one or two
  example sentences containing the highest-frequency hit.

### 3. Significance / legacy emphasis

- **Wikipedia source:** [Undue emphasis on significance, legacy, and broader trends](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Undue_emphasis_on_significance,_legacy,_and_broader_trends)
- **What it captures:** generic statements that connect the subject
  to broader importance without earning it.
- **How it's computed:** phrase matches against
  `AI_SIGNIFICANCE_PHRASES`, which includes:
  - `stands as`, `serves as`, `stands as a testament`, `is a
    testament`, `testament to`
  - `pivotal/crucial/key/vital/significant/central/important role`
  - `underscores its importance`, `highlights its significance`,
    `reflects broader`, `focal point`, `indelible mark`
  - `evolving landscape`, `shifting landscape`, `setting the stage
    for`, `marking a shift`, `shaping the future`, `enduring
    legacy`, `lasting impact`
- **Reported:** raw count, per-500w rate, top hits, example
  sentences.

### 4. Vague attribution

- **Wikipedia source:** [Vague attributions and overgeneralization of opinions](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Vague_attributions_and_overgeneralization_of_opinions)
- **What it captures:** references to unnamed authorities.
- **How it's computed:** phrase matches against
  `AI_VAGUE_ATTRIBUTION_PHRASES`: `industry reports`, `industry
  experts`, `observers have cited`, `experts argue`, `experts say`,
  `experts believe`, `critics argue`, `several sources`, `several
  publications`, `many sources`, `various sources`, `leading
  experts`, `studies have shown`, `research suggests`, etc.
- **Reported:** raw count, per-500w rate, top hits, example
  sentences.

### 5. Negative parallelisms

- **Wikipedia source:** [Not just X, but also Y](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Not_just_X,_but_also_Y)
  and [Not X, but Y](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Not_X,_but_Y)
- **What it captures:** contrastive constructions that deny one
  characterization before asserting another.
- **How it's computed:** four regex patterns over the raw text:
  - `not just X[, ] (but|it's|it is) Y`
  - `not only X[,]? but (also)? Y`
  - `it's/it is not X, it's/it is Y`
  - `not [up to 5 words], but Y`
- Matches are deduplicated. The report shows the matched phrase and
  the full surrounding sentence.
- **Reported:** raw count, per-500w rate, up to three example
  sentences.

### 6. Participial pseudo-analysis

- **Wikipedia source:** [Superficial analyses](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Superficial_analyses)
- **What it captures:** sentences ending in a comma + present-
  participle clause that makes an unattributed analytical claim
  ("..., highlighting the importance of X.").
- **How it's computed:** for each sentence:
  1. Find the last comma in the sentence.
  2. Check that the next non-space token is either (a) tagged `VBG`
     by spaCy, or (b) appears in `AI_PARTICIPIAL_STARTERS`
     (`highlighting`, `underscoring`, `emphasizing`, `ensuring`,
     `reflecting`, `symbolizing`, `contributing`, `cultivating`,
     `fostering`, `encompassing`, `showcasing`, `demonstrating`,
     `illustrating`, `providing`, `offering`, `enabling`,
     `facilitating`, `promoting`, `shaping`, `marking`, `creating`,
     `establishing`, `delivering`, `yielding`).
  3. If so, the sentence is flagged and the participial starter is
     recorded.
- **Reported:** raw count, per-500w rate, top starters with
  frequency, example sentences.
- **Limitation.** Some legitimately well-written sentences also end
  in participial clauses ("She walked into the room, smiling"). The
  marker is most diagnostic when the participial clause makes an
  analytical or evaluative claim ("..., highlighting the broader
  significance of this trend.") rather than a concrete observation.

### 7. Rule of three (triplet structures)

- **Wikipedia source:** [Rule of three](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Rule_of_three)
- **What it captures:** three parallel items in a list or series.
- **How it's computed:** scan token windows for the pattern
  `content_word, comma, content_word, comma, ('and'|'or'),
  content_word`. The three slots are constrained to share the same
  spaCy POS tag (all `ADJ`, all `NOUN`, or all `PROPN`) to bias
  toward truly parallel structure rather than incidental commas.
- **Reported:** raw count, per-500w rate, up to four example
  triplets with the surrounding sentence.
- **Limitation.** The detector misses triplets that span coordinate
  noun phrases (e.g., "fast cars, loud music, and bright lights"
  parses as triplet, but "the fast cars, the loud music, and the
  bright lights" may not because the determiners break the
  POS-parallel constraint). Treat the count as a lower bound.

### 8. Conclusion / outlook formulas

- **Wikipedia source:** [Outline-like conclusions about challenges and future prospects](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Outline-like_conclusions_about_challenges_and_future_prospects)
- **What it captures:** stock closing patterns that LLMs reach for.
- **How it's computed:** phrase matches against
  `AI_CONCLUSION_PHRASES`: `despite its`, `despite these
  challenges`, `challenges and legacy`, `future outlook`, `looking
  ahead`, `moving forward`, `as we look to the future`, `in
  conclusion`, `to conclude`, `in summary`, `to summarize`, `in the
  years to come`, `the future holds`, `going forward`, `navigating
  these challenges`, `faces several challenges`, `remain to be
  seen`.
- **Reported:** raw count, per-500w rate, top hits, example
  sentences.

---

## What this section does *not* measure

The eight metrics above are the subset of Wikipedia's catalog that
can be operationalized cleanly with regex and POS tagging. Several
signs from the page are intentionally **not** implemented because
they don't fit a stylometric framework, or because they require
context the tool doesn't have:

- **Title case in headings, overuse of boldface, inline-header
  vertical lists, Markdown in wikitext, broken wikitext, table
  formatting, heading-level skipping, thematic breaks before
  headings, reference markup bugs, emoji as formatting.** These are
  formatting and markup signs; they are stripped out by our
  extractors (HTML, Markdown) before the prose ever reaches the
  analyzer. Detecting them would require preserving the source
  markup, which would muddy every other metric.
- **Avoidance of basic copulatives ("is/are" decrease).** The
  Wikipedia page documents a measurable 10%+ drop in `is/are` usage
  in AI-generated 2023 text. We track `is/are` rates implicitly
  (they fall under standard tokenization), but operationalizing this
  as a *sign* requires a baseline period to compare against — which
  is genre-dependent. The `AI_COPULA_SUBSTITUTES` set is defined in
  `wordlists.py` for future use.
- **Canned emphasis on notability/attribution/media coverage,
  outline-like sectioning beyond conclusions, leads treating list
  titles as proper nouns, knowledge-cutoff disclaimers, prompt
  refusals.** These are document- or genre-specific signs (Wikipedia
  articles, AI assistant transcripts) that don't generalize to the
  short prose samples this tool analyzes.
- **Lexical diversity / elegant variation.** Already measured by
  Section 1.1 (TTR) — high TTR is actually slightly *suggestive* of
  AI variation, but the relationship is weak and length-sensitive,
  so we don't double-count.
- **Citation defects (invalid DOIs/ISBNs, broken external links,
  utm_source parameters, named-but-unused references).** These
  require following links and validating identifiers, which is well
  outside the tool's scope.
- **Pronounced shift in writing style mid-document.** Section 4.2
  (Register Consistency) already measures register shifts between
  paragraphs. AI insertions tend to shift register; the existing
  consistency metric catches the strongest cases.

To add coverage for any of the above, see the **Adding a new
feature** recipe in [architecture.md](architecture.md). The pattern
is: curated list → analyzer function → entry in
`analyzer/aitext_signs.py:analyze()` → block in `report.html` →
block in `markdown_export.py`.

---

## Calibration

Two ways to read the numbers:

1. **Comparison between two texts.** Submit both samples; look at
   how the totals and individual metric rates differ. If Text A has
   30 markers and Text B has 4, the gap is meaningful regardless of
   whether 30 is "high" in absolute terms.
2. **Calibration against your own baseline.** Run a few samples of
   known-human writing (your own work, a colleague's, a student
   essay you've already graded). Note the per-500w totals. That
   becomes your reference for what "normal" looks like in the
   genre you read.

The Wikipedia page itself emphasizes that any individual sign can
appear in human writing — the diagnostic value is in **clusters at
high rates**, especially when multiple time-stratified vocabulary
lists light up together.

---

## Source

Wikipedia: "Signs of AI writing." Accessed 2026-05-16.
<https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing>

The page is community-maintained and evolves. The lists in
`analyzer/wordlists.py` should be revisited periodically to stay
aligned with the current catalog.
