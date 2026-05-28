"""Deep scan: extended AI-writing-signs analysis, localhost-only.

Implements 18 additional stylistic markers drawn from Wikipedia's
*Signs of AI writing* catalog beyond the eight already exposed in
``aitext_signs.py``. Together with those eight, the deep-scan view
runs 26 metrics against a single text.

  Wikipedia source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing

Each metric returns a uniform dict::

    {
        "key": str,
        "name": str,
        "wikipedia_section": str (URL),
        "description": str,
        "raw_count": int,
        "per_500": float,
        "top_hits": list[(term, count)],
        "examples": list[dict],
        "details": dict,
        "notes": str,
    }

The deep-scan analyzer also surfaces an overall ``density`` classification
(low / moderate / high / very_high) based on total markers per 500 words.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter

from spacy.tokens import Doc

from . import aitext_signs
from .aitext_signs import _per_500
from .pipeline import load_nlp
from .preprocess import split_paragraphs, strip_quotes


WIKI = "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing"


# ============================================================
# Curated markers used by the new metrics
# ============================================================

# #9 Copula avoidance — marketing verbs that replace "is/are"
COPULAR_REPLACEMENTS = [
    "serves as", "marks", "features", "offers", "maintains", "boasts",
    "represents", "constitutes", "embodies", "exemplifies", "encompasses",
    "comprises", "denotes", "signifies", "designates", "stands as",
    "functions as", "operates as", "acts as",
]

# #13 Active social-media phrasing
SOCIAL_MEDIA_PHRASES = [
    "maintains an active social media presence",
    "active social media presence", "strong digital presence",
    "actively shares", "regularly posts", "growing online following",
    "vibrant online community", "robust online presence",
    "active on instagram", "active on twitter", "active on tiktok",
    "actively engages", "engages with followers",
]

# #14 Claimed debate generation
DEBATE_CLAIM_PHRASES = [
    "has generated debate about", "prompted discussion of",
    "sparked debate over", "sparked controversy", "ignited controversy",
    "fueled discussion", "raised questions about", "raised concerns about",
    "has sparked", "prompted debate", "generated controversy",
    "sparked discussion", "ignited debate", "fueled debate",
]

# #15 Heritage / cultural significance puffery
HERITAGE_PHRASES = [
    "rich cultural heritage", "rich heritage", "preserving traditions",
    "embedded in the fabric of", "steeped in history",
    "deep-rooted tradition", "time-honored", "longstanding tradition",
    "cultural tapestry", "rich tradition", "centuries-old",
    "deeply ingrained", "woven into the fabric",
]

# #16 Notability / media-attribution puffery
NOTABILITY_PHRASES = [
    "independent coverage", "profiled in", "written by a leading expert",
    "featured in", "regional media", "national media outlets",
    "local and national publications", "local media", "garnered attention",
    "received widespread coverage", "covered extensively",
    "leading publications", "renowned for",
]

# #17 Knowledge-cutoff disclaimers
KNOWLEDGE_CUTOFF_PHRASES = [
    "as of my last update", "as of my knowledge cutoff",
    "my training data only goes up to", "i don't have information about events after",
    "i do not have information about events after",
    "as of my last knowledge update", "based on information available",
    "i don't have access to real-time", "i do not have access to real-time",
    "i am unable to verify", "i cannot confirm",
    "as an ai language model", "as an ai assistant",
    "i'm an ai", "i am an ai",
]

# #18 Placeholder / template leftovers
PLACEHOLDER_PATTERNS = [
    r"\[insert [^\]]+\]",
    r"\[your [^\]]+\]",
    r"\[placeholder[^\]]*\]",
    r"\[name [^\]]+\]",
    r"\[edit [^\]]+\]",
    r"\bTBD\b",
    r"\bTBA\b",
    r"\bTKTK\b",
    r"\blorem ipsum\b",
    r"expand on this",
    r"more information needed",
    r"\[fill in [^\]]+\]",
]

# #23 Elegant variation — synonym clusters
SYNONYM_CLUSTERS = {
    "importance": {
        "important", "crucial", "vital", "pivotal", "significant",
        "key", "essential", "critical", "central", "fundamental",
    },
    "demonstrate": {
        "show", "demonstrate", "illustrate", "reveal", "exemplify",
        "manifest", "indicate", "highlight", "underscore",
    },
    "use": {
        "use", "utilize", "employ", "leverage", "harness", "deploy",
        "implement",
    },
    "foster": {
        "foster", "cultivate", "nurture", "encourage", "promote",
        "advance", "facilitate",
    },
    "enhance": {
        "enhance", "improve", "boost", "amplify", "augment", "elevate",
        "strengthen",
    },
    "discuss": {
        "discuss", "examine", "explore", "address", "consider",
        "investigate", "interrogate", "analyze",
    },
    "create": {
        "create", "generate", "produce", "develop", "construct",
        "establish", "forge",
    },
    "complex": {
        "complex", "intricate", "elaborate", "sophisticated", "nuanced",
        "multifaceted",
    },
    "beautiful": {
        "beautiful", "stunning", "breathtaking", "magnificent",
        "captivating", "exquisite", "picturesque",
    },
}

# Pattern for emoji as formatting (basic emoji ranges)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F5FF"   # symbols & pictographs
    "\U0001F600-\U0001F64F"   # emoticons
    "\U0001F680-\U0001F6FF"   # transport & map symbols
    "\U0001F700-\U0001F77F"   # alchemical
    "\U0001F900-\U0001F9FF"   # supplemental symbols
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "☀-⛿"           # misc symbols
    "✀-➿"            # dingbats
    "]"
)


# ============================================================
# Helpers
# ============================================================

def _find_sentence_containing(doc: Doc, needle: str) -> str:
    needle_lower = needle.lower()
    for sent in doc.sents:
        if needle_lower in sent.text.lower():
            return sent.text.strip()
    return ""


def _count_regex(text_lower: str, pattern: str, flags: int = 0) -> int:
    return len(re.findall(pattern, text_lower, flags))


def _count_phrases_lower(text_lower: str, phrases: list[str]) -> Counter:
    counter: Counter = Counter()
    for phrase in phrases:
        c = len(re.findall(r"\b" + re.escape(phrase) + r"\b", text_lower))
        if c:
            counter[phrase] = c
    return counter


def _first_sentence(para_text: str) -> str:
    """Cheap first-sentence extraction from a paragraph string."""
    m = re.match(r"\s*(.+?[.!?])(?:\s|$)", para_text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return para_text.strip()


# ============================================================
# TIER 2 METRICS
# ============================================================

# #9 Copula avoidance ----------------------------------------------------

def _metric_copula_avoidance(doc: Doc, text_lower: str, n_words: int) -> dict:
    copulas = {"is", "are", "was", "were", "be", "am", "being", "been"}
    copula_count = sum(1 for t in doc if t.is_alpha and t.lower_ in copulas)
    replacements = _count_phrases_lower(text_lower, COPULAR_REPLACEMENTS)
    replacement_total = sum(replacements.values())
    total = copula_count + replacement_total
    avoidance_ratio = (
        round(replacement_total / total, 3) if total else 0.0
    )
    examples = []
    for term, _ in replacements.most_common(2):
        s = _find_sentence_containing(doc, term)
        if s:
            examples.append({"sentence": s[:200], "term": term})
    return {
        "key": "copula_avoidance",
        "name": "Copula avoidance",
        "wikipedia_section": WIKI + "#Avoidance_of_basic_copulatives",
        "description": (
            "LLMs replace 'is/are' with marketing-verb alternatives like "
            "'serves as', 'features', 'maintains', 'boasts'."
        ),
        "raw_count": replacement_total,
        "per_500": _per_500(replacement_total, n_words),
        "top_hits": replacements.most_common(8),
        "examples": examples,
        "details": {
            "copula_count": copula_count,
            "replacement_count": replacement_total,
            "avoidance_ratio": avoidance_ratio,
        },
        "notes": (
            f"Replacement ratio {avoidance_ratio} (replacement_verbs / "
            f"(replacement_verbs + copulas))."
        ),
    }


# #10 'Refers to' lead --------------------------------------------------

def _metric_refers_to_lead(paragraphs: list[str], n_words: int) -> dict:
    matches = []
    for i, para in enumerate(paragraphs):
        first = _first_sentence(para)
        if re.search(r"\brefers to\b", first, re.IGNORECASE):
            matches.append({"paragraph": i + 1, "sentence": first[:200]})
    return {
        "key": "refers_to_lead",
        "name": "'Refers to' lead",
        "wikipedia_section": WIKI + "#Avoidance_of_basic_copulatives",
        "description": (
            "Opening sentences that define a topic via 'refers to …' instead "
            "of 'is …', as if the article is about the term rather than the "
            "subject itself."
        ),
        "raw_count": len(matches),
        "per_500": _per_500(len(matches), n_words),
        "top_hits": [],
        "examples": matches[:3],
        "details": {},
        "notes": "",
    }


# #11 Em-dash overuse ---------------------------------------------------

def _metric_em_dash_overuse(text: str, n_words: int) -> dict:
    count = text.count("—") + len(re.findall(r"(?<=\w) -- (?=\w)", text))
    rate = _per_500(count, n_words)
    threshold_flag = rate >= 8.0
    return {
        "key": "em_dash_overuse",
        "name": "Em-dash overuse",
        "wikipedia_section": WIKI + "#Overuse_of_em_dashes",
        "description": (
            "Em dashes used as a stylistic crutch beyond standard density "
            "for formal prose."
        ),
        "raw_count": count,
        "per_500": rate,
        "top_hits": [],
        "examples": [],
        "details": {
            "threshold_flagged": threshold_flag,
            "threshold_per_500": 8.0,
        },
        "notes": "Flagged when rate ≥ 8 per 500 words." if threshold_flag else "",
    }


# #12 Curly quotation marks --------------------------------------------

def _metric_curly_quotes(text: str, n_words: int) -> dict:
    curly = sum(text.count(c) for c in ("“", "”", "‘", "’"))
    straight = text.count('"') + text.count("'")
    total = curly + straight
    curly_share = round(curly / total, 3) if total else 0.0
    return {
        "key": "curly_quotes",
        "name": "Curly quotation marks",
        "wikipedia_section": WIKI + "#Curly_quotation_marks_and_apostrophes",
        "description": (
            "Use of curly/smart quotes (“ ” ‘ ’) "
            "where straight quotes would be expected — common copy-paste "
            "artifact from LLM output and word processors."
        ),
        "raw_count": curly,
        "per_500": _per_500(curly, n_words),
        "top_hits": [],
        "examples": [],
        "details": {
            "curly_count": curly,
            "straight_count": straight,
            "curly_share": curly_share,
        },
        "notes": "",
    }


# #13 Active social-media phrasing -------------------------------------

def _metric_social_media(doc: Doc, text_lower: str, n_words: int) -> dict:
    hits = _count_phrases_lower(text_lower, SOCIAL_MEDIA_PHRASES)
    total = sum(hits.values())
    examples = []
    for term, _ in hits.most_common(2):
        s = _find_sentence_containing(doc, term)
        if s:
            examples.append({"sentence": s[:200], "term": term})
    return {
        "key": "social_media_phrasing",
        "name": "Social-media presence phrasing",
        "wikipedia_section": WIKI + "#Active_social_media_presence_phrasing",
        "description": (
            "Idiosyncratic AI phrasing about an entity's social media activity "
            "('maintains an active social media presence', 'actively shares')."
        ),
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": hits.most_common(6),
        "examples": examples,
        "details": {},
        "notes": "",
    }


# #14 Claimed debate generation ----------------------------------------

def _metric_debate_claim(doc: Doc, text_lower: str, n_words: int) -> dict:
    hits = _count_phrases_lower(text_lower, DEBATE_CLAIM_PHRASES)
    total = sum(hits.values())
    examples = []
    for term, _ in hits.most_common(2):
        s = _find_sentence_containing(doc, term)
        if s:
            examples.append({"sentence": s[:200], "term": term})
    return {
        "key": "debate_claim",
        "name": "Claimed debate generation",
        "wikipedia_section": WIKI + "#Superficial_analyses",
        "description": (
            "Unsubstantiated claims that a topic 'has generated debate' or "
            "'sparked controversy' without naming the parties involved."
        ),
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": hits.most_common(6),
        "examples": examples,
        "details": {},
        "notes": "",
    }


# #15 Heritage / cultural significance ---------------------------------

def _metric_heritage(doc: Doc, text_lower: str, n_words: int) -> dict:
    hits = _count_phrases_lower(text_lower, HERITAGE_PHRASES)
    total = sum(hits.values())
    examples = []
    for term, _ in hits.most_common(2):
        s = _find_sentence_containing(doc, term)
        if s:
            examples.append({"sentence": s[:200], "term": term})
    return {
        "key": "heritage_puffery",
        "name": "Heritage / cultural-significance puffery",
        "wikipedia_section": WIKI + "#Promotional_and_advertisement-like_language",
        "description": (
            "Stock phrases asserting cultural depth or historical weight "
            "('rich cultural heritage', 'steeped in history', 'time-honored')."
        ),
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": hits.most_common(6),
        "examples": examples,
        "details": {},
        "notes": "",
    }


# #16 Notability / media-attribution -----------------------------------

def _metric_notability(doc: Doc, text_lower: str, n_words: int) -> dict:
    hits = _count_phrases_lower(text_lower, NOTABILITY_PHRASES)
    total = sum(hits.values())
    examples = []
    for term, _ in hits.most_common(2):
        s = _find_sentence_containing(doc, term)
        if s:
            examples.append({"sentence": s[:200], "term": term})
    return {
        "key": "notability_puffery",
        "name": "Notability / media-attribution puffery",
        "wikipedia_section": WIKI + "#Canned_emphasis_on_notability,_attribution,_and_media_coverage",
        "description": (
            "Inflated coverage claims and stock attribution phrases "
            "('independent coverage', 'profiled in', 'featured in')."
        ),
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": hits.most_common(6),
        "examples": examples,
        "details": {},
        "notes": "",
    }


# #17 Knowledge-cutoff disclaimers -------------------------------------

def _metric_knowledge_cutoff(doc: Doc, text_lower: str, n_words: int) -> dict:
    hits = _count_phrases_lower(text_lower, KNOWLEDGE_CUTOFF_PHRASES)
    total = sum(hits.values())
    examples = []
    for term, _ in hits.most_common(2):
        s = _find_sentence_containing(doc, term)
        if s:
            examples.append({"sentence": s[:200], "term": term})
    return {
        "key": "knowledge_cutoff",
        "name": "Knowledge-cutoff disclaimers",
        "wikipedia_section": WIKI + "#Communication_intended_for_the_user",
        "description": (
            "Direct LLM self-reference: training-cutoff disclaimers, 'as an "
            "AI language model' framings. Any presence is diagnostic of "
            "unedited model output."
        ),
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": hits.most_common(6),
        "examples": examples,
        "details": {},
        "notes": "Any non-zero count strongly suggests unedited AI output.",
    }


# #18 Placeholder / template leftovers ---------------------------------

def _metric_placeholders(text: str, n_words: int) -> dict:
    matches: list[str] = []
    for pat in PLACEHOLDER_PATTERNS:
        for m in re.finditer(pat, text, flags=re.IGNORECASE):
            matches.append(m.group(0))
    count = len(matches)
    return {
        "key": "placeholders",
        "name": "Placeholder / template leftovers",
        "wikipedia_section": WIKI + "#Phrasal_templates_and_placeholder_text",
        "description": (
            "Unfilled template markers like '[insert X]', 'TBD', 'TKTK', "
            "'lorem ipsum' — signs of unedited LLM output."
        ),
        "raw_count": count,
        "per_500": _per_500(count, n_words),
        "top_hits": Counter(matches).most_common(6),
        "examples": [{"term": m} for m in matches[:5]],
        "details": {},
        "notes": "Any non-zero count strongly suggests unedited drafts.",
    }


# #19 Title-case markdown headings -------------------------------------

def _metric_title_case_headings(raw_text: str, n_words: int) -> dict:
    heading_lines = re.findall(r"^(#{1,6})\s+(.+)$", raw_text, flags=re.MULTILINE)
    title_case_headings = []
    for _, heading_text in heading_lines:
        words = [w for w in re.findall(r"\b[A-Za-z][A-Za-z']*\b", heading_text) if w]
        if len(words) < 2:
            continue
        # Skip 1st/last (always capitalized in title case anyway); count interior words.
        interior = words[1:-1] if len(words) >= 3 else []
        capital_count = sum(1 for w in interior if w[0].isupper())
        # Title-case = most interior content words capitalized
        if interior and capital_count / len(interior) >= 0.6:
            title_case_headings.append(heading_text.strip()[:120])
    return {
        "key": "title_case_headings",
        "name": "Title-case markdown headings",
        "wikipedia_section": WIKI + "#Title_case_in_section_headings",
        "description": (
            "Markdown headings written in Title Case (e.g., 'Impact Of "
            "Technology And Digitalization'), against the prose convention "
            "of sentence case."
        ),
        "raw_count": len(title_case_headings),
        "per_500": _per_500(len(title_case_headings), n_words),
        "top_hits": [],
        "examples": [{"sentence": h} for h in title_case_headings[:5]],
        "details": {
            "total_headings": len(heading_lines),
            "title_case_headings": len(title_case_headings),
        },
        "notes": "",
    }


# #20 Excessive markdown bold -------------------------------------------

def _metric_markdown_bold(raw_text: str, n_words: int) -> dict:
    bold_matches = re.findall(r"\*\*([^*\n]{1,80})\*\*", raw_text)
    bold_matches += re.findall(r"__([^_\n]{1,80})__", raw_text)
    count = len(bold_matches)
    rate = _per_500(count, n_words)
    threshold_flag = rate >= 10.0
    return {
        "key": "markdown_bold_density",
        "name": "Excessive markdown bold",
        "wikipedia_section": WIKI + "#Overuse_of_boldface",
        "description": (
            "Mechanical heavy use of **bold** markdown to mark key terms, "
            "characteristic of listicle and readme-style LLM output."
        ),
        "raw_count": count,
        "per_500": rate,
        "top_hits": Counter(bold_matches).most_common(8),
        "examples": [],
        "details": {"threshold_per_500": 10.0, "threshold_flagged": threshold_flag},
        "notes": "Flagged when rate ≥ 10 per 500 words." if threshold_flag else "",
    }


# #21 Inline-header vertical lists -------------------------------------

def _metric_inline_header_lists(raw_text: str, n_words: int) -> dict:
    # Bullet line, then **Header**: prose
    pat = re.compile(
        r"^[\s]*[•\-\*–—]\s*\*\*([^*\n]+)\*\*\s*[:—\-]",
        re.MULTILINE,
    )
    # Also: numbered "1. **Header**: prose"
    pat2 = re.compile(
        r"^[\s]*\d+\.\s*\*\*([^*\n]+)\*\*\s*[:—\-]",
        re.MULTILINE,
    )
    headers = [m.group(1).strip() for m in pat.finditer(raw_text)]
    headers += [m.group(1).strip() for m in pat2.finditer(raw_text)]
    return {
        "key": "inline_header_lists",
        "name": "Inline-header vertical lists",
        "wikipedia_section": WIKI + "#Inline-header_vertical_lists",
        "description": (
            "List items shaped like '• **Header**: prose' — a signature "
            "LLM formatting move when asked for structured information."
        ),
        "raw_count": len(headers),
        "per_500": _per_500(len(headers), n_words),
        "top_hits": Counter(headers).most_common(6),
        "examples": [{"sentence": h} for h in headers[:5]],
        "details": {},
        "notes": "",
    }


# #22 Markdown formatting artifacts ------------------------------------

def _metric_markdown_artifacts(raw_text: str, n_words: int) -> dict:
    counts = {
        "headings": len(re.findall(r"^#{1,6}\s+", raw_text, flags=re.MULTILINE)),
        "bold_pairs": len(re.findall(r"\*\*[^*\n]+\*\*", raw_text)),
        "italic_pairs": len(re.findall(r"(?<!\*)\*[^*\n]{1,80}\*(?!\*)", raw_text)),
        "bullet_lines": len(re.findall(r"^\s*[-*+]\s+", raw_text, flags=re.MULTILINE)),
        "numbered_lines": len(re.findall(r"^\s*\d+\.\s+", raw_text, flags=re.MULTILINE)),
        "horizontal_rules": len(re.findall(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", raw_text, flags=re.MULTILINE)),
        "code_fences": len(re.findall(r"^```", raw_text, flags=re.MULTILINE)),
    }
    total = sum(counts.values())
    return {
        "key": "markdown_artifacts",
        "name": "Markdown formatting artifacts",
        "wikipedia_section": WIKI + "#Use_of_Markdown",
        "description": (
            "Presence of markdown syntax (#, **, *, bullets, numbered lists, "
            "horizontal rules, code fences) in text expected to be plain "
            "prose — a strong tell of pasted LLM output."
        ),
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": list(counts.items()),
        "examples": [],
        "details": counts,
        "notes": "",
    }


# ============================================================
# TIER 3 METRICS
# ============================================================

# #23 Elegant variation -------------------------------------------------

def _metric_elegant_variation(paragraph_docs: list[Doc], n_words: int) -> dict:
    """Per-paragraph: count distinct synonym-cluster members appearing.

    Flag paragraphs where 3+ distinct members of the same synonym cluster
    appear — characteristic LLM "elegant variation" to avoid repetition.
    """
    flagged_paragraphs: list[dict] = []
    cluster_totals: Counter = Counter()
    for i, p_doc in enumerate(paragraph_docs):
        tokens_in_para = {t.lower_ for t in p_doc if t.is_alpha}
        for cluster_name, members in SYNONYM_CLUSTERS.items():
            present = tokens_in_para & members
            if len(present) >= 3:
                flagged_paragraphs.append({
                    "paragraph": i + 1,
                    "cluster": cluster_name,
                    "members_present": sorted(present),
                })
                cluster_totals[cluster_name] += 1
    return {
        "key": "elegant_variation",
        "name": "Elegant variation (synonym cycling)",
        "wikipedia_section": WIKI + "#Lexical_diversity",
        "description": (
            "Paragraphs where the writer cycles through three or more "
            "near-synonyms for the same concept — characteristic of LLM "
            "repetition-penalty behavior. Approximate detection via a "
            "curated synonym-cluster list."
        ),
        "raw_count": len(flagged_paragraphs),
        "per_500": _per_500(len(flagged_paragraphs), n_words),
        "top_hits": cluster_totals.most_common(),
        "examples": flagged_paragraphs[:5],
        "details": {
            "clusters_tracked": len(SYNONYM_CLUSTERS),
            "flagged_paragraphs": len(flagged_paragraphs),
        },
        "notes": "Approximate detection — false positives possible on intentionally varied prose.",
    }


# #24 Pronounced style shift across paragraphs -------------------------

def _para_features(p_doc: Doc) -> dict:
    """Compact feature vector per paragraph for shift detection."""
    tokens = [t for t in p_doc if t.is_alpha]
    n = len(tokens) or 1
    types = {t.lower_ for t in tokens}
    sents = [s for s in p_doc.sents if any(t.is_alpha for t in s)]
    sent_lengths = [sum(1 for t in s if t.is_alpha) for s in sents]
    mean_sent = statistics.mean(sent_lengths) if sent_lengths else 0
    ttr = round(len(types) / n, 3)
    first_sg = sum(1 for t in tokens if t.lower_ in {"i", "me", "my", "mine", "myself"})
    contractions = len(re.findall(
        r"\b(?:don't|doesn't|didn't|won't|isn't|aren't|wasn't|weren't|"
        r"i'm|i've|i'll|it's|that's|there's|can't|couldn't|shouldn't)\b",
        p_doc.text, re.IGNORECASE,
    ))
    return {
        "n_words": n,
        "mean_sentence": round(mean_sent, 2),
        "ttr": ttr,
        "first_sg_per_500": round(first_sg / n * 500, 2),
        "contractions_per_500": round(contractions / n * 500, 2),
    }


def _metric_style_shift(paragraph_docs: list[Doc], n_words: int) -> dict:
    if len(paragraph_docs) < 2:
        return {
            "key": "style_shift",
            "name": "Pronounced style shift",
            "wikipedia_section": WIKI + "#Pronounced_shift_in_writing_style",
            "description": (
                "Adjacent paragraphs that diverge sharply on multiple "
                "stylistic dimensions simultaneously (sentence rhythm, "
                "lexical diversity, register markers)."
            ),
            "raw_count": 0,
            "per_500": 0.0,
            "top_hits": [],
            "examples": [],
            "details": {"note": "Fewer than 2 paragraphs; no shifts to detect."},
            "notes": "",
        }
    features = [_para_features(p) for p in paragraph_docs]
    shifts: list[dict] = []
    for i in range(1, len(features)):
        a, b = features[i - 1], features[i]
        if a["n_words"] < 30 or b["n_words"] < 30:
            continue
        sent_delta = abs(a["mean_sentence"] - b["mean_sentence"])
        ttr_delta = abs(a["ttr"] - b["ttr"])
        first_sg_delta = abs(a["first_sg_per_500"] - b["first_sg_per_500"])
        contractions_delta = abs(a["contractions_per_500"] - b["contractions_per_500"])
        dims_shifted = sum([
            sent_delta >= 5,
            ttr_delta >= 0.10,
            first_sg_delta >= 8,
            contractions_delta >= 5,
        ])
        if dims_shifted >= 2:
            shifts.append({
                "from_paragraph": i,
                "to_paragraph": i + 1,
                "sentence_length_delta": round(sent_delta, 2),
                "ttr_delta": round(ttr_delta, 3),
                "first_sg_delta": round(first_sg_delta, 2),
                "contractions_delta": round(contractions_delta, 2),
                "dimensions_shifted": dims_shifted,
            })
    return {
        "key": "style_shift",
        "name": "Pronounced style shift",
        "wikipedia_section": WIKI + "#Pronounced_shift_in_writing_style",
        "description": (
            "Adjacent paragraphs that diverge on 2+ stylistic dimensions "
            "simultaneously (sentence rhythm, lexical diversity, first-person "
            "rate, contraction rate). May indicate mixed authorship or "
            "switching between unedited LLM output and human revision."
        ),
        "raw_count": len(shifts),
        "per_500": _per_500(len(shifts), n_words),
        "top_hits": [],
        "examples": shifts[:5],
        "details": {"shifts_detected": len(shifts)},
        "notes": "",
    }


# #25 Skipped heading levels / thematic-break misplacement -------------

def _metric_heading_hierarchy(raw_text: str, n_words: int) -> dict:
    lines = raw_text.split("\n")
    issues: list[dict] = []
    prev_level = 0
    for idx, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if not m:
            continue
        level = len(m.group(1))
        text = m.group(2).strip()
        if prev_level and level > prev_level + 1:
            issues.append({
                "type": "skipped_level",
                "from_level": prev_level,
                "to_level": level,
                "heading": text[:120],
                "line": idx + 1,
            })
        # Thematic break (--- / *** / ___) right before this heading?
        if idx > 0 and re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", lines[idx - 1]):
            issues.append({
                "type": "thematic_break_before_heading",
                "heading": text[:120],
                "line": idx + 1,
            })
        prev_level = level
    return {
        "key": "heading_hierarchy",
        "name": "Skipped heading levels / thematic-break misplacement",
        "wikipedia_section": WIKI + "#Skipping_heading_levels",
        "description": (
            "Markdown headings that jump levels (e.g., H2 → H4) or are "
            "preceded by a horizontal rule serving no structural purpose."
        ),
        "raw_count": len(issues),
        "per_500": _per_500(len(issues), n_words),
        "top_hits": [],
        "examples": issues[:5],
        "details": {},
        "notes": "",
    }


# #26 Emoji as formatting ----------------------------------------------

def _metric_emoji(raw_text: str, n_words: int) -> dict:
    all_emojis = EMOJI_PATTERN.findall(raw_text)
    # Structural use: emoji at start of a line, used as bullet
    structural = len(re.findall(
        r"^\s*" + EMOJI_PATTERN.pattern + r"\s+",
        raw_text, re.MULTILINE,
    ))
    return {
        "key": "emoji_formatting",
        "name": "Emoji as formatting",
        "wikipedia_section": WIKI + "#Emoji_as_formatting",
        "description": (
            "Emoji characters used as bullet markers, section dividers, or "
            "structural decoration — a common LLM listicle move."
        ),
        "raw_count": len(all_emojis),
        "per_500": _per_500(len(all_emojis), n_words),
        "top_hits": Counter(all_emojis).most_common(8),
        "examples": [],
        "details": {
            "total_emoji": len(all_emojis),
            "structural_emoji": structural,
        },
        "notes": "",
    }


# ============================================================
# Orchestrator
# ============================================================

DENSITY_THRESHOLDS = [
    (15, "low"),
    (40, "moderate"),
    (80, "high"),
]


def classify_density(total_per_500: float) -> str:
    for threshold, label in DENSITY_THRESHOLDS:
        if total_per_500 < threshold:
            return label
    return "very_high"


def analyze_deep(
    raw_text: str,
    doc: Doc,
    paragraphs: list[str],
    paragraph_docs: list[Doc],
) -> dict:
    """Run all deep-scan metrics. Returns a uniform result dict.

    Args:
        raw_text:        Original input with markdown formatting preserved.
        doc:             spaCy parse of the quote-stripped text.
        paragraphs:      Quote-stripped paragraph strings.
        paragraph_docs:  Per-paragraph spaCy docs.
    """
    n_words = sum(1 for t in doc if t.is_alpha)
    text_lower = doc.text.lower()

    # Existing 8 metrics from aitext_signs
    existing = aitext_signs.analyze(doc)
    existing_metrics = existing["metrics"]

    # 14 new Tier-2 metrics + 4 Tier-3 metrics
    new_metrics = {
        "copula_avoidance":      _metric_copula_avoidance(doc, text_lower, n_words),
        "refers_to_lead":        _metric_refers_to_lead(paragraphs, n_words),
        "em_dash_overuse":       _metric_em_dash_overuse(raw_text, n_words),
        "curly_quotes":          _metric_curly_quotes(raw_text, n_words),
        "social_media_phrasing": _metric_social_media(doc, text_lower, n_words),
        "debate_claim":          _metric_debate_claim(doc, text_lower, n_words),
        "heritage_puffery":      _metric_heritage(doc, text_lower, n_words),
        "notability_puffery":    _metric_notability(doc, text_lower, n_words),
        "knowledge_cutoff":      _metric_knowledge_cutoff(doc, text_lower, n_words),
        "placeholders":          _metric_placeholders(raw_text, n_words),
        "title_case_headings":   _metric_title_case_headings(raw_text, n_words),
        "markdown_bold_density": _metric_markdown_bold(raw_text, n_words),
        "inline_header_lists":   _metric_inline_header_lists(raw_text, n_words),
        "markdown_artifacts":    _metric_markdown_artifacts(raw_text, n_words),
        # Tier 3
        "elegant_variation":     _metric_elegant_variation(paragraph_docs, n_words),
        "style_shift":           _metric_style_shift(paragraph_docs, n_words),
        "heading_hierarchy":     _metric_heading_hierarchy(raw_text, n_words),
        "emoji_formatting":      _metric_emoji(raw_text, n_words),
    }

    # Combine existing + new into a single ordered metrics dict.
    all_metrics: dict[str, dict] = {}
    for key, m in existing_metrics.items():
        # Existing metrics use a slightly different shape; normalize for the
        # deep-scan view.
        all_metrics[key] = {
            "key": key,
            "name": _existing_metric_name(key),
            "wikipedia_section": m.get("wikipedia_section", WIKI),
            "description": _existing_metric_description(key),
            "raw_count": m.get("raw_count", 0),
            "per_500": m.get("per_500", 0.0),
            "top_hits": m.get("top_hits", []) or m.get("top_starters", []) or [],
            "examples": m.get("examples", []),
            "details": {
                k: v for k, v in m.items()
                if k not in ("raw_count", "per_500", "top_hits", "examples",
                             "wikipedia_section", "top_starters")
            },
            "notes": "",
            "tier": "existing",
        }
    for key, m in new_metrics.items():
        m["tier"] = "new"
        all_metrics[key] = m

    total_raw = sum(m["raw_count"] for m in all_metrics.values())
    total_per_500 = _per_500(total_raw, n_words)
    density = classify_density(total_per_500)

    return {
        "metrics": all_metrics,
        "total_markers_raw": total_raw,
        "total_markers_per_500": total_per_500,
        "density": density,
        "wikipedia_url": WIKI,
        "n_words": n_words,
        "metric_count": len(all_metrics),
    }


_EXISTING_NAMES = {
    "ai_vocabulary":         "AI vocabulary",
    "promotional":           "Promotional phrasing",
    "significance":          "Significance emphasis",
    "vague_attribution":     "Vague attribution",
    "negative_parallelisms": "Negative parallelisms",
    "participial_tails":     "Participial pseudo-analysis",
    "rule_of_three":         "Rule of three",
    "conclusion_formulas":   "Conclusion formulas",
}

_EXISTING_DESCRIPTIONS = {
    "ai_vocabulary":         "Words documented as statistically frequent in LLM output post-2022. Three time-stratified lists (2023–mid-24, mid-24–mid-25, mid-25+).",
    "promotional":           "Travel-guide / press-release phrasing: 'boasts a', 'nestled in', 'diverse array', 'natural beauty'.",
    "significance":          "Generic statements connecting the subject to broader importance: 'stands as a testament', 'pivotal role', 'evolving landscape'.",
    "vague_attribution":     "References to unnamed authorities: 'experts argue', 'industry reports', 'several sources'.",
    "negative_parallelisms": "Contrastive 'not just X but Y' / 'not only … but also' constructions.",
    "participial_tails":     "Sentences ending in a comma + -ing clause making an unattributed analytical claim.",
    "rule_of_three":         "Three-item parallel lists with shared part-of-speech.",
    "conclusion_formulas":   "Stock closing patterns: 'despite its challenges', 'looking ahead', 'the future outlook remains'.",
}


def _existing_metric_name(key: str) -> str:
    return _EXISTING_NAMES.get(key, key.replace("_", " ").title())


def _existing_metric_description(key: str) -> str:
    return _EXISTING_DESCRIPTIONS.get(key, "")


def run_from_text(raw_text: str, topic: str | None = None) -> dict:
    """Convenience wrapper: take raw text, do full preprocessing, return result."""
    nlp = load_nlp()
    qr = strip_quotes(raw_text)
    stripped = qr.stripped_text
    paragraphs = split_paragraphs(stripped) or ([stripped] if stripped else [])
    doc = nlp(stripped) if stripped else nlp("")
    paragraph_docs = [nlp(p) for p in paragraphs]
    result = analyze_deep(raw_text, doc, paragraphs, paragraph_docs)
    result["topic"] = topic
    result["quoted_word_count"] = qr.quoted_word_count
    result["quoted_spans"] = len(qr.quoted_spans)
    return result
