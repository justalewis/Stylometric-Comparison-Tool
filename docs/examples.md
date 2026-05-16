# Worked Examples

Two end-to-end comparisons, with real numbers from the tool. The
first compares a formal academic register against an informal student
register — a baseline for what the tool surfaces when two human-
written texts diverge for ordinary reasons (genre, audience, voice).
The second adds an AI-flavored sample to show what the AI-writing-
signs section does when it has something to detect.

Both examples use short samples (140–200 words) for readability. Real
analyses are stronger with 400–1000-word samples.

---

## Example 1: Formal vs. informal human prose

### Text A — formal academic prose (198 words)

> The increasing prevalence of artificial intelligence in higher
> education necessitates a careful examination of its pedagogical
> implications. Universities must articulate clear policies that
> delineate appropriate use, lest the technology proliferate without
> sufficient oversight. While some institutions have endeavored to
> implement comprehensive frameworks, others remain in preliminary
> stages of policy development. Consequently, students often navigate
> ambiguous terrain, uncertain whether their use of generative tools
> constitutes legitimate scholarship or academic dishonesty.
>
> The methodological challenges are substantial. Faculty must
> reconceptualize assessment practices that have long presumed the
> absence of computational assistance. Furthermore, the credibility
> of student work becomes contingent upon transparent disclosure of
> AI involvement, a practice that requires new conventions of
> citation and acknowledgment. It could be argued that such
> conventions are still in formation, and that the academy has not
> yet reached consensus regarding their proper articulation.
>
> Nevertheless, certain principles appear to be emerging. Disclosure,
> transparency, and reflective use seem to constitute the foundations
> of an ethical framework. Instructors who facilitate student
> engagement with these tools, rather than prohibit their use
> entirely, may cultivate more sophisticated digital literacy.
> Ultimately, the trajectory of AI in higher education will depend
> not on prohibition but on the cultivation of judicious, informed
> practice.

### Text B — informal student register (164 words)

> I think AI is honestly kind of a mixed bag in school. Like,
> basically everyone is using it, but nobody really wants to talk
> about it. Teachers are stuck in this weird spot where they kind of
> know what is going on, but they do not really know how to deal with
> it. And honestly, I get it.
>
> You might wonder if students are just cheating with this stuff.
> Sometimes yeah, probably. But a lot of the time, it is just people
> trying to figure out how to write a sentence that does not sound
> terrible. I mean, I have used it a lot for that.
>
> Now I want to talk about what I think we should do. First, I think
> teachers should just be upfront and ask students what they used.
> Second, I think students should learn how to use these tools well,
> not just be told to avoid them. Because at the end of the day, this
> stuff is not going away.

### What the tool reports

**Tallies:** 6 Strong Match · 2 Partial Match · 7 No Match · 0
Indeterminate

| Feature | Text A | Text B | Rating |
|---|---|---|---|
| 1.1 Type-Token Ratio | 0.753 (149/198) | 0.567 (93/164) | No Match |
| 1.2 Latinate/Germanic | 0.73 (Latinate) | 0.00 (Germanic) | No Match |
| 1.3 Pet Words & Phrases | conventions, disclosure, in higher education | a lot, going, honestly, i think, kind of | No Match |
| 1.4 Hedges/Fillers/Intensifiers | informal 0/500w, formal 2.5/500w (formal) | informal 54.9/500w, formal 0/500w (informal) | No Match |
| 2.1 Sentence Length | mean 16.5, SD 5.93 | mean 13.67, SD 6.93 | Strong Match |
| 2.2 Sentence Openers | noun_subject 41.7%, then transitional 25.0% | pronoun_subject 25.0%, then adverbial 25.0% | No Match |
| 2.3 Coordination/Subordination | high subordination (10.0) | high subordination (2.67) | Strong Match |
| 2.4 Punctuation | commas 35/500w | commas 33/500w | Strong Match |
| 3.1 Paragraph Structure | 3 pgs, mean 4 sents, topic: first | 3 pgs, mean 4 sents, topic: first | Strong Match |
| 3.2 Transitions | hybrid | hybrid | Strong Match |
| 3.3 Evidence/Claim | claim_then_elaboration | claim_then_elaboration | Strong Match |
| 3.4 Metadiscourse | textual 0/500w, interpersonal 0/500w | textual 3/500w, interpersonal 15/500w | No Match |
| 4.1 Register | formal | semi-formal | Partial Match |
| 4.2 Register Consistency | consistent | shifts at pg 1, 2 | No Match |
| 4.3 Pronoun Profile | third: 12.6/500w | third: 30.5/500w | Partial Match |

**Total AI-writing-signs markers:** Text A: 0. Text B: 0.

### What this tells you

The two texts agree on six things and diverge on nine. The
convergences are interesting:

- **Sentence length and rhythm match.** Both writers average ~14-16
  words per sentence with standard deviations near 6. The rhythms
  are the same.
- **Both lean heavily on subordination.** Text A's ratio is more
  extreme (10:1 versus 2.67:1), but both are clearly above
  "balanced." Both writers like to embed clauses.
- **Punctuation rates are nearly identical.** Both use commas heavily
  and almost nothing else.
- **Paragraph structure matches.** Three paragraphs each, ~4
  sentences each, topic sentence first.
- **Evidence-to-claim pattern matches.** Both develop their points
  through reasoning rather than citing external sources.

The divergences are where you'd expect them:

- **Vocabulary streams are opposite.** Text A is 73% Latinate
  (`utilize`, `delineate`, `proliferate`, `endeavor`, `constitute`,
  `articulate`). Text B is entirely Germanic in its categorized
  words (`think`, `going`, `kind`, `know`, `talk`, `use`, `tell`,
  `like`, `get`).
- **Hedge profiles are mirror images.** Text A's hedges are formal
  (`it could be argued`); Text B's are informal (`kind of`,
  `basically`, `honestly`, `just`, `really`).
- **Sentence openers diverge.** Text A starts most sentences with
  noun phrases or transitional connectors; Text B starts with
  pronouns and adverbials.
- **Text B has frequent metadiscourse** (`I think`, `I want to talk
  about`, `you might wonder`); Text A has none.
- **Pronoun profiles differ.** Text B's `I`-count is roughly triple
  Text A's third-person-it count, normalized.
- **Text B's register shifts** within itself (the first paragraph is
  more informal than the third, which moves toward exhortation).

### Interpretation

These two texts are clearly written for different audiences and in
different registers. A reader doesn't need a tool to see that. What
the tool gives you is a structured inventory: this is a text that
holds its register stable, leans Latinate, prefers noun-subject
openings, and uses no first or second person. *That* is the contour
of the formal academic register Text A inhabits. Text B inhabits a
different contour and the tool names every dimension on which they
differ.

For a teaching context, the conversation isn't "which is better."
The conversation is: which of these contours do you want your
academic writing to inhabit, and which patterns from your informal
register are worth bringing across?

---

## Example 2: AI-flavored prose

To see what the AI-writing-signs section detects, here's a sample
crafted to exhibit the eight signs explicitly:

> The vibrant tapestry of artificial intelligence stands as a
> testament to human ingenuity, underscoring its pivotal role in
> shaping the evolving landscape of modern education. Nestled in the
> heart of contemporary scholarly discourse, this technology boasts a
> diverse array of applications, fostering meaningful engagement
> across institutions, disciplines, and communities. Industry reports
> and leading experts have noted its enduring impact, highlighting
> the importance of thoughtful implementation. It is not just a tool,
> but a transformative force. Several sources suggest that the
> technology contributes to the renowned commitment to excellence
> found in groundbreaking research, exemplifying a deep dedication to
> innovation. Despite its many challenges, the future outlook remains
> promising. The intricate interplay between policy, pedagogy, and
> practice underscores the crucial need for meticulous evaluation,
> ensuring that students, faculty, and administrators all benefit.
> Looking ahead, this evolving landscape will continue to shape
> educational futures.

### What the AI-signs section reports

141 words. **50 total markers · 177 per 500w.**

| Metric | Count | Per 500w | Notable hits |
|---|---|---|---|
| AI vocabulary | 22 | 78.0 | `vibrant`, `pivotal`, `landscape`, `enduring`, `underscores`, `intricate`, `meticulous`, `interplay` |
| Promotional phrasing | 8 | 28.4 | `boasts a`, `in the heart of`, `nestled in`, `diverse array` |
| Significance emphasis | 6 | 21.3 | `evolving landscape` (2×), `stands as a testament`, `testament to`, `pivotal role` |
| Vague attribution | 4 | 14.2 | `industry reports`, `experts have noted`, `several sources`, `leading experts` |
| Negative parallelisms | 1 | 3.6 | *"It is not just a tool, but a transformative force"* |
| Participial pseudo-analysis | 3 | 10.6 | starters: `underscoring`, `highlighting`, `exemplifying` |
| Rule of three | 3 | 10.6 | `institutions / disciplines / communities`, `policy / pedagogy / practice`, `students / faculty / administrators` |
| Conclusion formulas | 3 | 10.6 | `despite its`, `future outlook`, `looking ahead` |

### What this tells you

Every metric lights up. The text doesn't *necessarily* mean an AI
wrote it — a thoughtful human writer could produce these patterns
deliberately, and bad academic prose has produced them for decades —
but a 177-per-500-word total, with multiple metrics each above 10
per 500w, is a strong cluster. Compared against Text A from Example
1 (0 markers), the contrast is unmistakable.

The point of having the metrics broken out individually is that you
can see *which* patterns are present. A text might score high on
"significance emphasis" because the writer genuinely is making
significance claims about a subject that warrants them; that's not
the same situation as a text that scores high across all eight
metrics simultaneously. The Wikipedia source page is explicit on
this: clusters at high rates across multiple metrics are the
diagnostic signal, not any single hit.

---

## How to read the report yourself

Open the live tool at <https://stylometric-compare.fly.dev/> with
your credentials, paste either of the texts above (or your own), and
work through the report. Tooltips on dotted-underlined terms give
plain-language definitions. Each AI-signs metric has a `↗ wiki`
link to its source section. The Markdown export button at the top of
the report produces a self-contained file you can save or annotate.

For the framing the tool was built to support, see
[pedagogy.md](pedagogy.md). For the methodology behind each
measurement, see [methodology.md](methodology.md). For the
limitations and what the tool deliberately does not do, see
[limitations.md](limitations.md).
