# Methodology

This document explains, feature by feature, what the tool measures, how it
computes each metric, what the comparison rules are, and where the analyst
should apply judgment. The sixteen features extend the original [specification](spec.md) with
one added feature (§1.5 Reading level); this document records the
implementation decisions made along the way.

The tool produces two outputs per run:

1. **Individual profiles** — Text A's profile and Text B's profile, each
   organized into the four sections below.
2. **Comparative ratings** — for each of the sixteen features, one of:
   - **Strong Match** — both texts behave the same way on this feature.
   - **Partial Match** — the texts agree on the dominant pattern but
     diverge on secondary measurements.
   - **No Match** — the texts behave differently on this feature.
   - **Indeterminate** — there isn't enough signal to decide (sample too
     short, no relevant tokens, etc.).

A summary line counts the four rating types and offers a short narrative.
The tool does **not** assert authorship, AI-generation, or
academic-integrity conclusions; it describes patterns and lets the analyst
draw inferences.

---

## Preprocessing

Before any of the features are computed, each text passes through
`analyzer/preprocess.py`:

1. **Quoted material is stripped.** Double-quoted spans (straight `"..."`
   and curly `"..."`) and block quotes (lines beginning with `>` or
   indented four or more spaces) are removed. The text inside them is the
   *source author's* choices, not the writer's, so it would contaminate
   the lexical and syntactic counts. The number of quoted spans and the
   word count of quoted material are retained as metadata and shown in the
   report.
2. **Paragraphs are split** on blank lines (two or more consecutive
   newlines). Empty paragraphs are dropped. The discourse module receives
   this paragraph list directly.
3. **A spaCy `Doc` is built** from the stripped text using
   `en_core_web_sm`. The `ner` and `lemmatizer` components are disabled
   for speed; they are not needed for any feature.
4. **Per-paragraph `Doc`s are also built** so that paragraph-level features
   (topic-sentence position, register consistency) have access to spaCy's
   parse and POS tags within each paragraph.

Single quotes are deliberately **not** stripped — they collide with
contractions (`don't`, `it's`) and possessives (`student's`), and the
false-positive cost outweighs the value.

---

## Section 1 — Lexical preferences

### 1.1 Lexical diversity (TTR, MATTR, MTLD)

**What it measures.** How varied the writer's vocabulary is across the
sample. The tool reports three related metrics: raw TTR, MATTR
(length-robust by sliding window), and MTLD (length-robust by factor
counting). Each addresses a different limitation of the others.

**How they're computed.**

- **TTR (Type-Token Ratio).** Every alphabetic token in the spaCy doc
  is lowercased. The number of *types* (unique forms) is divided by
  the number of *tokens* (total forms). Punctuation, spaces, and digits
  are excluded. The standard textbook definition.
- **MATTR (Moving-Average Type-Token Ratio).** A 100-token window
  slides one position at a time across the token list. TTR is computed
  within each window; the windows' TTRs are averaged. Because every
  window is the same size, MATTR is *length-independent*: a 400-word
  sample and a 4,000-word sample can be compared directly. Implemented
  with an incremental Counter so the cost is `O(n)` rather than
  `O(n × window)`.
- **MTLD (Measure of Textual Lexical Diversity).** Following McCarthy
  & Jarvis (2010). The algorithm walks tokens accumulating a running
  TTR; each time the running TTR drops to or below 0.72, a "factor" is
  counted and the running state resets. Leftover tokens at the tail
  are scaled by `(1 − last_TTR) / (1 − 0.72)`. The full MTLD is the
  total token count divided by the factor count, computed in both
  directions (forward and backward) and averaged.

**Validity bounds.**

| Metric | Minimum tokens | Notes |
|---|---|---|
| TTR | 1 | Reported even on very short samples, but mechanically inflated below ~200 words. |
| MATTR | 200 | Needs at least 2× the window for a meaningful average. |
| MTLD | 100 | Below this, factor counts are too noisy. |

When the sample is too short for MATTR or MTLD, the corresponding field
returns `None` and the per-text profile surfaces an explicit warning
instead of a misleadingly precise number.

**Reported per text.** Raw token count, raw type count, raw TTR ratio,
MATTR (or "unavailable"), MTLD (or "unavailable"), plus any
small-sample warnings.

**Interpretation guide.**

- MATTR is bounded `[0, 1]` like TTR. Values above ~0.78 are typical
  of varied prose; values below ~0.70 suggest heavy local repetition.
- MTLD is unbounded but typically falls between 40 and 150 for
  natural prose. Higher values indicate more sustained diversity
  before the running TTR exhausts itself.

**Comparison rule.** When both texts have MATTR available, the
comparator uses MATTR (length-robust, no length-ratio guard needed):

| Condition | Rating |
|---|---|
| `\|MATTR_a − MATTR_b\| ≤ 0.03` | Strong Match |
| `0.03 < \|MATTR_a − MATTR_b\| ≤ 0.06` | Partial Match |
| `\|MATTR_a − MATTR_b\| > 0.06` | No Match |

When MATTR is unavailable for either text, the comparator falls back
to raw TTR with the older, looser thresholds and reinstates the 2×
length-ratio Indeterminate guard for that branch:

| Condition (TTR fallback) | Rating |
|---|---|
| Either MATTR unavailable AND one text > 2× the other's length | Indeterminate |
| `\|TTR_a − TTR_b\| ≤ 0.05` | Strong Match |
| `0.05 < \|TTR_a − TTR_b\| ≤ 0.10` | Partial Match |
| `\|TTR_a − TTR_b\| > 0.10` | No Match |

MTLD is reported in the per-text profile but does not participate in
the comparison rating directly — its scale is harder to threshold
intuitively, and an analyst who wants to weigh it can read it off the
profile.

### 1.2 Latinate vs. Germanic lean

**What it measures.** Register tilt as expressed through word origins.
Latinate vocabulary (Latin/French roots) tends toward formal, abstract,
polysyllabic forms (`utilize`, `commence`, `facilitate`); Germanic
vocabulary (Old English/Norse roots) tends toward concrete, everyday
forms (`use`, `start`, `help`). A writer's habitual preference for one
stream is a stable stylistic marker.

**Word lists.** `analyzer/wordlists.py` contains curated `LATINATE` and
`GERMANIC` sets. Both extend the illustrative examples in the spec to a
few hundred entries each, with inflected forms included where common
(e.g., `utilize`, `utilizes`, `utilizing`, `utilization`).

**How it's computed.** Every alphabetic token is checked against both
lists; words not in either are simply uncategorized and excluded. The
ratio is `latinate_count / (latinate_count + germanic_count)`.

**Reported.** Latinate count, Germanic count, the ratio, and the top
hits in each category (for the per-text profile).

**Lean classification** (`_lean` in `compare.py`):

- `ratio ≥ 0.60` → Latinate-leaning
- `ratio ≤ 0.40` (with at least one categorized word) → Germanic-leaning
- `0.40 < ratio < 0.60` → mixed
- zero categorized words → indeterminate

**Comparison rule.**

| Condition | Rating |
|---|---|
| Either text has zero categorized words | Indeterminate |
| Both lean the same way (both Latinate or both Germanic) | Strong Match |
| Both fall in the mixed band | Partial Match |
| One leans Latinate and the other Germanic | No Match |
| Other mixed-vs.-pure combinations | Partial Match |

### 1.3 Pet words and habitual phrases

**What it measures.** Content words and short multiword phrases that the
writer reaches for repeatedly, separated as best as possible from words
the topic forces them to use.

**How it's computed.**

1. Tokenize and lowercase. Drop function words (the closed-class set in
   `wordlists.FUNCTION_WORDS`).
2. Flag any content word appearing **3 or more times** (or **2 or more
   times** if the total token count is below 400 — short texts need a
   lower threshold to surface anything).
3. Separately extract 2-, 3-, and 4-grams that recur at least twice,
   excluding n-grams made entirely of function words and dropping
   sub-phrases of longer matches (so "deal with it" doesn't also yield
   "deal with").
4. If the analyst supplied a **topic hint**, any flagged word that
   appears in the hint is categorized as *topical* rather than *habitual*.
   Habitual words are the ones used for comparison.

**Limitation.** Without a topic hint, the tool cannot reliably separate
topical from habitual repetition. The report shows both lists and labels
the topical/habitual split when a hint is provided.

**Comparison rule.** Take the set of habitual words and habitual phrases
from each text and count overlaps.

| Overlap | Rating |
|---|---|
| Neither text produced any habitual words | Indeterminate |
| 2 or more shared markers | Strong Match |
| Exactly 1 shared marker | Partial Match |
| No shared markers | No Match |

### 1.4 Hedges, fillers, and intensifiers

**What it measures.** Register markers tied to interpersonal stance and
formality.

**Three categories** (`wordlists.py`):

- **Informal hedges / fillers.** `basically`, `pretty much`, `kind of`,
  `sort of`, `a lot`, `just`, `really`, `actually`, `honestly`, `I mean`,
  `you know`, `I guess`, `stuff`, `things`, `whatever`, `anyway`, …
- **Intensifiers / boosters.** `very`, `extremely`, `absolutely`,
  `totally`, `completely`, `literally`, `definitely`, `clearly`,
  `obviously`, `certainly`, `truly`, `incredibly`, `remarkably`,
  `significantly`, …
- **Formal hedges** (the academic counterpart). `perhaps`, `arguably`,
  `potentially`, `somewhat`, `to some extent`, `it could be argued`,
  `one might suggest`, `it appears that`, …

Single-word markers are matched as whole tokens; multiword markers are
matched as whole-word regex sequences on the lowercased text. The result
is a normalized rate per 500 words for each subcategory.

**Dominant pattern** is computed per text:

- Informal dominant if informal-per-500 > formal-per-500 *and* informal
  rate ≥ 3 per 500 words.
- Formal dominant if formal-per-500 > informal-per-500 *and* formal rate
  ≥ 2 per 500 words.
- Otherwise mixed, or "low across the board" if both subcategories are
  zero.

**Comparison rule.**

| Condition | Rating |
|---|---|
| Same dominant pattern in both texts | Strong Match |
| One informal-dominant, the other formal-dominant | No Match |
| Any other combination | Partial Match |

### 1.5 Reading level

**What it measures.** How difficult the text is to read, synthesized
from word length (syllables per word) and sentence length. Reported
as two numbers: a US grade level and a 0–100 ease score. Sits within
the Lexical section because reading level tends to correlate with the
Latinate/Germanic ratio (§1.2) — Latinate-heavy prose is usually
harder to read because Latinate words carry more syllables. Reading
level provides useful context for the vocabulary-stream metric: a
Latinate-leaning text at a plain-English reading level is doing
something different from a Latinate-leaning text at a graduate
reading level.

**How they're computed.** Both metrics come from the `textstat`
library, which implements the standard formulas over spaCy's
tokenization:

- **Flesch-Kincaid Grade Level** = `0.39 · (words/sentences) + 11.8 ·
  (syllables/words) − 15.59`. The result maps to a US school grade
  (8 = 8th grade, 12 = high school senior, 16 = college senior, 17+ =
  graduate / specialist).
- **Flesch Reading Ease** = `206.835 − 1.015 · (words/sentences) −
  84.6 · (syllables/words)`. A 0–100 scale where higher = easier.
  Uses the same inputs as Flesch-Kincaid Grade Level but inverts the
  polarity, so plain-English prose scores in the 60–80 band.

**Validity bound.** Both metrics are unreliable on very short text.
The tool suppresses them (returns `None` + warning) when the sample
has fewer than 50 words or fewer than 3 sentences. Above that
threshold both metrics are reported with a human-readable band label
(`elementary`, `standard`, `college`, `graduate / specialist`).

**Reported per text.** Flesch-Kincaid Grade Level (to one decimal),
Flesch Reading Ease (to one decimal), and a human-readable band for
each. Warnings if the sample was too short.

**Comparison rule.** The comparator uses Flesch-Kincaid Grade Level
distance:

| Condition | Rating |
|---|---|
| Either text has reading-level metrics unavailable | Indeterminate |
| `\|grade_a − grade_b\| ≤ 2.0` | Strong Match |
| `2.0 < \|grade_a − grade_b\| ≤ 4.0` | Partial Match |
| `\|grade_a − grade_b\| > 4.0` | No Match |

Flesch Reading Ease is reported in the profile but does not
participate in the comparison rating separately — its scale is
inverted from Grade Level and covers the same underlying inputs, so
comparing on Grade Level alone avoids double-counting the signal.

---

## Section 2 — Syntactic patterns

### 2.1 Sentence length distribution

**What it measures.** Sentence rhythm: not just average length, but the
spread between long and short.

**How it's computed.** spaCy's sentence tokenizer is used directly
(handles abbreviations and decimal numbers reasonably). Word length is
the count of alphabetic tokens within each sentence.

**Reported.**

- Total sentence count
- Mean, median, and standard deviation of sentence length
- Shortest sentence (length and text) and longest sentence (length and
  text)
- Distribution by bucket: 1–10 (short), 11–20 (medium), 21–30 (long),
  31+ (very long)

The standard deviation is often more diagnostic than the mean. A writer
who alternates short punchy sentences with long elaborated ones will
have a high SD; a writer who stays in a narrow band will have a low SD.

**Comparison rule.**

| Condition (let M = mean, S = SD) | Rating |
|---|---|
| `\|M_a − M_b\| ≤ 3` and `\|S_a − S_b\| ≤ 3` | Strong Match |
| Exactly one of those two conditions holds | Partial Match |
| Neither holds | No Match |

### 2.2 Sentence-opening patterns

**What it measures.** A writer's default move at the start of a sentence
is a strong stylistic signal.

**Six categories**, assigned in this priority order to each sentence
(first match wins):

1. **Transitional connector** — sentence opens with a curated
   transitional word or phrase (`However`, `Therefore`, `Furthermore`,
   `In addition`, `On the other hand`, `In conclusion`, …).
2. **Coordinating conjunction** — sentence opens with `and`, `but`, `so`,
   `or`, `yet`, `nor`, or `for` *and* spaCy tags it as a conjunction.
3. **Participial / gerund** — first token tagged `VBG` (present
   participle) or `VBN` (past participle): "Struggling to write…",
   "Given this situation…".
4. **Pronoun subject** — first token is a personal pronoun functioning as
   a subject, or a demonstrative (`This`, `These`) functioning as a
   subject.
5. **Noun subject** — first token is a noun or proper noun (or a
   determiner-led noun phrase) functioning as a subject.
6. **Adverbial / prepositional** — first token is an adverb, preposition,
   or subordinating conjunction.

A seventh **other** bucket catches anything else (rare).

**Reported.** Raw counts and percentages per category, the top two
categories ranked, and example openings drawn from the text.

**Implementation note.** The spec listed pronoun-subject and
noun-subject before the conjunctive/transitional categories. In practice
many transitional connectors (`However`) are syntactically adverbs, so
checking the transitional list *first* prevents misclassification. The
spec's six categories are preserved exactly; only the check order is
adjusted for accuracy.

**Comparison rule.** Let `T_a`, `T_b` be the top category in each text
and `S_a`, `S_b` be the second; let `Δ` be the percentage-point
difference between the dominant categories.

| Condition | Rating |
|---|---|
| `T_a = T_b`, `S_a = S_b`, and both differences ≤ 15 pp | Strong Match |
| `T_a = T_b` but secondary or proportions diverge | Partial Match |
| `T_a ≠ T_b` | No Match |

### 2.3 Coordination vs. subordination

**What it measures.** Does the writer chain clauses additively (high
coordination) or embed them with subordinators and relative clauses
(high subordination)? This indexes syntactic complexity and
genre-fittedness.

**How it's counted.**

- **Coordinating clauses.** Tokens with `pos_ == "CCONJ"` and lemma in
  `{and, but, or, so, yet, nor, for}` are counted only when the token's
  head is a verb that has at least one **verbal** conjunct child. This
  filters out phrasal coordination (`apples and oranges`) so only
  clause-level joins are tallied.
- **Subordinate clauses.** Tokens with `pos_ == "SCONJ"` or a lemma in
  the curated `SUBORDINATORS` set (`because`, `although`, `while`, `if`,
  `since`, `whereas`, `as if`, `so that`, …) and the right dependency
  tag (`mark` or `advmod`).
- **Relative clauses.** Tokens with `dep_ == "relcl"`. The introducing
  relativizer (`who`, `which`, `that`) is recorded for the per-text
  profile.
- **Comma splices.** A best-effort heuristic: a comma followed by a
  pronoun or noun followed by a finite verb, with no coordinating
  conjunction between. Useful for flagging informal prose; not robust
  enough to rely on by itself.

**Ratio.** `(subordinate_clauses + relative_clauses) / coordinating_clauses`.
The tendency label is then one of:

- `≥ 1.50` → high subordination
- `0.75 – 1.49` → balanced
- `< 0.75` → high coordination
- zero of both → indeterminate

**Comparison rule.**

| Condition | Rating |
|---|---|
| Either text is indeterminate | Indeterminate |
| Both labels match | Strong Match |
| One is high-subordination and the other high-coordination | No Match |
| Adjacent labels (high vs. balanced, balanced vs. high) | Partial Match |

### 2.4 Punctuation rates

**What it measures.** Idiosyncratic punctuation habits — semicolon usage
and em-dash frequency are especially diagnostic of personal style.

**Counted per text** (raw and per 500 words):

- Semicolons
- Colons
- Em dashes (Unicode `—` and double-hyphen surrogates)
- Open parentheses
- Exclamation points
- Question marks
- Ellipses (`...` or `…`)
- Commas

**Comparison rule.** For each of the eight punctuation types, the two
texts are deemed to match on that type when:

- Both use it at within 50% of each other's normalized rate, **or**
- Both don't use it at all (rate = 0 for both).

Mismatch = one uses it, the other does not, or rates differ by more than
50%.

| Types matching | Rating |
|---|---|
| 5 or more | Strong Match |
| 3 or 4 | Partial Match |
| 0 to 2 | No Match |

---

## Section 3 — Discourse organization

### 3.1 Paragraph structure

**What it measures.** Paragraph length and the position of the
topic-bearing sentence.

**How paragraphs are counted.** Blank-line delimited paragraphs from the
quote-stripped text. Each paragraph is independently parsed by spaCy so
sentence boundaries are local to the paragraph.

**Reported.** Total paragraph count, mean and median number of
sentences per paragraph, range (shortest and longest), and the dominant
topic-sentence position.

**Topic-sentence position.** Per paragraph the tool scores each sentence
on three signals:

1. Count of interpretation/claim markers (`this shows`, `this means`,
   `suggests that`, `the point is`, …).
2. Count of claim-bearing verbs (`argue`, `claim`, `show`, `mean`,
   `suggest`, `demonstrate`, `imply`, `reveal`, …).
3. Topic-term density: how many of the paragraph's five most frequent
   content words appear in the sentence, divided by the sentence's
   content-word count.

Score = `2 × marker_count + verb_count + topic_density`. The sentence
with the highest score is taken as the candidate topic sentence; its
position becomes the label:

- `first` — first sentence in the paragraph.
- `last` — last sentence.
- `embedded` — middle sentence.
- `distributed` — no sentence dominates (max score = 0, or several tie
  for the top).

**Honest disclosure.** This is a heuristic. The report labels the
topic-sentence position explicitly as a heuristic estimate and recommends
human review. Topic structure in real prose is rarely cleanly
attributable to a single sentence, and the score above is a coarse proxy.

**Comparison rule.**

| Condition | Rating |
|---|---|
| Same dominant position **and** mean paragraph length within 1 sentence | Strong Match |
| One of those two conditions holds | Partial Match |
| Neither holds | No Match |

### 3.2 Transition strategy

**What it measures.** How the writer links paragraphs.

**Three labels**, applied to the first sentence of every paragraph after
the first:

- **`metadiscursive_narration`** — opens with a phrase from
  `METADISCOURSE_TEXTUAL` (`In this essay`, `As mentioned above`,
  `To summarize`, `I want to discuss`, `Now I want to`, `Let me explain`,
  …). The writer narrates their own argument structure.
- **`explicit_transitional`** — opens with a conjunctive adverb
  (`However`, `Therefore`, `Furthermore`, `Nevertheless`, …) or a stock
  transitional phrase (`On the other hand`, `In addition`, `As a result`,
  `Another concern is`, …).
- **`implicit`** — neither; the reader is left to infer the connection.

The dominant strategy is the category accounting for more than 60% of
the text's transitions; otherwise the strategy is `hybrid`. The
threshold is configurable in `discourse.py`.

**Edge case.** Single-paragraph texts have no transitions to analyze and
are reported as `indeterminate`.

**Comparison rule.**

| Condition | Rating |
|---|---|
| Either text has fewer than 2 paragraphs | Indeterminate |
| Both texts share the same dominant strategy | Strong Match |
| One is explicit-transitional and the other implicit | No Match |
| Adjacent strategies (e.g., metadiscursive vs. explicit) | Partial Match |

### 3.3 Evidence-to-claim sequencing

**What it measures.** Does the writer state a claim and then support
it, or build from examples to a conclusion? And what kind of evidence
shows up?

**Pattern labels**, per paragraph:

- `claim_evidence_interpretation` — claim → evidence → interpretation.
- `claim_evidence_no_interpretation` — claim → evidence, but no explicit
  unpacking of what the evidence means.
- `evidence_then_claim` — examples or data first, claim drawn from them.
- `claim_then_elaboration` — no external evidence; the writer develops
  the point through reasoning, hypotheticals, or personal experience.

**Detection.** External evidence is detected via:

- Inline citations matching APA-like patterns: `(Smith, 2020)`,
  `(Smith and Jones, 2021a)`, `(Smith et al., 2022)`.
- Numeric bracketed citations: `[1]`, `[42]`.
- Quoted material (any double-quote character).

Interpretation is detected via `INTERPRETATION_MARKERS` (`this shows`,
`what this means`, `the implication`, …).

**Evidence type** (separate from pattern):

- `citations` — peer-reviewed-style references present.
- `quoted_material` — direct quotation present.
- `anecdotal` — phrases like `when I was`, `my friend`, `in my
  experience`.
- `hypothetical` — `imagine`, `suppose`, `what if`, `let us say`.
- `rhetorical_question` — any `?` in the paragraph.

The primary evidence type is the most frequently observed across
paragraphs.

**Limitation.** This is approximate. The tool relies on surface signals
(citation regex, marker phrases), not actual argument parsing. It will
miss embedded evidence (e.g., a paraphrased source without parenthetical
citation) and may misfire on paragraphs that mention rhetorical
questions in passing.

**Comparison rule.**

| Condition | Rating |
|---|---|
| Same dominant pattern **and** same primary evidence type | Strong Match |
| Same pattern, different evidence types | Partial Match |
| Different dominant patterns | No Match |

### 3.4 Metadiscourse

**What it measures.** How often the writer steps outside the argument to
comment on the text or address the reader.

**Two subcategories** (rates per 500 words):

- **Textual metadiscourse** — references to the text's own structure:
  `In this essay I will…`, `As mentioned above…`, `The following
  section…`, `To summarize…`, `Let me explain…`. High textual
  metadiscourse signals a writer who narrates their argument structure;
  zero or near-zero suggests a writer who lets the argument carry the
  reader without stage directions.
- **Interpersonal metadiscourse** — direct address to the reader or
  positioning of the writer's stance: `You might think…`, `I believe`,
  `I argue`, `One could argue`, `It is important to note`, rhetorical
  questions aimed at the reader.

**Comparison rule.** Let `T_a/T_b` be the textual rates and `I_a/I_b` be
the interpersonal rates. "Close" = both nonzero and within 50% of each
other, **or** both zero.

| Condition | Rating |
|---|---|
| Both subcategories are close | Strong Match |
| One subcategory close, the other diverges | Partial Match |
| Both diverge | No Match |

---

## Section 4 — Register and stance

### 4.1 Overall register classification

**What it measures.** The text's formality level, synthesized from the
cumulative evidence of earlier features.

**Four labels:** `formal`, `semi-formal`, `mixed`, `informal`.

**How it's computed.** A scoring function (`_classify` in `register.py`)
counts formal markers and informal markers across nine signals:

| Marker | Counts toward |
|---|---|
| Zero contractions per 500w | Formal |
| ≥ 2 contractions per 500w | Informal |
| Zero first-person-singular tokens | Formal |
| ≥ 8 first-person-singular per 500w | Informal |
| Zero second-person tokens | Formal |
| ≥ 2 second-person per 500w | Informal |
| ≥ 4 informal hedges per 500w | Informal |
| ≥ 1.5 formal hedges per 500w | Formal |
| Latinate ratio ≥ 0.60 | Formal |
| Latinate ratio ≤ 0.40 (nonzero) | Informal |
| ≥ 0.5 exclamation points per 500w | Informal |
| ≥ 1 question mark per 500w | Informal |

The difference `formal_score − informal_score` determines the label:

- `≥ 3` → formal
- `1 or 2` → semi-formal
- `0` → mixed
- `−1 or −2` → semi-formal (leaning informal but moderate)
- `≤ −3` → informal

The supporting markers list is included in the report so the analyst can
see *why* a text received its label.

**Comparison rule.**

| Condition | Rating |
|---|---|
| Same label and at least one shared marker | Strong Match |
| Same label even without shared markers | Strong Match |
| Adjacent labels on the `[formal, semi-formal, mixed, informal]` ladder | Partial Match |
| Two or more steps apart on the ladder | No Match |

### 4.2 Register consistency

**What it measures.** Whether the register holds steady across the text
or shifts within it.

**How it's computed.** Each paragraph is classified individually using a
lightweight version of the same scoring (contractions, first-person,
second-person, informal hedges, exclamations). The text is **consistent**
when every paragraph receives the same label; otherwise the report lists
each *shift* with its paragraph index, source register, and destination
register.

Texts with fewer than two paragraphs are flagged as indeterminate for
this feature.

**Comparison rule.**

| Condition | Rating |
|---|---|
| Either text has fewer than 2 paragraphs | Indeterminate |
| Both texts consistent | Strong Match |
| Both shift in matching directions and locations | Strong Match |
| Both shift but only partially overlap | Partial Match |
| Both shift in different directions | No Match |
| One consistent, the other shifts | No Match |

### 4.3 Pronoun profile

**What it measures.** Pronoun usage is one of the most reliable register
markers and the cleanest signal of the writer's stance toward the
audience.

**Counted categories** (raw and per 500 words):

- **First singular** — `I, me, my, mine, myself`.
- **First plural** — `we, us, our, ours, ourselves`.
- **Second** — `you, your, yours, yourself, yourselves`.
- **Third** — all third-person variants and `it / its / itself`.
- **Impersonal `one`** — `one, ones, oneself` when spaCy tags them as
  pronouns (filters out the numeral and noun senses).
- **Existential `there`** — `there` tagged with the `expl` dependency.
- **Expletive `it`** — `it` tagged with the `expl` dependency.

**Dominant category.** Computed from the four primary categories (first
singular, first plural, second, third). Texts with no personal pronouns
report `none`.

**Comparison rule.**

| Condition | Rating |
|---|---|
| Both texts have `none` as dominant | Strong Match |
| Same dominant category and rates within 50% of each other | Strong Match |
| Same dominant category but rates differ by more than 50% | Partial Match |
| Different dominant categories | No Match |

---

## Section 5 — Comparative summary

The fifteen comparators run sequentially over the two profiles. The
report shows:

1. **Tally chips** — counts of Strong, Partial, No, and Indeterminate
   ratings.
2. **Per-feature table** — feature name, Text A summary value, Text B
   summary value, rating, explanation.
3. **Narrative** — three to five sentences naming the strongest
   convergences and divergences and offering a coarse global
   characterization:
   - 10 or more Strong Matches → "profiles converge across most measured
     dimensions; weigh whether divergences are topic- or genre-driven".
   - 6 or more No Matches → "profiles diverge on a majority of features;
     the texts appear to come from different stylistic systems".
   - Otherwise → "mixed pattern: notable convergence in some dimensions,
     divergence in others".

The narrative explicitly disclaims authorship, AI-generation, and
academic-integrity conclusions.

---

## Normalization

Every count that will be compared across texts is reported as both a
**raw count** and a **rate per 500 words**, so that samples of different
lengths remain comparable. The 500-word denominator is the spec's
convention; it has no special statistical meaning, only readability.

---

---

## Section 6 — AI-writing signs (profile-only)

Eight additional metrics, drawn from Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
catalog, describe stylistic patterns commonly observed in
large-language-model output. They appear in the per-text profile but
are **not** part of the comparative summary table — they are
descriptive markers, not comparison features. The eight:

| Metric | What it tracks | Wikipedia source |
|---|---|---|
| AI vocabulary density | `delve`, `tapestry`, `underscore`, `pivotal`, `vibrant`, etc., across three time-stratified lists | [link](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#High_density_of_%22AI_vocabulary%22_words) |
| Promotional phrasing | `nestled in the heart of`, `boasts a`, `diverse array`, `renowned for` | [link](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Promotional_and_advertisement-like_language) |
| Significance / legacy emphasis | `testament to`, `pivotal role`, `evolving landscape`, `underscores its importance` | [link](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Undue_emphasis_on_significance,_legacy,_and_broader_trends) |
| Vague attribution | `experts argue`, `industry reports`, `several sources`, `leading scholars` | [link](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Vague_attributions_and_overgeneralization_of_opinions) |
| Negative parallelisms | `not just X but Y`, `not only X but also Y`, `it is not X, it is Y` | [link](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Not_just_X,_but_also_Y) |
| Participial pseudo-analysis | sentences ending in `, highlighting...` / `, ensuring...` clauses | [link](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Superficial_analyses) |
| Rule of three | three-item parallel lists with shared POS | [link](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Rule_of_three) |
| Conclusion formulas | `despite its...`, `future outlook`, `looking ahead`, `in conclusion` | [link](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Outline-like_conclusions_about_challenges_and_future_prospects) |

Each metric reports raw count, per-500-word rate, top hits, and (for
the syntactic ones) example sentences. The section also reports a
**total markers** headline — the sum across the eight, normalized
per 500 words — as a one-glance measure of how many AI-writing
patterns the text exhibits.

**Important framing.** These are descriptive markers, not diagnostic
tests. Humans use every one of these patterns; the Wikipedia page
itself states that no single sign is determinative. The intended use
is calibration (compare against your own baseline of known-human
writing) or comparison (Text A versus Text B). Full methodology,
per-metric word lists, detection rules, and limitations are in
[ai-signs.md](ai-signs.md).

---

## Where the existing 15 features cross-reference Wikipedia

Several of the original features partially overlap with signs from
the Wikipedia catalog. The relationships:

| Tool feature | Related Wikipedia sign |
|---|---|
| 1.1 TTR | [Lexical diversity / elegant variation](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Lexical_diversity/elegant_variation) — high TTR can suggest forced synonym variation, though the relationship is weak and length-sensitive |
| 1.4 Hedges / Intensifiers | "It's important to note", "It is worth noting" overlap with Wikipedia's stock-phrase markers; we count these in the formal-hedge and metadiscourse buckets |
| 2.4 Punctuation (em dashes) | [Overuse of em dashes](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Overuse_of_em_dashes) — our per-500w em-dash rate is the same measurement |
| 3.2 Transitions | Stock transitional phrases (`Furthermore`, `Moreover`, `In conclusion`) overlap with Wikipedia's "AI vocabulary" and conclusion-formula categories |
| 3.4 Metadiscourse | Textual metadiscourse phrases (`In this essay I will`, `To summarize`) overlap with Wikipedia's conclusion-formula and outline-section signs |
| 4.2 Register Consistency | [Pronounced shift in writing style](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing#Pronounced_shift_in_writing_style) — our consistency check across paragraphs catches the strongest cases |

The AI-signs section (§6) and the existing 15 features are
deliberately complementary: the 16 features are general stylistic
descriptors useful for any comparison; the 8 AI-signs metrics are
the subset of LLM-output markers that can be cleanly
operationalized from running prose.

---

## What the tool does not do

For the things this tool intentionally avoids — AI detection,
authorship attribution, plagiarism flagging — see
[limitations.md](limitations.md).
