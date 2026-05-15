# Stylometric Comparison Tool: Analysis Specification

> Reproduced verbatim from the original specification that guided the
> tool's design. This document is the source of truth for what the tool
> implements. Where the implementation made adjustments
> (e.g., sentence-opener check order, topic-sentence heuristic), they are
> documented in [methodology.md](methodology.md).

## Purpose

This tool accepts two plain-text samples (approximately 300–1500 words each) and produces a structured comparative stylometric profile. Its primary use case is evaluating whether two texts plausibly share the same author by analyzing lexical preferences, syntactic patterns, discourse organization, and register. The tool is not a plagiarism detector or AI classifier; it describes *what each text does linguistically* and reports the degree of convergence or divergence between the two profiles.

The tool produces two outputs: (1) an individual profile for each text, and (2) a comparative summary that rates each feature as **Strong Match**, **Partial Match**, **No Match**, or **Indeterminate**, with a brief explanation for each rating.

---

## Section 1: Lexical Preferences

Lexical analysis examines what words the writer chooses, how varied that vocabulary is, and what habitual patterns emerge in word selection.

### 1.1 Type-Token Ratio (TTR)

Calculate the number of unique word forms (types) divided by the total number of word tokens. Tokenize by splitting on whitespace and stripping punctuation; lowercase all tokens before counting. Report both the raw counts (types, tokens) and the ratio to two decimal places.

Interpretation guidance:
- TTR above 0.55 in a 500-word sample indicates relatively high lexical diversity.
- TTR below 0.40 indicates relatively constrained vocabulary with heavy repetition.
- TTR is sensitive to text length (longer texts produce lower ratios mechanically), so comparisons are most meaningful when both samples are within roughly 30% of each other in word count. If the samples differ substantially in length, note this as a confound.

When comparing: a difference of 0.05 or less is a Strong Match; 0.05–0.10 is Partial Match; greater than 0.10 is No Match. If one text is more than double the other's length, rate Indeterminate.

### 1.2 Latinate vs. Germanic Vocabulary Tendency

English draws on two major etymological streams that carry distinct register associations. Latinate vocabulary (derived from Latin and French) tends toward formal, abstract, and polysyllabic forms. Germanic vocabulary (from Old English and Norse) tends toward concrete, shorter, everyday forms. Many concepts have near-synonyms from both streams, and a writer's habitual preference for one stream over the other is a stable stylistic marker.

The tool should maintain two reference lists:

**Latinate markers** (illustrative, not exhaustive): utilize, commence, facilitate, subsequent, demonstrate, implement, exacerbate, prohibit, integrate, compromise, formulate, substitution, accessibility, credibility, technological, adaptability, prioritize, preservation, ultimately, increasingly, furthermore, consequently, nevertheless, substantial, acquisition, methodology, conceptualize, necessitate, endeavor, ascertain, preliminary, constitute, encompass, articulate, proliferation, trajectory, parameter, paradigm, implications, infrastructure, jurisdiction, articulate, delineate, substantiate.

**Germanic markers** (illustrative, not exhaustive): use, start, begin, help, next, show, set up, make worse, ban, blend, weaken, shape, swap, reach, get, give, put, look, find, think, need, keep, want, try, take, bring, build, work, handle, share, grow, rise, fall, kind, type, way, fair, strong, weak, deep, wide, sharp, hard.

For each text, scan content words and tally how many fall into each category. Report the raw count in each category and the ratio (Latinate count / total categorized words). Words not in either list are uncategorized and excluded from the ratio.

Additionally, identify specific cases where the writer chose a Latinate form where a common Germanic alternative exists (or vice versa), and quote the examples. These specific choices are more diagnostically revealing than the aggregate count.

When comparing: if both texts lean the same direction (both above 0.60 Latinate, or both below 0.40), that is a Strong Match. If both are in the 0.40–0.60 middle range, Partial Match. If one text is above 0.60 and the other below 0.40, No Match.

### 1.3 Pet Words and Habitual Phrases

Identify content words and multiword phrases that recur more than expected and are not strictly required by the topic. A word is "required by the topic" if it names a key concept under discussion and has no ready synonym in context (e.g., "AI" in an essay about AI is required; "basically" is not). To operationalize this:

1. Count all content words (exclude closed-class function words: articles, prepositions, pronouns, conjunctions, auxiliary verbs, common determiners).
2. Flag any content word appearing 3 or more times, or any content word appearing twice if the total text is under 400 words.
3. Manually categorize each flagged word as **topical** (required by subject matter) or **habitual** (could be replaced by a synonym or omitted without changing meaning).
4. Also scan for repeated multiword phrases (2–4 words) that appear more than once: collocations like "brings up the question," "at the end of the day," "in terms of."

Report habitual words and phrases for each text, with counts and example sentences.

When comparing: if the two texts share 2 or more habitual words/phrases (not topical ones), Strong Match. If they share 1, Partial Match. If they share none, No Match. If neither text produces habitual words at all, Indeterminate.

### 1.4 Informal Hedges, Fillers, and Intensifiers

Count occurrences of the following categories, which function as register markers:

**Hedges and fillers:** basically, pretty much, kind of, sort of, a lot, just, really, actually, honestly, like (non-comparative), I mean, you know, I guess, stuff, things, whatever, anyway, anyways.

**Intensifiers and boosters:** very, extremely, absolutely, totally, completely, literally, definitely, clearly, obviously, certainly, truly, incredibly, remarkably, significantly.

**Formal hedges (for contrast):** perhaps, arguably, potentially, somewhat, to some extent, it could be argued, one might suggest, it appears that.

Report the count in each subcategory and the total per 500 words (normalized rate). These markers are strong register indicators: high informal-hedge counts signal conversational writing; high formal-hedge counts signal academic register.

When comparing: if both texts are in the same subcategory dominant pattern (both high-informal, both high-formal, or both low across the board), Strong Match. If one text uses informal hedges and the other uses formal hedges, No Match.

---

## Section 2: Syntactic Patterns

Syntactic analysis examines how the writer constructs sentences: their length, complexity, variety, and characteristic structural habits.

### 2.1 Sentence Length Distribution

Tokenize the text into sentences (split on terminal punctuation: period, question mark, exclamation point; handle abbreviations and decimal numbers gracefully). For each sentence, count word tokens. Report:

- Total sentence count
- Mean sentence length (words)
- Median sentence length
- Standard deviation
- Shortest and longest sentences (word count and the sentence itself)
- Distribution by bucket: short (1–10 words), medium (11–20), long (21–30), very long (31+)

The standard deviation and distribution shape are often more diagnostic than the mean. A writer who alternates between very short and very long sentences will have a high SD; a writer who stays in a narrow band will have a low SD. Both the mean and the SD should be compared.

When comparing: if means are within 3 words of each other AND standard deviations are within 3 of each other, Strong Match. If only one of those conditions is met, Partial Match. If neither, No Match.

### 2.2 Sentence-Opening Patterns

For each sentence, identify the first grammatical element. Categorize into the following (check in order; assign the first match):

1. **Subject-first (pronoun):** sentence opens with a personal or demonstrative pronoun as subject ("I think," "This means," "It is," "They argue," "We need")
2. **Subject-first (noun/NP):** sentence opens with a noun phrase as subject ("Universities are built," "The most immediate concern," "Students with disabilities")
3. **Adverbial/prepositional opener:** sentence opens with a fronted adverbial phrase or prepositional phrase ("In this essay," "As a result," "Instead of," "Now," "Even though")
4. **Transitional connector:** sentence opens with a conjunctive adverb or transitional phrase ("However," "Therefore," "Furthermore," "On the other hand," "In conclusion")
5. **Participial/gerund opener:** sentence opens with a present or past participle phrase ("Struggling to write," "Given this situation," "Used responsibly")
6. **Coordinating conjunction opener:** sentence opens with and, but, so, or, yet, for ("But the real issue," "So to ethically use," "And that means")

Report the count and percentage for each category. Writers tend to have a default sentence-opening pattern; a writer who opens 70% of sentences with a pronoun subject has a different syntactic profile from one who opens 40% with adverbial phrases.

When comparing: if the top two categories are the same in both texts and within 15 percentage points of each other, Strong Match. If the top category matches but proportions diverge by more than 15 points, Partial Match. If the top categories differ, No Match.

### 2.3 Coordination vs. Subordination Tendency

This feature measures the writer's preference for joining clauses with coordinating structures (and, but, or, so, comma splices, semicolons linking independent clauses) versus subordinating structures (because, although, when, while, if, since, after, before, that-clauses, relative clauses with who/which/that).

Count:
- **Coordinating conjunctions** linking clauses (not those joining words or phrases): and, but, or, so, yet, for, nor when connecting independent clauses
- **Comma splices** (two independent clauses joined by a comma without a conjunction): these are errors in formal writing but frequent in informal writing and are diagnostically useful
- **Subordinating conjunctions:** because, although, though, even though, while, when, if, since, after, before, unless, whereas, as (causal), so that, in order that
- **Relative clauses:** who, which, that (when introducing a clause, not as a demonstrative)

Report the ratio of subordination to coordination. A higher ratio indicates more syntactically complex, embedded prose; a lower ratio indicates more paratactic, additive prose. Also note the specific subordinators the writer favors: some writers rely heavily on "because" while others prefer "although" or "while."

When comparing: if both texts fall in the same third of the ratio range (both high-subordination, both balanced, or both high-coordination), Strong Match. Otherwise, Partial Match or No Match depending on distance.

### 2.4 Punctuation Patterns

Count occurrences of the following per 500 words (normalized rate):

- Semicolons
- Colons
- Em dashes (or double hyphens functioning as em dashes)
- Parentheses (count opening parens)
- Exclamation points
- Question marks (in non-interrogative contexts, i.e., rhetorical questions)
- Ellipses
- Commas (total count, since comma density reflects clause complexity and listing habits)

Certain punctuation marks are strong personal-style markers. Semicolon usage varies enormously between writers; some never use them, others average one per paragraph. Em dash frequency is similarly diagnostic. Exclamation points and rhetorical questions mark informal, direct-address register.

When comparing: for each punctuation type, check whether both texts use it at a similar rate (within 50% of each other per 500 words) or whether one uses it and the other does not. If 5+ punctuation types match in rate, Strong Match. If 3–4, Partial Match. Fewer, No Match.

---

## Section 3: Discourse Organization

Discourse analysis examines how the writer structures paragraphs, sequences claims and evidence, manages transitions, and positions themselves in the text.

### 3.1 Paragraph Structure

Count paragraphs (defined by hard line breaks, excluding title/header lines). For each paragraph, count sentences. Report:

- Total paragraph count
- Mean paragraph length in sentences
- Range (shortest and longest paragraphs)

Then, for each paragraph, identify the **topic sentence position:**
- **First sentence:** the paragraph opens with its main claim or topic.
- **Last sentence:** the paragraph builds toward its claim, which appears at the end.
- **Embedded:** the main claim appears in a middle sentence, with setup before it and elaboration after.
- **Distributed/absent:** no single sentence captures the paragraph's main point; the claim is distributed across multiple sentences or implicit.

Report the dominant pattern (which position accounts for the plurality of paragraphs).

When comparing: if both texts share the same dominant topic-sentence position and are within 1 sentence of each other on mean paragraph length, Strong Match. If the dominant position matches but lengths diverge, or vice versa, Partial Match. If neither matches, No Match.

### 3.2 Transition Strategy

Examine how paragraphs connect to each other. Categorize the writer's dominant approach:

- **Explicit transitional phrases:** the writer uses overt connectors at or near the start of paragraphs ("Furthermore," "On the other hand," "Another concern is," "In addition," "However").
- **Metadiscursive narration:** the writer announces what the essay will do next ("Now we should talk about," "I want to discuss," "Even though I have basically explained").
- **Implicit logical connection:** the writer relies on the reader to infer the relationship between paragraphs from content alone, without explicit connectors.
- **Hybrid:** a mix of the above with no single dominant strategy.

Provide examples of actual transitions from the text. Note whether transitions are formulaic (drawn from a small set of stock phrases) or varied.

When comparing: if both texts use the same dominant strategy, Strong Match. If both are explicit but differ in character (e.g., one uses metadiscursive narration while the other uses stock academic connectors), Partial Match. If one is explicit and the other implicit, No Match.

### 3.3 Evidence-to-Claim Sequencing

For each body paragraph, determine the writer's typical pattern for relating claims to supporting material:

- **Claim → Evidence → Interpretation:** the writer states a point, provides supporting material (quotation, example, data), then explains what it means.
- **Claim → Evidence (no interpretation):** the writer states a point, provides support, but does not explicitly interpret or connect the evidence back to the claim.
- **Evidence → Claim:** the writer presents examples or data first, then draws a concluding claim from them.
- **Claim → Elaboration (no external evidence):** the writer states a point and develops it through further reasoning, hypotheticals, or personal experience without introducing outside sources.

Also note the *type* of evidence the writer uses: peer-reviewed sources with formal citation, anecdotal examples, hypothetical scenarios, personal experience, appeals to common knowledge, or rhetorical questions functioning as implicit evidence.

When comparing: if both texts share the same dominant claim-evidence pattern AND the same primary evidence type, Strong Match. If the pattern matches but evidence types differ, Partial Match. If neither matches, No Match.

### 3.4 Metadiscourse

Metadiscourse refers to moments where the writer comments on the text itself rather than the subject matter. Scan for two subcategories:

**Textual metadiscourse** (references to the text's own structure): "In this essay I will," "As mentioned above," "The following section," "To summarize," "Basically what I'm trying to say is," "Let me explain."

**Interpersonal metadiscourse** (direct address to the reader or positioning of the writer's stance): "You might think," "I believe," "It is important to note," "One could argue," "Do you enjoy...?" (rhetorical questions directed at the reader).

Count instances of each subcategory and report a normalized rate per 500 words. High textual metadiscourse suggests a writer who narrates their own argument structure, common in developmental writers. Low or zero metadiscourse suggests a writer who lets the argument speak without stage directions.

When comparing: if both texts have similar normalized rates (within 50% of each other) in both subcategories, Strong Match. If one subcategory matches and the other diverges, Partial Match. If both diverge substantially, No Match.

---

## Section 4: Register and Stance

Register analysis characterizes the formality level and the writer's self-presentation within the text.

### 4.1 Overall Register Classification

Based on the cumulative evidence from all prior features, classify each text's register:

- **Formal:** no first or second person (or only the editorial "one"), no contractions, no informal hedges, Latinate vocabulary preference, complex subordinated syntax, citation apparatus, absence of rhetorical questions and exclamation points.
- **Semi-formal:** may use first person ("I argue"), avoids second person, few or no contractions, mostly Latinate vocabulary but with some plain alternatives, moderate sentence complexity, may or may not include citations.
- **Informal:** uses first and/or second person freely, may use contractions, relies on Germanic vocabulary, shorter sentences with coordination dominance, may include rhetorical questions, conversational hedges (basically, just, a lot), anecdotal evidence.
- **Mixed:** exhibits features of two or more register levels in different sections of the text.

Cite specific evidence from the text supporting the classification. Name the strongest register markers (the 3–4 features that most clearly place the text).

When comparing: if both texts receive the same classification and the supporting markers overlap, Strong Match. If both are adjacent categories (e.g., one semi-formal and one formal), Partial Match. If they are two or more levels apart (e.g., informal vs. formal), No Match.

### 4.2 Register Consistency

Evaluate whether the register is stable throughout the text or shifts. If it shifts:

- Identify where (which paragraph or sentence)
- Describe the direction (e.g., informal → more formal in conclusion; formal → informal in a specific paragraph)
- Estimate the magnitude (slight tightening vs. wholesale register change)

Register inconsistency can indicate multiple authorial processes (e.g., a writer drafting some sections independently and others with assistance), or it can reflect normal variation in a developing writer. The tool should report the finding without interpreting the cause.

When comparing: if both texts are consistent, or both show shifts in the same direction and location (e.g., both loosen in a middle paragraph), Strong Match. If one is consistent and the other shifts, or they shift in opposite directions, No Match.

### 4.3 Pronoun Profile

Count all personal pronoun tokens and categorize:

- **First person singular:** I, me, my, mine, myself
- **First person plural:** we, us, our, ours, ourselves
- **Second person:** you, your, yours, yourself
- **Third person:** he/she/they/it and their variants
- **Impersonal constructions:** one, it (expletive, as in "it is important"), there (existential, as in "there are many")

Report raw counts and normalized rates per 500 words. The pronoun profile is one of the most reliable register markers. A text with 10+ first-person-singular instances per 500 words has a fundamentally different stance from one with zero. A text with frequent second-person address is performing a different rhetorical relationship with its audience than one using exclusively third person.

When comparing: if both texts use the same dominant pronoun category (or both avoid personal pronouns) and rates are within 50% of each other, Strong Match. If the dominant category matches but rates diverge significantly, Partial Match. If dominant categories differ (e.g., one uses first-person-singular and the other uses no personal pronouns), No Match.

---

## Section 5: Comparative Summary

After completing all individual analyses, produce a summary table with the following columns:

| Feature | Text 1 Value | Text 2 Value | Rating | Explanation |
|---------|-------------|-------------|--------|-------------|
| 1.1 TTR | | | | |
| 1.2 Latinate/Germanic | | | | |
| 1.3 Pet Words | | | | |
| 1.4 Hedges/Fillers | | | | |
| 2.1 Sentence Length | | | | |
| 2.2 Sentence Openers | | | | |
| 2.3 Coord/Subord | | | | |
| 2.4 Punctuation | | | | |
| 3.1 Paragraph Structure | | | | |
| 3.2 Transitions | | | | |
| 3.3 Evidence-Claim | | | | |
| 3.4 Metadiscourse | | | | |
| 4.1 Register | | | | |
| 4.2 Consistency | | | | |
| 4.3 Pronoun Profile | | | | |

After the table, provide a narrative summary (3–5 sentences) describing the overall pattern: how many features match, where the strongest convergences and divergences lie, and what the profile suggests about the relationship between the two texts. The tool should not assert conclusions about authorship, AI generation, or academic integrity; it should report findings and let the analyst draw conclusions.

---

## Implementation Notes

### Input Format
- Two plain-text strings, labeled Text A and Text B.
- Optional: the analyst can supply a brief topic description (e.g., "both essays argue about AI in education") so the tool can better distinguish topical from habitual word repetition.

### Output Format
- A structured report with clearly labeled sections matching the spec above.
- Each section includes: the raw metric, a qualitative interpretation for each text, and the comparative rating.
- The final summary table and narrative.

### Handling Quoted Material
Quoted material (direct quotations from sources, identified by quotation marks or block-indent formatting) should be excluded from all lexical and syntactic counts. Quoted words are the source author's choices, not the writer's. The tool should identify and strip quoted material before running its counts, but note the *presence* and *length* of quoted material as a feature (since the decision to quote at length vs. paraphrase is itself a stylistic choice).

### Text Length Requirements
Both samples should be at least 250 words (after stripping quoted material). If either sample falls below this threshold after stripping quotes, the tool should warn that results may be unreliable due to small sample size. Ideal sample size is 400–1000 words of the writer's own prose per text.

### Normalization
All frequency counts that will be compared across texts should be reported as both raw counts and normalized rates per 500 words, to allow comparison across samples of different lengths.
