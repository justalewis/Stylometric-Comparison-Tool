"""Curated word lists for stylometric markers.

Each list is a set of lowercased word forms or multiword phrases. Lists are
illustrative rather than exhaustive; they aim to catch high-frequency markers
in academic and student prose. Multiword phrases are matched as regex \b...\b
sequences in the analyzers.
"""

LATINATE = {
    "utilize", "utilization", "commence", "commencement", "facilitate",
    "facilitation", "subsequent", "subsequently", "demonstrate", "demonstration",
    "implement", "implementation", "exacerbate", "prohibit", "prohibition",
    "integrate", "integration", "compromise", "formulate", "formulation",
    "substitution", "substitute", "accessibility", "accessible", "credibility",
    "credible", "technological", "adaptability", "adapt", "prioritize",
    "preservation", "preserve", "ultimately", "increasingly", "furthermore",
    "consequently", "nevertheless", "substantial", "substantially",
    "acquisition", "acquire", "methodology", "methodological", "conceptualize",
    "concept", "conceptual", "necessitate", "necessary", "endeavor",
    "ascertain", "preliminary", "constitute", "encompass", "articulate",
    "articulation", "proliferation", "proliferate", "trajectory", "parameter",
    "paradigm", "paradigmatic", "implication", "implications", "infrastructure",
    "jurisdiction", "delineate", "delineation", "substantiate",
    "substantiation", "epistemology", "epistemological", "ontology",
    "discourse", "rhetoric", "rhetorical", "pedagogy", "pedagogical",
    "hegemony", "hegemonic", "ideology", "ideological", "manifestation",
    "manifest", "subjugate", "subjugation", "marginalize", "marginalization",
    "perpetuate", "perpetuation", "elucidate", "elucidation", "constitute",
    "constitution", "transmission", "transmit", "evaluate", "evaluation",
    "interrogate", "interrogation", "intervention", "intervene", "innovate",
    "innovation", "innovative", "consideration", "consider", "examine",
    "examination", "investigate", "investigation", "analysis", "analyze",
    "synthesis", "synthesize", "critique", "critical", "contemporary",
    "fundamental", "fundamentally", "significant", "significance",
    "significantly", "approximate", "approximately", "individual",
    "individuals", "particular", "particularly", "specific", "specifically",
    "essential", "essentially", "moreover", "however", "therefore", "thus",
    "additionally", "alternatively", "comparatively", "respectively",
    "establish", "establishment", "represent", "representation", "indicate",
    "indication", "construct", "construction", "produce", "production",
    "develop", "development", "process", "process", "structure", "structural",
    "function", "functional", "operate", "operation", "operational",
    "potential", "potentially", "probable", "probability", "possible",
    "possibility", "available", "availability", "appropriate", "inappropriate",
    "adequate", "inadequate", "sufficient", "insufficient",
}

GERMANIC = {
    "use", "used", "uses", "using", "start", "started", "begin", "began",
    "begun", "help", "helped", "next", "show", "showed", "shown", "set",
    "make", "made", "worse", "ban", "banned", "blend", "blended", "weaken",
    "weakened", "shape", "shaped", "swap", "swapped", "reach", "reached",
    "get", "got", "give", "gave", "given", "put", "look", "looked", "find",
    "found", "think", "thought", "need", "needed", "keep", "kept", "want",
    "wanted", "try", "tried", "take", "took", "taken", "bring", "brought",
    "build", "built", "work", "worked", "handle", "handled", "share",
    "shared", "grow", "grew", "grown", "rise", "rose", "risen", "fall",
    "fell", "fallen", "kind", "type", "way", "ways", "fair", "strong",
    "weak", "deep", "wide", "sharp", "hard", "soft", "good", "bad", "big",
    "small", "old", "new", "high", "low", "long", "short", "many", "much",
    "few", "little", "more", "less", "most", "least", "best", "worst",
    "easy", "tough", "tight", "loose", "fast", "slow", "early", "late",
    "right", "wrong", "true", "false", "near", "far", "open", "shut",
    "thing", "things", "stuff", "guy", "guys", "kid", "kids", "folk",
    "folks", "house", "home", "land", "land", "book", "word", "words",
    "talk", "talked", "tell", "told", "say", "said", "ask", "asked",
    "answer", "answered", "feel", "felt", "hear", "heard", "see", "saw",
    "seen", "watch", "watched", "read", "wrote", "written", "send", "sent",
    "leave", "left", "stay", "stayed", "stand", "stood", "sit", "sat",
    "walk", "walked", "run", "ran", "drive", "drove", "live", "lived",
    "die", "died", "love", "loved", "hate", "hated", "like", "liked",
    "play", "played", "win", "won", "lose", "lost", "buy", "bought",
    "sell", "sold", "pay", "paid", "cost", "spend", "spent", "save",
    "saved", "learn", "learned", "teach", "taught", "mean", "meant",
    "know", "knew", "known", "wish", "wished", "hope", "hoped",
}

# Multiword phrases are kept as regex-friendly strings (lowercase, single spaces).
INFORMAL_HEDGES_MULTI = [
    "pretty much", "kind of", "sort of", "a lot", "a bit", "a little",
    "i mean", "you know", "i guess", "or something", "or whatever",
    "more or less", "not really", "not so much", "in a way", "to be honest",
]

INFORMAL_HEDGES_SINGLE = {
    "basically", "just", "really", "actually", "honestly", "anyway",
    "anyways", "stuff", "things", "whatever", "like",
}

INTENSIFIERS_MULTI = [
    "a lot more", "way more", "much more",
]

INTENSIFIERS_SINGLE = {
    "very", "extremely", "absolutely", "totally", "completely", "literally",
    "definitely", "clearly", "obviously", "certainly", "truly", "incredibly",
    "remarkably", "significantly", "highly", "utterly", "thoroughly",
    "entirely", "wholly", "exceptionally", "particularly",
}

FORMAL_HEDGES_MULTI = [
    "to some extent", "to a certain extent", "it could be argued",
    "one might suggest", "it appears that", "it seems that",
    "it may be that", "in many cases", "in some cases", "for the most part",
    "by and large", "on the whole", "in general",
]

FORMAL_HEDGES_SINGLE = {
    "perhaps", "arguably", "potentially", "somewhat", "presumably",
    "ostensibly", "seemingly", "apparently",
}

# Conjunctive adverbs / explicit transitional connectors. Used both for
# sentence-opener detection and for paragraph-transition strategy.
TRANSITIONAL_CONNECTORS = {
    "however", "therefore", "thus", "hence", "furthermore", "moreover",
    "additionally", "consequently", "nevertheless", "nonetheless",
    "accordingly", "meanwhile", "subsequently", "similarly", "likewise",
    "conversely", "alternatively", "indeed", "instead", "otherwise",
    "finally", "lastly", "first", "second", "third", "next", "then",
}

TRANSITIONAL_PHRASES = [
    "on the other hand", "in addition", "in contrast", "by contrast",
    "for example", "for instance", "in particular", "in fact",
    "in conclusion", "in summary", "to summarize", "to conclude",
    "as a result", "as such", "that said", "that being said",
    "on the contrary", "in other words", "more importantly",
    "another concern is", "another issue is", "another point is",
    "another reason is", "another example is",
]

METADISCOURSE_TEXTUAL = [
    "in this essay", "in this paper", "in this article", "in this section",
    "in this chapter", "as mentioned above", "as noted above",
    "as discussed above", "as i mentioned", "as i noted", "as i discussed",
    "as i said", "the following section", "the next section",
    "in the next section", "the previous section", "in the previous section",
    "to summarize", "to recap", "in summary", "in conclusion",
    "to conclude", "let me explain", "let me clarify", "let me start by",
    "i want to discuss", "i will discuss", "i will argue", "i will show",
    "i will demonstrate", "what i am trying to say", "what i mean is",
    "basically what i am trying to say", "now we should talk about",
    "now i want to", "now let us", "now lets", "first i will",
    "next i will", "finally i will", "throughout this essay",
    "throughout this paper",
]

METADISCOURSE_INTERPERSONAL = [
    "you might think", "you may think", "you might wonder", "you may wonder",
    "you might ask", "you may ask", "you might say", "you may say",
    "i believe", "i think", "i argue", "i contend", "i suggest", "i claim",
    "i maintain", "in my view", "in my opinion", "from my perspective",
    "it is important to note", "it is worth noting", "it should be noted",
    "it is interesting to note", "one could argue", "one might argue",
    "one might suggest", "one could say", "it is important to remember",
    "keep in mind", "bear in mind", "consider this", "imagine if",
    "imagine that", "picture this",
]

# Subordinators used in subordination counting. Excludes "that" because it is
# heavily polysemous (demonstrative, complementizer, relativizer) and is
# better handled via spaCy dependency tags in the syntactic module.
SUBORDINATORS = {
    "because", "although", "though", "even though", "while", "whilst",
    "when", "whenever", "if", "unless", "since", "after", "before",
    "until", "till", "whereas", "wherever", "where", "as", "as if",
    "as though", "so that", "in order that", "provided that", "given that",
}

# Coordinating conjunctions (FANBOYS).
COORDINATORS = {"and", "but", "or", "so", "yet", "for", "nor"}

# Personal pronouns by category, used in pronoun-profile counting.
PRONOUNS_FIRST_SG = {"i", "me", "my", "mine", "myself"}
PRONOUNS_FIRST_PL = {"we", "us", "our", "ours", "ourselves"}
PRONOUNS_SECOND = {"you", "your", "yours", "yourself", "yourselves"}
PRONOUNS_THIRD = {
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "they", "them", "their", "theirs", "themselves", "themself",
    "it", "its", "itself",
}
PRONOUNS_IMPERSONAL_ONE = {"one", "ones", "oneself"}

# Closed-class function words used to filter pet-word candidates.
FUNCTION_WORDS = {
    "the", "a", "an", "and", "or", "but", "so", "yet", "for", "nor",
    "if", "as", "of", "in", "on", "at", "by", "to", "with", "from",
    "into", "onto", "over", "under", "out", "up", "down", "off",
    "about", "above", "below", "across", "after", "against", "along",
    "among", "around", "before", "behind", "between", "beyond",
    "during", "except", "inside", "outside", "near", "since",
    "through", "throughout", "toward", "towards", "until", "upon",
    "via", "within", "without",
    "be", "am", "is", "are", "was", "were", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing",
    "done", "will", "would", "shall", "should", "may", "might",
    "must", "can", "could", "ought",
    "this", "that", "these", "those", "such",
    "i", "me", "my", "mine", "myself", "we", "us", "our", "ours",
    "ourselves", "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "themself", "one", "ones", "oneself",
    "who", "whom", "whose", "which", "what", "where", "when",
    "why", "how", "whether",
    "not", "no", "nor", "neither", "either", "both", "all", "any",
    "some", "every", "each", "many", "much", "more", "most", "less",
    "least", "few", "several", "other", "another", "same",
    "very", "too", "also", "even", "only", "just", "still", "already",
    "again", "ever", "never", "always", "often", "sometimes",
    "there", "here", "now", "then",
}

# Interpretation / claim-marking verbs and phrases that signal the writer is
# moving from evidence to claim. Used by the discourse module.
INTERPRETATION_MARKERS = [
    "this shows", "this means", "this suggests", "this indicates",
    "this demonstrates", "this implies", "this reveals", "this highlights",
    "this points to", "this illustrates", "this proves", "this confirms",
    "this tells us", "shows that", "means that", "suggests that",
    "indicates that", "demonstrates that", "implies that", "reveals that",
    "in other words", "what this means", "the point is", "the upshot",
    "the takeaway", "the implication",
]


# ---------------------------------------------------------------------------
# AI-writing-signs lists. Sourced from
# https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
# (accessed 2026-05-16). These feed analyzer/aitext_signs.py.
# ---------------------------------------------------------------------------

# §"High density of AI vocabulary words" — three time-stratified lists
# documented on the Wikipedia page. We keep them separate so the report can
# show provenance ("this hit appears on the mid-2025+ list").

AI_VOCAB_2023_MID2024 = {
    "additionally", "boasts", "bolstered", "crucial", "delve",
    "emphasizing", "enduring", "garner", "intricate", "intricacies",
    "interplay", "key", "landscape", "meticulous", "meticulously",
    "pivotal", "underscore", "underscores", "underscored", "underscoring",
    "tapestry", "testament", "valuable", "vibrant",
}

AI_VOCAB_MID2024_MID2025 = {
    "bolstered", "crucial", "emphasizing", "enhance", "enhances",
    "enhanced", "enhancing", "enduring", "fostering", "highlighting",
    "highlights", "highlight", "pivotal", "showcasing", "showcase",
    "showcases", "underscore", "underscores", "underscored", "vibrant",
}

AI_VOCAB_MID2025_PLUS = {
    "emphasizing", "enhance", "enhances", "enhanced", "enhancing",
    "highlighting", "highlights", "highlight", "showcasing", "showcase",
    "showcases",
}

# "Align with" is a multi-word entry on the mid-2024 list; we match it
# separately as a phrase.
AI_VOCAB_PHRASES = ["align with", "aligns with", "aligned with", "aligning with"]


# §"Promotional and advertisement-like language"
AI_PROMOTIONAL_PHRASES = [
    "boasts a", "boasts an", "in the heart of", "nestled in",
    "nestled between", "natural beauty", "diverse array", "wide array",
    "rich tapestry", "rich array", "rich history", "rich tradition",
    "commitment to excellence", "deep commitment", "unwavering commitment",
    "renowned for", "groundbreaking", "state-of-the-art",
    "world-class", "cutting-edge", "deeply committed",
]

AI_PROMOTIONAL_SINGLES = {
    "vibrant", "renowned", "profound", "exemplifies", "showcases",
}


# §"Undue emphasis on significance, legacy, and broader trends"
AI_SIGNIFICANCE_PHRASES = [
    "stands as", "serves as", "stands as a testament", "is a testament",
    "testament to", "pivotal role", "crucial role", "key role",
    "vital role", "significant role", "central role", "important role",
    "underscores its importance", "underscores the importance",
    "highlights its importance", "highlights the importance",
    "highlights its significance", "underscores its significance",
    "reflects broader", "reflects a broader", "focal point",
    "indelible mark", "indelible impact", "deeply rooted",
    "key turning point", "evolving landscape", "shifting landscape",
    "setting the stage for", "marking a shift", "represents a shift",
    "shaping the future", "shaping the landscape", "ongoing legacy",
    "enduring legacy", "lasting impact", "contributing to the",
    "in the broader context", "in the larger context",
]


# §"Vague attributions and overgeneralization of opinions"
AI_VAGUE_ATTRIBUTION_PHRASES = [
    "industry reports", "industry experts", "observers have cited",
    "observers have noted", "experts argue", "experts say",
    "experts believe", "experts have noted", "experts contend",
    "critics argue", "critics have noted", "some critics argue",
    "some scholars argue", "several sources", "several publications",
    "several outlets", "many sources", "various sources",
    "various publications", "various outlets", "multiple sources",
    "leading experts", "leading scholars", "scholars have argued",
    "scholars argue", "scholars suggest", "researchers have shown",
    "studies have shown", "studies suggest", "studies indicate",
    "research suggests", "research shows", "research indicates",
]


# §"Outline-like conclusions about challenges and future prospects"
AI_CONCLUSION_PHRASES = [
    "despite its", "despite these challenges", "despite the challenges",
    "challenges and legacy", "future outlook", "looking ahead",
    "moving forward", "as we look to the future", "in conclusion",
    "to conclude", "in summary", "to summarize", "in the years to come",
    "in the coming years", "in the future", "the future holds",
    "going forward", "as we move forward", "navigating these challenges",
    "faces several challenges", "faces many challenges",
    "faces numerous challenges", "remain to be seen",
]


# §"Avoidance of basic copulatives" — verbs that LLMs reach for instead of
# "is/are". We don't penalize these — we just count them and report them
# alongside the is/are rate so the analyst can see the substitution pattern.
AI_COPULA_SUBSTITUTES = {
    "serves", "stands", "marks", "represents", "embodies",
    "exemplifies", "constitutes", "epitomizes", "encompasses",
    "personifies", "signifies", "denotes",
}


# §"Superficial analyses" — sentences ending in a participial -ing clause
# making unattributed claims. We detect these heuristically; this list
# captures the common starters.
AI_PARTICIPIAL_STARTERS = {
    "highlighting", "underscoring", "emphasizing", "ensuring",
    "reflecting", "symbolizing", "contributing", "cultivating",
    "fostering", "encompassing", "showcasing", "demonstrating",
    "illustrating", "providing", "offering", "enabling",
    "facilitating", "promoting", "shaping", "marking", "creating",
    "establishing", "delivering", "yielding",
}
