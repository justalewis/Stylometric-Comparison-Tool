# Glossary

Plain-language definitions for every term the report uses. In the
browser, these same definitions appear as hover tooltips on dotted-
underlined terms throughout the report — this page is the long-form
reference.

The terms are grouped by where they appear in the report. Within each
group they are listed in the order the report uses them.

> **Note.** Definitions here are deliberately non-technical. For the
> formal methodology — how each metric is computed, what comparison
> thresholds are applied — see [methodology.md](methodology.md). For
> the AI-writing-signs catalog and its Wikipedia crosswalk, see
> [ai-signs.md](ai-signs.md).

---

## Preprocessing

**Quoted material.** Direct quotations from sources. The tool removes
them before analysis because they are the *source author's* choices,
not the writer's. Double-quoted spans (straight `"..."` and curly
`"..."`) and block quotes (lines beginning with `>` or indented four
or more spaces) are stripped. The report still notes how many quoted
spans were removed and how many words they contained.

**Paragraph.** A block of prose separated from the next by a blank
line. The tool uses blank-line-delimited paragraphs from the
quote-stripped text. Empty paragraphs are dropped.

**Sample size.** How many words remain after quoted material is
removed. Below 250 words the tool warns that results may be
unreliable; 400–1000 words is the ideal range.

---

## Section 1: Lexical

**TTR (type-token ratio).** The number of distinct word forms (types)
divided by the total number of word forms (tokens). Higher TTR = more
varied vocabulary; lower TTR = more repetition.

**Type.** A distinct word form. "The cat sat on the mat" has 6 tokens
but 5 types because "the" appears twice.

**Token.** A single word occurrence. Punctuation and numbers are not
counted as tokens.

**Latinate.** Words derived from Latin or French roots (`utilize`,
`commence`, `facilitate`). Tend to be formal, abstract, polysyllabic.

**Germanic.** Words derived from Old English or Old Norse (`use`,
`start`, `help`). Tend to be concrete, shorter, everyday.

**Latinate/Germanic ratio.** Latinate hits divided by the total of
Latinate plus Germanic hits. Higher than 0.60 = Latinate lean; lower
than 0.40 = Germanic lean; in between = mixed.

**Pet word.** A content word the writer reaches for repeatedly that
the topic doesn't strictly require. With a topic hint, the tool
separates these from words that are simply topical.

**Habitual phrase.** A 2-4 word phrase that recurs more than once and
isn't a stock function-word combination. Examples: "deal with it",
"at the end of the day", "in terms of".

**Hedge.** A softener that qualifies a claim. *Informal hedges*
(`basically`, `kind of`, `pretty much`) signal conversational
register; *formal hedges* (`perhaps`, `arguably`, `it could be
argued`) signal academic register.

**Filler.** A word that fills space without carrying meaning (`just`,
`really`, `actually`, `like`, `you know`). Common in informal writing.

**Intensifier.** A booster that strengthens a claim (`very`,
`extremely`, `absolutely`, `literally`, `definitely`). High
intensifier rates signal emphatic, often informal register.

---

## Section 2: Syntactic

**Sentence length.** Number of word tokens per sentence. The mean and
standard deviation together describe the writer's rhythm: high SD =
mix of short and long; low SD = uniform length.

**Standard deviation (SD).** A measure of spread. Low SD = sentences
cluster around the mean; high SD = wide range from short to long. The
tool reports SD alongside the mean because rhythm is often more
diagnostic than average length.

**Sentence opener.** The first grammatical element of a sentence.
The tool classifies openers into six categories: pronoun subject,
noun subject, transitional connector, adverbial/prepositional,
participial/gerund, or coordinating conjunction.

- **Pronoun subject.** A sentence that starts with a personal or
  demonstrative pronoun acting as the subject: "I think...", "This
  means...", "They argue...".
- **Noun subject.** A sentence that starts with a noun or noun phrase
  as the subject: "Universities are built...", "The most immediate
  concern...".
- **Transitional connector.** A sentence-initial word or phrase that
  signals the logical relationship to what came before: "However",
  "Therefore", "Furthermore", "On the other hand".
- **Adverbial opener.** A sentence that starts with an adverbial
  phrase, prepositional phrase, or subordinator: "In this essay",
  "As a result", "Even though".
- **Participial/gerund opener.** A sentence that starts with an
  `-ing` or `-ed` verb form: "Struggling to write...", "Given this
  situation...".
- **Coordinating conjunction opener.** A sentence that starts with
  `and`, `but`, `so`, `or`, `yet`, `nor`, or `for`.

**Coordination.** Linking clauses with coordinating conjunctions
(`and`, `but`, `or`, `so`, `yet`, `nor`). Produces additive,
paratactic prose — one thing, then another, then another.

**Subordination.** Embedding one clause inside another with
subordinators (`because`, `although`, `while`, `if`) or relative
clauses. Produces complex, syntactically embedded prose — one thing
*because of* another, or *which* leads to another.

**Subordinator.** A word that introduces a subordinate clause:
`because`, `although`, `though`, `while`, `when`, `if`, `since`,
`after`, `before`, `unless`, `whereas`.

**Relative clause.** A clause introduced by `who`, `which`, or `that`
that modifies a preceding noun: "the writer who argued...", "the book
that I read...".

**Comma splice.** Two independent clauses joined with only a comma,
no conjunction: "I came, I saw, I conquered." An error in formal
writing, common in informal prose. The tool flags suspected splices
but the detector is heuristic — treat counts as approximate.

**Em dash.** A long dash used for parenthetical asides, abrupt shifts,
or emphasis (the character `—`, or `--` typed as a substitute).
Frequency varies enormously between writers; high em-dash use is a
strong personal-style marker.

---

## Section 3: Discourse

**Topic sentence.** The sentence in a paragraph that states its main
claim or topic. Position can be first, last, embedded (middle), or
distributed across several sentences.

**Distributed topic.** A paragraph whose main claim is spread across
multiple sentences rather than concentrated in one. The tool labels
these as "distributed" when no single sentence dominates by the
scoring heuristic.

**Transition strategy.** How the writer links paragraphs to each
other. Three patterns: explicit transitional connectors,
metadiscursive narration ("In this essay I will..."), or implicit
logical connection. "Hybrid" means no single strategy dominates.

**Metadiscursive narration.** Sentences where the writer announces
the text's own structure: "Now I want to discuss...", "Let me
explain...", "In this section...".

**Evidence type.** What kind of supporting material the writer uses:
peer-reviewed citations, direct quotations, anecdotes, hypothetical
scenarios, rhetorical questions, or general reasoning.

**Interpretation marker.** A phrase that signals the writer is moving
from evidence to claim: "this shows", "what this means", "the
implication is", "in other words".

**Metadiscourse.** Moments where the writer talks about the text or
addresses the reader rather than the subject matter.

- **Textual metadiscourse.** References to the text's own structure:
  "In this essay I will", "As mentioned above", "To summarize".
- **Interpersonal metadiscourse.** Direct address to the reader or
  positioning of the writer's stance: "You might think", "I believe",
  "It is important to note".

---

## Section 4: Register

**Register.** The formality level of the text. Four labels:

- **Formal.** No first/second person, no contractions, Latinate
  vocabulary, complex subordinated syntax, citation apparatus, no
  rhetorical questions or exclamation points.
- **Semi-formal.** May use first person ("I argue"), avoids second
  person, few or no contractions, mostly Latinate vocabulary,
  moderate sentence complexity.
- **Informal.** Uses first and/or second person freely, may use
  contractions, relies on Germanic vocabulary, shorter sentences,
  may include rhetorical questions and conversational hedges.
- **Mixed.** Features from multiple levels appear in different parts
  of the text.

**Register consistency.** Whether the text holds the same register
throughout, or shifts between paragraphs. Shifts are reported with
paragraph index and direction (e.g., "formal → informal at
paragraph 3").

**Pronoun profile.** The mix of first-singular, first-plural,
second-person, and third-person pronouns. One of the most reliable
register markers.

- **First person singular.** `I, me, my, mine, myself`. Heavy use
  signals personal voice and informal register.
- **First person plural.** `we, us, our, ours, ourselves`.
- **Second person.** `you, your, yours, yourself`. Directly addresses
  the reader; rare in formal academic writing.
- **Third person.** `he/him/his, she/her/hers, they/them/their, it/
  its` and related forms.
- **Expletive.** A grammatically required placeholder pronoun: "*It*
  is important that...", "*There* are many reasons". The tool counts
  these separately so they don't inflate the third-person count.

---

## Section 5: Comparison ratings

For each of the 15 features, the tool produces one of four ratings:

- **Strong Match.** The two texts behave the same way on this
  feature, within the spec's thresholds.
- **Partial Match.** The texts agree on the dominant pattern but
  diverge on secondary measurements.
- **No Match.** The texts behave differently on this feature.
- **Indeterminate.** Not enough signal to decide — sample too short,
  no relevant tokens, length difference too large, or fewer than two
  paragraphs.

**Per 500 words.** A normalized rate that lets you compare counts
across samples of different lengths. If a text has 8 hits in 1000
words, the per-500-word rate is 4.

---

## Section 6: AI-writing signs

These eight metrics describe *stylistic patterns* commonly observed
in large-language-model output, catalogued on Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
page. They are descriptive — high rates suggest the writer reaches
for these patterns, not that the text was AI-generated. Humans use
all of these too. See [ai-signs.md](ai-signs.md) for the full
methodology and per-metric Wikipedia links.

**AI-writing sign.** A stylistic pattern commonly observed in
large-language-model output. High rates are descriptive, not
diagnostic.

**AI vocabulary.** Words documented as statistically frequent in LLM
output post-2022: `delve`, `tapestry`, `underscore`, `pivotal`,
`vibrant`, `meticulous`, `showcasing`, `intricate`, `fostering`,
`highlighting`, `enhance`, and others. The tool tracks three
time-stratified lists (2023–mid-2024, mid-2024–mid-2025, mid-2025+)
because the LLM vocabulary drift over time.

**Promotional phrasing.** Travel-guide or press-release style:
"nestled in the heart of", "boasts a diverse array", "renowned for",
"state-of-the-art".

**Significance emphasis.** Generic statements connecting the subject
to broader importance: "stands as a testament to", "pivotal role in
shaping", "underscores its importance", "evolving landscape".

**Vague attribution.** References to unnamed authorities: "industry
reports", "experts argue", "several sources", "leading scholars
suggest".

**Negative parallelism.** Contrastive constructions that deny one
thing and assert another: "not just X but Y", "not only X but also
Y", "it is not X, it is Y".

**Participial tail.** A sentence ending in a comma + present-
participle clause that makes an unattributed analytical claim:
"...highlighting the importance of X", "...ensuring sustainability".

**Rule of three.** Three parallel items in a list or series: "X, Y,
and Z". Common in human writing too, but overused in LLM output for
rhythmic effect.

**Conclusion formula.** Stock closing patterns: "despite its
challenges...", "looking ahead", "the future outlook is promising",
"in conclusion".

---

## Maintenance

The same definitions live in `analyzer/glossary.py` (as a Python
`dict[str, str]`) so the in-app tooltips and this page stay aligned.
When adding a new term:

1. Add it to `analyzer/glossary.py`.
2. Add it here in the appropriate section.
3. Wrap the term in `{{ gloss('Term') }}` in
   [templates/report.html](../templates/report.html) wherever it
   first appears in the report.
