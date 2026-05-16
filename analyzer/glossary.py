"""Plain-language definitions for every term the report exposes.

The Flask app passes this dict to templates as ``glossary``. The
template's ``gloss`` macro looks up a term and wraps the rendered text
in a span with a CSS-driven tooltip.

The same content is rendered as docs/glossary.md so the definitions
live in two places by design — the dict is for in-app tooltips, the
markdown file is for readable reference outside the tool.
"""

GLOSSARY: dict[str, str] = {

    # -- Preprocessing ------------------------------------------------------
    "Quoted material":
        "Direct quotations from sources. The tool removes them before analysis "
        "because they are the source author's choices, not the writer's. "
        "Double-quoted spans and indented or '>'-prefixed block quotes are "
        "stripped.",
    "Paragraph":
        "A block of prose separated from the next by a blank line. The tool "
        "uses blank-line-delimited paragraphs from the quote-stripped text.",
    "Sample size":
        "How many words remain after quoted material is removed. Below 250 "
        "words the tool warns that results may be unreliable; 400-1000 words "
        "is the ideal range.",

    # -- Section 1: Lexical -------------------------------------------------
    "TTR":
        "Type-token ratio. The number of distinct word forms (types) divided "
        "by the total number of word forms (tokens). Higher = more varied "
        "vocabulary; lower = more repetition.",
    "Type":
        "A distinct word form. 'The cat sat on the mat' has 6 tokens but 5 "
        "types because 'the' appears twice.",
    "Token":
        "A single word occurrence. Punctuation and numbers are not counted "
        "as tokens.",
    "Latinate":
        "Words derived from Latin or French roots (utilize, commence, "
        "facilitate). Tend to be formal, abstract, polysyllabic.",
    "Germanic":
        "Words derived from Old English or Old Norse (use, start, help). "
        "Tend to be concrete, shorter, everyday.",
    "Latinate/Germanic ratio":
        "Latinate hits divided by the total of Latinate plus Germanic hits. "
        "Higher than 0.60 = Latinate lean; lower than 0.40 = Germanic lean.",
    "Pet word":
        "A content word the writer reaches for repeatedly that the topic "
        "doesn't strictly require. With a topic hint, the tool separates "
        "these from words that are simply topical.",
    "Habitual phrase":
        "A 2-4 word phrase that recurs more than once and isn't a stock "
        "function-word combination. Examples: 'deal with it', 'at the end "
        "of the day'.",
    "Hedge":
        "A softener that qualifies a claim. Informal hedges (basically, "
        "kind of, pretty much) signal conversational register; formal "
        "hedges (perhaps, arguably, it could be argued) signal academic "
        "register.",
    "Filler":
        "A word that fills space without carrying meaning (just, really, "
        "actually, like, you know). Common in informal writing.",
    "Intensifier":
        "A booster that strengthens a claim (very, extremely, absolutely, "
        "literally, definitely). High intensifier rates signal emphatic, "
        "often informal register.",

    # -- Section 2: Syntactic -----------------------------------------------
    "Sentence length":
        "Number of word tokens per sentence. The mean and standard deviation "
        "together describe the writer's rhythm: high SD = mix of short and "
        "long; low SD = uniform length.",
    "Standard deviation":
        "A measure of spread. Low SD = sentences cluster around the mean; "
        "high SD = wide range from short to long.",
    "Sentence opener":
        "The first grammatical element of a sentence. The tool classifies "
        "openers into six categories: pronoun subject, noun subject, "
        "transitional connector, adverbial/prepositional, "
        "participial/gerund, or coordinating conjunction.",
    "Pronoun subject":
        "A sentence that starts with a personal or demonstrative pronoun "
        "acting as the subject: 'I think...', 'This means...', 'They "
        "argue...'.",
    "Noun subject":
        "A sentence that starts with a noun or noun phrase as the subject: "
        "'Universities are built...', 'The most immediate concern...'.",
    "Transitional connector":
        "A sentence-initial word or phrase that signals the logical "
        "relationship to what came before: 'However', 'Therefore', "
        "'Furthermore', 'On the other hand'.",
    "Adverbial opener":
        "A sentence that starts with an adverbial phrase, prepositional "
        "phrase, or subordinator: 'In this essay', 'As a result', "
        "'Even though'.",
    "Coordination":
        "Linking clauses with coordinating conjunctions (and, but, or, "
        "so, yet, nor). Produces additive, paratactic prose.",
    "Subordination":
        "Embedding one clause inside another with subordinators (because, "
        "although, while, if) or relative clauses. Produces complex, "
        "syntactically embedded prose.",
    "Subordinator":
        "A word that introduces a subordinate clause: because, although, "
        "though, while, when, if, since, after, before, unless, whereas.",
    "Relative clause":
        "A clause introduced by 'who', 'which', or 'that' that modifies a "
        "preceding noun: 'the writer who argued...', 'the book that I "
        "read...'.",
    "Comma splice":
        "Two independent clauses joined with only a comma, no conjunction: "
        "'I came, I saw, I conquered.' An error in formal writing, common "
        "in informal prose.",
    "Em dash":
        "A long dash used for parenthetical asides, abrupt shifts, or "
        "emphasis (the character '—'). Frequency varies enormously between "
        "writers; high em-dash use is a strong personal-style marker.",

    # -- Section 3: Discourse -----------------------------------------------
    "Topic sentence":
        "The sentence in a paragraph that states its main claim or topic. "
        "Position can be first, last, embedded (middle), or distributed "
        "across several sentences.",
    "Distributed topic":
        "A paragraph whose main claim is spread across multiple sentences "
        "rather than concentrated in one. The tool labels these as "
        "'distributed' when no single sentence dominates.",
    "Transition strategy":
        "How the writer links paragraphs to each other. Three patterns: "
        "explicit transitional connectors, metadiscursive narration "
        "('In this essay I will...'), or implicit logical connection.",
    "Metadiscursive narration":
        "Sentences where the writer announces the text's own structure: "
        "'Now I want to discuss...', 'Let me explain...', 'In this "
        "section...'.",
    "Evidence type":
        "What kind of supporting material the writer uses: peer-reviewed "
        "citations, direct quotations, anecdotes, hypothetical scenarios, "
        "rhetorical questions, or general reasoning.",
    "Interpretation marker":
        "A phrase that signals the writer is moving from evidence to "
        "claim: 'this shows', 'what this means', 'the implication is'.",
    "Metadiscourse":
        "Moments where the writer talks about the text or addresses the "
        "reader rather than the subject matter. Textual metadiscourse "
        "narrates the argument's structure; interpersonal metadiscourse "
        "directly addresses the reader or marks the writer's stance.",
    "Textual metadiscourse":
        "References to the text's own structure: 'In this essay I will', "
        "'As mentioned above', 'To summarize'.",
    "Interpersonal metadiscourse":
        "Direct address to the reader or positioning of the writer's "
        "stance: 'You might think', 'I believe', 'It is important to "
        "note'.",

    # -- Section 4: Register ------------------------------------------------
    "Register":
        "The formality level of the text. Four labels: formal (no first/"
        "second person, no contractions, Latinate vocabulary), semi-formal "
        "(first person OK, mostly Latinate), informal (first/second "
        "person, contractions, Germanic vocabulary, hedges), or mixed "
        "(features from multiple levels).",
    "Register consistency":
        "Whether the text holds the same register throughout, or shifts "
        "between paragraphs. Shifts are reported with paragraph index and "
        "direction (e.g., 'formal -> informal at paragraph 3').",
    "Pronoun profile":
        "The mix of first-singular, first-plural, second-person, and "
        "third-person pronouns. One of the most reliable register "
        "markers.",
    "First person singular":
        "I, me, my, mine, myself. Heavy use signals personal voice and "
        "informal register.",
    "Second person":
        "You, your, yours, yourself. Directly addresses the reader; rare "
        "in formal academic writing, common in advice or instructional "
        "prose.",
    "Expletive":
        "A grammatically required placeholder pronoun: 'It is important "
        "that...', 'There are many reasons'. The tool counts these "
        "separately so they don't inflate the third-person count.",

    # -- Section 5: Comparison ratings --------------------------------------
    "Strong Match":
        "The two texts behave the same way on this feature, within the "
        "spec's thresholds.",
    "Partial Match":
        "The texts agree on the dominant pattern but diverge on secondary "
        "measurements.",
    "No Match":
        "The texts behave differently on this feature.",
    "Indeterminate":
        "Not enough signal to decide — sample too short, no relevant "
        "tokens, length difference too large, or fewer than two "
        "paragraphs.",
    "Per 500 words":
        "A normalized rate that lets you compare counts across samples of "
        "different lengths. If a text has 8 hits in 1000 words, the "
        "per-500-word rate is 4.",

    # -- Section 6: AI-writing signs ----------------------------------------
    "AI-writing sign":
        "A stylistic pattern commonly observed in large-language-model "
        "output, catalogued on Wikipedia's 'Signs of AI writing' page. "
        "High rates are descriptive, not diagnostic — humans use these "
        "patterns too.",
    "AI vocabulary":
        "Words documented as statistically frequent in LLM output post-"
        "2022: delve, tapestry, underscore, pivotal, vibrant, meticulous, "
        "showcasing, intricate, fostering, highlighting, enhance, and "
        "others. The tool tracks three time-stratified lists.",
    "Promotional phrasing":
        "Travel-guide or press-release style: 'nestled in the heart of', "
        "'boasts a diverse array', 'renowned for', 'state-of-the-art'.",
    "Significance emphasis":
        "Generic statements connecting the subject to broader importance: "
        "'stands as a testament to', 'pivotal role in shaping', "
        "'underscores its importance', 'evolving landscape'.",
    "Vague attribution":
        "References to unnamed authorities: 'industry reports', 'experts "
        "argue', 'several sources', 'leading scholars suggest'.",
    "Negative parallelism":
        "Contrastive constructions that deny one thing and assert "
        "another: 'not just X but Y', 'not only X but also Y', 'it is "
        "not X, it is Y'.",
    "Participial tail":
        "A sentence ending in a comma + present-participle clause that "
        "makes an unattributed analytical claim: '...highlighting the "
        "importance of X', '...ensuring sustainability'.",
    "Rule of three":
        "Three parallel items in a list or series: 'X, Y, and Z'. Common "
        "in human writing too, but overused in LLM output for rhythmic "
        "effect.",
    "Conclusion formula":
        "Stock closing patterns: 'despite its challenges...', 'looking "
        "ahead', 'the future outlook is promising', 'in conclusion'.",
}
