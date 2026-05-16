# Using the Tool in Teaching

This document is for instructors who want to use the comparison tool
in writing classrooms — first-year composition, writing-intensive
courses across the disciplines, advanced rhetoric and style courses,
graduate seminars on academic writing. It explains the framing the
tool was built for, sketches several classroom workflows, and offers
guidance on the conversations the results are meant to support.

The tool was built specifically to support these conversations. If
you read only one document in this repository, this is the one.

---

## What the tool is for

The tool produces a structured stylometric description of two writing
samples and reports the degree of convergence or divergence between
them. It is **descriptive**, not diagnostic — it shows the analyst
what each text does linguistically, and the analyst draws the
inferences.

In a teaching context the tool is most useful for:

1. **Surfacing the components of voice.** Students often think of
   "voice" as something amorphous, intuitive, ineffable. The tool's
   per-text profile breaks voice into countable parts — sentence
   length distribution, Latinate-vs.-Germanic vocabulary, paragraph
   topic position, pronoun profile, register markers — and shows the
   student that their stylistic choices add up to a measurable
   profile. This makes "voice" something they can work *on* rather
   than something they have to wait for.

2. **Comparing a student to themselves.** The most powerful use is
   to compare two samples by the same student across genres,
   contexts, or stages of revision. The differences are not
   evidence of dishonesty; they are an inventory of what changes
   when the writer's situation changes. That inventory is the
   beginning of a meta-cognitive conversation about style.

3. **Opening conversations when AI use is suspected.** When you
   notice a stylistic gap between two pieces of student work — an
   in-class essay next to a take-home draft, say — the tool gives
   you something concrete to point to. "This doesn't sound like
   you" is not a productive starting point. "Your in-class work
   shows a Germanic-leaning vocabulary, second-person address, and
   high informal-hedge density; this draft shows Latinate-leaning
   vocabulary, no second-person, formal hedges, and four 'rule of
   three' triplets" *is* a productive starting point.

The tool is **not** for:

- Adjudicating academic integrity. The methodology section makes this
  explicit; see [limitations.md](limitations.md). Reasons go beyond
  the legal caveats — a confident "AI detection" claim from a tool
  like this would be both wrong on the technical merits and harmful
  to the kind of conversation the tool is designed to enable.
- Replacing your reading of the student's work. The tool surfaces
  patterns; your reading provides context, charity, history with the
  student, and judgment.
- Producing a number you can put in a grade book.

---

## Three classroom workflows

### Workflow 1: Self-comparison across drafts

Have each student submit two drafts of the same paper for comparison.
Run the comparison together — either projecting the report in class
or having students run it on their own at office hours.

What to look at:

- **Sentence-length distribution.** Did revision tighten or stretch
  sentences? Did the standard deviation change?
- **Sentence openers.** Did the writer break out of a default
  opening pattern when they revised?
- **Coordination vs. subordination.** Did the embedded complexity
  shift?
- **Pet words and habitual phrases.** Did the revision excise
  tics, or did the tics survive?
- **Topic-sentence position.** Did the writer move from
  "distributed" to "first" or vice versa?

The point isn't to identify a "better" draft. The point is to make
the writer's choices visible to them.

### Workflow 2: Cross-genre self-comparison

Have students submit two samples in different genres — for example,
an analytical essay and a personal reflection — and compare them.
Most students will see a striking gap: different register, different
pronoun profiles, different sentence rhythms, sometimes different
vocabulary streams. The conversation is then about *why* their voice
adapts to genre, what stays constant (the habitual phrases, the
sentence-rhythm signature), and what the through-line of "their"
voice actually is.

This workflow is especially useful early in a course when students
are still learning that academic register isn't a costume they put
on but a set of constraints they negotiate.

### Workflow 3: AI-augmentation conversation

When you see a gap between two pieces of work by the same student
that you suspect involves AI assistance, run the comparison and meet
with the student. Bring up the report — not as evidence, but as a
starting point. Useful framings:

- "I want to talk about your writing across these two assignments.
  Will you walk me through how each one came together?"
- "Some of the patterns the tool surfaces — Latinate-leaning
  vocabulary, 'evolving landscape' phrasing, rule-of-three
  triplets — are things AI tools tend to produce by default. I'm not
  asking whether you used one. I'm asking what you wanted this
  paragraph to sound like."
- "If you used an AI tool, that's a conversation worth having on its
  own terms — not because I'm trying to catch you, but because the
  tool is going to smooth your voice toward its defaults, and your
  voice is what we're trying to develop here."

These conversations work best when they are **about writing**, not
about cheating. The student usually knows whether they used a tool.
You are not the right person to adjudicate that. You *are* the right
person to talk about voice.

---

## Talking to students about voice

A few framings that come up repeatedly:

### "Voice isn't decoration."

The most important thing the tool helps make visible. Style isn't
something layered on top of meaning — it *is* meaning. The choice
between "use" and "utilize," between a 12-word sentence and a
35-word one, between starting a sentence with "However" and
starting it with "I," between a paragraph that opens with its claim
and one that builds toward it: these are choices about how the
writer wants to position themselves and the reader. They aren't
optional.

### "Smoothing is loss."

When AI tools take a developing writer's draft and "improve" it,
they make a series of stylistic decisions on the writer's behalf —
toward more Latinate vocabulary, more subordination, more
metadiscursive narration, more rule-of-three patterns. These are
defaults baked into the training distribution. They are not
neutral. They displace the writer's own emerging stylistic
identity. For an experienced writer who already has a stable voice,
that displacement is annoying and reversible. For a developing
writer, it short-circuits the apprenticeship they are trying to
undertake.

### "Voice is figured out, not found."

Students sometimes describe voice as if it's something they have to
"find" — as if it's already out there waiting for them. The more
useful framing is that voice is the cumulative trace of decisions
the writer keeps making about words, sentences, paragraphs, and
audience. The tool helps make those decisions visible so they can
be reflected on, refined, and owned.

### "The samples agree on six features, diverge on nine."

When the tool produces a comparison summary, the numerical breakdown
gives students something concrete to react to. You can ask: which of
the agreements feel like things you'd want to keep stable across
your writing? Which of the divergences feel like genre-appropriate
adaptations and which feel like inconsistencies you'd want to
investigate?

---

## What the AI-writing-signs section is for

[Section 6](ai-signs.md) of the report measures eight stylistic
markers commonly found in LLM output: AI-vocabulary density,
promotional phrasing, significance/legacy emphasis, vague
attribution, negative parallelisms, participial pseudo-analysis,
rule of three, and conclusion formulas.

In teaching:

- **Use the section to teach the markers themselves.** Many
  developing writers don't yet recognize the rhetorical moves
  AI tools default to. Seeing them named and counted helps the
  student notice them in their own reading and resist them in
  their own writing.
- **Use the section as a starting point for revision.** When a
  student's draft lights up the AI-signs section, the question
  isn't *did you use AI*. The question is: *do you want your
  writing to sound this way?* Some of the markers (significance
  emphasis, conclusion formulas) are common in poorly written
  human academic prose too; the tool is surfacing the move, not
  attributing it.
- **Use the section to calibrate.** Run your own work, or work
  you know to be human-written, and look at the numbers. That
  becomes your baseline. The Wikipedia source page is explicit
  that no single sign is determinative — clusters at high rates
  across multiple metrics are the meaningful signal.

The tool deliberately does **not** rate the AI-signs section as
"Strong Match" / "No Match" the way the other 15 features are
rated. The framing is descriptive, not diagnostic. Honor that in
your conversations with students.

---

## Sample prompts for student reflection

After running a comparison, ask the student to write a short
reflection answering some of these:

1. Which features matched between your two samples? Are those the
   features you would have predicted?
2. Which features diverged? What in the genre, audience, or
   purpose of each text might explain the divergence?
3. What in your sentence-length distribution and standard
   deviation do you notice across the two samples? Is the
   rhythm consistent, or does it shift?
4. Look at the habitual words and phrases the tool flagged.
   Which of them are choices you'd want to keep? Which feel
   like tics to address in revision?
5. Compare the topic-sentence positions across your paragraphs.
   What pattern emerges? What pattern would you want your
   academic writing to have?
6. If the AI-writing-signs section flagged any markers, look at
   the specific words or phrases. Were they ones you reached
   for deliberately, or are they places where the writing
   defaulted to a register you weren't aiming for?

These prompts work even — perhaps especially — when AI use isn't
in question. The reflection is about owning the stylistic
decisions, not about defending against suspicion.

---

## A note on tone

Conversations about voice, especially ones triggered by suspected
AI assistance, are easy to make adversarial and almost never
productive when they are. The tool was built to support
conversations that are about writing, not about catching.

The framing in your office hours matters more than the numbers in
the report. If a student walks out of the conversation feeling
caught, the tool has not served the purpose. If they walk out
thinking differently about their own choices on the page, it has.
