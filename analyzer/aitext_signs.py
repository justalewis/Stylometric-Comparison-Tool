"""Section 6: stylistic patterns commonly found in AI-generated writing.

Based on Wikipedia's "Signs of AI writing" page
(https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). The metrics
here describe *stylistic markers* commonly observed in LLM output. They
are profile-only — no Strong/Partial/No Match comparator ratings — to
keep the framing honest: high rates suggest the writer reaches for these
patterns, not that the text was AI-generated.

Eight metrics, each producing a per-500-word rate, raw count, and
illustrative hits:

  1. AI vocabulary density (three time-stratified lists)
  2. Promotional / advertisement-like phrasing
  3. Significance / legacy emphasis
  4. Vague attribution patterns
  5. Negative parallelisms ("not just X, but Y")
  6. Participial pseudo-analysis (sentences ending in -ing clauses)
  7. Rule-of-three triplet structures
  8. Conclusion / outlook formulas
"""

from __future__ import annotations

import re
from collections import Counter

from spacy.tokens import Doc

from . import wordlists


WIKIPEDIA_BASE = "https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing"


def _per_500(n: int, n_words: int) -> float:
    if n_words == 0:
        return 0.0
    return round((n / n_words) * 500, 2)


def _count_word_set(doc: Doc, words: set[str]) -> Counter:
    counter: Counter = Counter()
    for tok in doc:
        if tok.is_alpha and tok.lower_ in words:
            counter[tok.lower_] += 1
    return counter


def _count_phrases(text_lower: str, phrases: list[str]) -> Counter:
    counter: Counter = Counter()
    for phrase in phrases:
        rx = re.compile(r"\b" + re.escape(phrase) + r"\b")
        c = len(rx.findall(text_lower))
        if c:
            counter[phrase] = c
    return counter


def _example_sentence(doc: Doc, needle: str) -> str:
    """First sentence containing the needle (case-insensitive), trimmed."""
    needle_lower = needle.lower()
    for sent in doc.sents:
        if needle_lower in sent.text.lower():
            return sent.text.strip()
    return ""


# -- M1. AI vocabulary density ----------------------------------------------

def analyze_ai_vocabulary(doc: Doc, n_words: int) -> dict:
    """Hits against the three time-stratified AI-vocabulary lists."""
    hits_2023 = _count_word_set(doc, wordlists.AI_VOCAB_2023_MID2024)
    hits_2024 = _count_word_set(doc, wordlists.AI_VOCAB_MID2024_MID2025)
    hits_2025 = _count_word_set(doc, wordlists.AI_VOCAB_MID2025_PLUS)
    phrase_hits = _count_phrases(doc.text.lower(), wordlists.AI_VOCAB_PHRASES)

    # The lists overlap; for the headline rate we count each distinct hit
    # only once across the three lists.
    combined: Counter = Counter()
    for c in (hits_2023, hits_2024, hits_2025):
        combined.update(c)
    total_hits = sum(combined.values()) + sum(phrase_hits.values())

    # Provenance: which list each hit appears on.
    provenance: dict[str, list[str]] = {}
    for word in combined:
        eras: list[str] = []
        if word in wordlists.AI_VOCAB_2023_MID2024:
            eras.append("2023-mid24")
        if word in wordlists.AI_VOCAB_MID2024_MID2025:
            eras.append("mid24-mid25")
        if word in wordlists.AI_VOCAB_MID2025_PLUS:
            eras.append("mid25+")
        provenance[word] = eras

    return {
        "wikipedia_section": f"{WIKIPEDIA_BASE}#High_density_of_%22AI_vocabulary%22_words",
        "raw_count": total_hits,
        "per_500": _per_500(total_hits, n_words),
        "top_hits": combined.most_common(10),
        "phrase_hits": phrase_hits.most_common(5),
        "provenance": provenance,
    }


# -- M2. Promotional / ad-like phrasing -------------------------------------

def analyze_promotional(doc: Doc, n_words: int) -> dict:
    text_lower = doc.text.lower()
    phrase_hits = _count_phrases(text_lower, wordlists.AI_PROMOTIONAL_PHRASES)
    single_hits = _count_word_set(doc, wordlists.AI_PROMOTIONAL_SINGLES)
    total = sum(phrase_hits.values()) + sum(single_hits.values())
    top = (phrase_hits + single_hits).most_common(8)
    examples = []
    for term, _ in top[:3]:
        ex = _example_sentence(doc, term)
        if ex:
            examples.append({"term": term, "sentence": ex[:200]})
    return {
        "wikipedia_section": f"{WIKIPEDIA_BASE}#Promotional_and_advertisement-like_language",
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": top,
        "examples": examples,
    }


# -- M3. Significance / legacy emphasis -------------------------------------

def analyze_significance(doc: Doc, n_words: int) -> dict:
    text_lower = doc.text.lower()
    hits = _count_phrases(text_lower, wordlists.AI_SIGNIFICANCE_PHRASES)
    total = sum(hits.values())
    top = hits.most_common(8)
    examples = []
    for term, _ in top[:3]:
        ex = _example_sentence(doc, term)
        if ex:
            examples.append({"term": term, "sentence": ex[:200]})
    return {
        "wikipedia_section": f"{WIKIPEDIA_BASE}#Undue_emphasis_on_significance,_legacy,_and_broader_trends",
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": top,
        "examples": examples,
    }


# -- M4. Vague attribution --------------------------------------------------

def analyze_vague_attribution(doc: Doc, n_words: int) -> dict:
    text_lower = doc.text.lower()
    hits = _count_phrases(text_lower, wordlists.AI_VAGUE_ATTRIBUTION_PHRASES)
    total = sum(hits.values())
    top = hits.most_common(8)
    examples = []
    for term, _ in top[:3]:
        ex = _example_sentence(doc, term)
        if ex:
            examples.append({"term": term, "sentence": ex[:200]})
    return {
        "wikipedia_section": f"{WIKIPEDIA_BASE}#Vague_attributions_and_overgeneralization_of_opinions",
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": top,
        "examples": examples,
    }


# -- M5. Negative parallelisms ----------------------------------------------

_NEG_PARALLEL_PATTERNS = [
    # not just X, but (also)? Y
    re.compile(r"\bnot\s+just\b[^.!?\n]{2,80}?,\s*(?:but|it'?s|it is)\b", re.IGNORECASE),
    # not only X, but (also)? Y
    re.compile(r"\bnot\s+only\b[^.!?\n]{2,80}?,?\s*but(?:\s+also)?\b", re.IGNORECASE),
    # it is not X, it is Y    /    it's not X, it's Y
    re.compile(r"\bit'?s?\s+not\b[^.!?\n]{2,60}?,\s*it'?s?\b", re.IGNORECASE),
    # not X, but Y  (more constrained to avoid false positives on plain "not")
    re.compile(r"\bnot\s+[a-z]+(?:\s+[a-z]+){0,4},\s*but\b", re.IGNORECASE),
]


def analyze_negative_parallelisms(doc: Doc, n_words: int) -> dict:
    text = doc.text
    matches: list[str] = []
    for pattern in _NEG_PARALLEL_PATTERNS:
        for m in pattern.finditer(text):
            matches.append(m.group(0))
    # Dedupe while preserving order.
    seen: set[str] = set()
    unique = []
    for m in matches:
        key = m.lower()
        if key not in seen:
            seen.add(key)
            unique.append(m)
    examples = []
    for ex in unique[:3]:
        full = _example_sentence(doc, ex[:30])
        examples.append({"term": ex[:80], "sentence": full[:220] if full else ex})
    return {
        "wikipedia_section": f"{WIKIPEDIA_BASE}#Not_just_X,_but_also_Y",
        "raw_count": len(unique),
        "per_500": _per_500(len(unique), n_words),
        "examples": examples,
    }


# -- M6. Participial pseudo-analysis ----------------------------------------

def analyze_participial_tails(doc: Doc, n_words: int) -> dict:
    """Sentences ending in a comma + present-participle clause.

    Pattern: "..., highlighting the importance of X."
    Detection: for each sentence, find the last comma, then check that what
    follows starts with a VBG token (or one of the curated starters) and
    extends to sentence end.
    """
    sents = list(doc.sents)
    matches: list[dict] = []
    for sent in sents:
        tokens = [t for t in sent if not t.is_space]
        if len(tokens) < 5:
            continue
        # Find the last comma.
        last_comma_idx = None
        for i in range(len(tokens) - 1, -1, -1):
            if tokens[i].text == ",":
                last_comma_idx = i
                break
        if last_comma_idx is None or last_comma_idx >= len(tokens) - 2:
            continue
        next_tok = tokens[last_comma_idx + 1]
        starter_match = (
            next_tok.tag_ == "VBG"
            or next_tok.lower_ in wordlists.AI_PARTICIPIAL_STARTERS
        )
        if not starter_match:
            continue
        tail = sent.text[next_tok.idx - sent.start_char :].strip(" .,;:!?")
        matches.append({
            "starter": next_tok.lower_,
            "tail": tail[:120],
            "sentence": sent.text.strip()[:220],
        })
    starter_counts = Counter(m["starter"] for m in matches)
    return {
        "wikipedia_section": f"{WIKIPEDIA_BASE}#Superficial_analyses",
        "raw_count": len(matches),
        "per_500": _per_500(len(matches), n_words),
        "top_starters": starter_counts.most_common(8),
        "examples": matches[:3],
    }


# -- M7. Rule of three (triplet structures) ---------------------------------

def analyze_rule_of_three(doc: Doc, n_words: int) -> dict:
    """Three-item parallel lists: 'X, Y, and Z' where X/Y/Z are content words.

    Detection: a content token, followed by ", " + content token, followed
    by ", and/or " + content token. We allow ADJ or NOUN/PROPN heads in
    each slot and require the three slots to share POS to bias toward
    parallel structure.
    """
    sents = list(doc.sents)
    hits: list[dict] = []
    for sent in sents:
        toks = list(sent)
        for i, tok in enumerate(toks):
            if tok.pos_ not in ("ADJ", "NOUN", "PROPN"):
                continue
            # Look for the pattern: tok, "," tok2, "," ("and"|"or") tok3.
            if i + 6 >= len(toks):
                continue
            window = toks[i:i + 8]
            try:
                t0 = window[0]
                if window[1].text != ",":
                    continue
                t1 = window[2]
                if t1.pos_ not in ("ADJ", "NOUN", "PROPN"):
                    continue
                if window[3].text != ",":
                    continue
                conj = window[4]
                if conj.lower_ not in ("and", "or"):
                    continue
                t2 = window[5]
                if t2.pos_ not in ("ADJ", "NOUN", "PROPN"):
                    continue
                if not (t0.pos_ == t1.pos_ == t2.pos_):
                    continue
                hits.append({
                    "items": [t0.text, t1.text, t2.text],
                    "sentence": sent.text.strip()[:220],
                })
            except IndexError:
                continue
    return {
        "wikipedia_section": f"{WIKIPEDIA_BASE}#Rule_of_three",
        "raw_count": len(hits),
        "per_500": _per_500(len(hits), n_words),
        "examples": hits[:4],
    }


# -- M8. Conclusion / outlook formulas --------------------------------------

def analyze_conclusion_formulas(doc: Doc, n_words: int) -> dict:
    text_lower = doc.text.lower()
    hits = _count_phrases(text_lower, wordlists.AI_CONCLUSION_PHRASES)
    total = sum(hits.values())
    top = hits.most_common(8)
    examples = []
    for term, _ in top[:3]:
        ex = _example_sentence(doc, term)
        if ex:
            examples.append({"term": term, "sentence": ex[:200]})
    return {
        "wikipedia_section": f"{WIKIPEDIA_BASE}#Outline-like_conclusions_about_challenges_and_future_prospects",
        "raw_count": total,
        "per_500": _per_500(total, n_words),
        "top_hits": top,
        "examples": examples,
    }


# -- Aggregator -------------------------------------------------------------

def analyze(doc: Doc) -> dict:
    n_words = sum(1 for t in doc if t.is_alpha)
    metrics = {
        "ai_vocabulary":         analyze_ai_vocabulary(doc, n_words),
        "promotional":           analyze_promotional(doc, n_words),
        "significance":          analyze_significance(doc, n_words),
        "vague_attribution":     analyze_vague_attribution(doc, n_words),
        "negative_parallelisms": analyze_negative_parallelisms(doc, n_words),
        "participial_tails":     analyze_participial_tails(doc, n_words),
        "rule_of_three":         analyze_rule_of_three(doc, n_words),
        "conclusion_formulas":   analyze_conclusion_formulas(doc, n_words),
    }
    # Headline summary: total markers per 500 words (sum across the eight).
    total_markers = sum(m["raw_count"] for m in metrics.values())
    return {
        "wikipedia_url": WIKIPEDIA_BASE,
        "metrics": metrics,
        "total_markers_raw": total_markers,
        "total_markers_per_500": _per_500(total_markers, n_words),
    }
