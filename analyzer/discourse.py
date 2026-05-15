"""Section 3: discourse organization.

  3.1 Paragraph structure (count, length, topic-sentence position)
  3.2 Transition strategy
  3.3 Evidence-to-claim sequencing
  3.4 Metadiscourse (textual + interpersonal)

Topic-sentence detection is necessarily approximate. We score each sentence
within a paragraph by (a) presence of interpretation/claim markers and
(b) density of the paragraph's most frequent content words, then pick the
highest-scoring sentence as the candidate "claim" sentence. The report
labels this dimension explicitly as a heuristic.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter

from spacy.tokens import Doc

from . import wordlists


# -- 3.1 Paragraph structure ------------------------------------------------

_CLAIM_VERBS = {
    "argue", "argues", "claim", "claims", "show", "shows", "mean", "means",
    "suggest", "suggests", "indicate", "indicates", "imply", "implies",
    "demonstrate", "demonstrates", "reveal", "reveals", "prove", "proves",
    "confirm", "confirms", "highlight", "highlights",
}


def _paragraph_sentences(p_doc: Doc) -> list:
    return [s for s in p_doc.sents if sum(1 for t in s if t.is_alpha) >= 1]


def _topic_sentence_position(p_doc: Doc) -> tuple[str, str]:
    """Return ('first'|'last'|'embedded'|'distributed', example_text)."""
    sents = _paragraph_sentences(p_doc)
    if not sents:
        return "distributed", ""
    if len(sents) == 1:
        return "first", sents[0].text.strip()

    # Build paragraph-level content-word frequencies.
    content = [
        t.lower_ for t in p_doc
        if t.is_alpha and t.lower_ not in wordlists.FUNCTION_WORDS
    ]
    freq = Counter(content)
    top_terms = {w for w, _ in freq.most_common(5)}

    scores: list[float] = []
    for sent in sents:
        sent_lower = sent.text.lower()
        # Claim marker score.
        marker_score = sum(
            1 for phrase in wordlists.INTERPRETATION_MARKERS
            if phrase in sent_lower
        )
        # Claim verb score.
        verb_score = sum(
            1 for tok in sent
            if tok.lemma_.lower() in _CLAIM_VERBS
        )
        # Topic term density.
        sent_content = [
            t.lower_ for t in sent
            if t.is_alpha and t.lower_ not in wordlists.FUNCTION_WORDS
        ]
        topic_score = (
            sum(1 for w in sent_content if w in top_terms) / max(len(sent_content), 1)
        )
        scores.append(marker_score * 2 + verb_score + topic_score)

    max_score = max(scores)
    # If two or more sentences tie at the top, call it distributed.
    top_indices = [i for i, s in enumerate(scores) if s == max_score]
    if max_score == 0 or len(top_indices) > 1:
        return "distributed", ""

    idx = top_indices[0]
    if idx == 0:
        return "first", sents[idx].text.strip()
    if idx == len(sents) - 1:
        return "last", sents[idx].text.strip()
    return "embedded", sents[idx].text.strip()


def analyze_paragraph_structure(paragraph_docs: list[Doc]) -> dict:
    sent_counts: list[int] = []
    positions: list[str] = []
    examples: dict[str, list[str]] = {
        "first": [], "last": [], "embedded": [], "distributed": [],
    }
    for p_doc in paragraph_docs:
        sents = _paragraph_sentences(p_doc)
        sent_counts.append(len(sents))
        pos, ex = _topic_sentence_position(p_doc)
        positions.append(pos)
        if ex and len(examples[pos]) < 2:
            examples[pos].append(ex)

    counts = Counter(positions)
    dominant = counts.most_common(1)[0][0] if counts else "distributed"

    return {
        "paragraph_count": len(paragraph_docs),
        "mean_sentences": round(statistics.mean(sent_counts), 2) if sent_counts else 0.0,
        "median_sentences": statistics.median(sent_counts) if sent_counts else 0,
        "min_sentences": min(sent_counts) if sent_counts else 0,
        "max_sentences": max(sent_counts) if sent_counts else 0,
        "topic_position_counts": dict(counts),
        "dominant_topic_position": dominant,
        "examples": examples,
    }


# -- 3.2 Transition strategy ------------------------------------------------

def _transition_category(first_sent_text: str) -> tuple[str, str]:
    lower = first_sent_text.lower().strip()
    # Check metadiscursive narration first.
    for phrase in wordlists.METADISCOURSE_TEXTUAL:
        if lower.startswith(phrase) or f". {phrase}" in lower[:120]:
            return "metadiscursive_narration", phrase
    # Explicit transitional phrases.
    for phrase in wordlists.TRANSITIONAL_PHRASES:
        if lower.startswith(phrase):
            return "explicit_transitional", phrase
    # Single-word transitional connectors.
    first_word = re.match(r"\w+", lower)
    if first_word and first_word.group(0) in wordlists.TRANSITIONAL_CONNECTORS:
        return "explicit_transitional", first_word.group(0)
    return "implicit", ""


def analyze_transitions(paragraph_docs: list[Doc]) -> dict:
    if len(paragraph_docs) < 2:
        return {
            "dominant_strategy": "indeterminate",
            "category_counts": {},
            "examples": {},
            "note": "Fewer than 2 paragraphs; no transitions to analyze.",
        }
    cats: list[str] = []
    examples: dict[str, list[str]] = {
        "metadiscursive_narration": [], "explicit_transitional": [], "implicit": [],
    }
    for p_doc in paragraph_docs[1:]:
        sents = _paragraph_sentences(p_doc)
        if not sents:
            continue
        first = sents[0].text.strip()
        cat, marker = _transition_category(first)
        cats.append(cat)
        if len(examples[cat]) < 3:
            snippet = first[:120] + ("..." if len(first) > 120 else "")
            examples[cat].append(snippet)
    counts = Counter(cats)
    # Hybrid if no category exceeds 60%.
    total = sum(counts.values()) or 1
    top_cat, top_n = (counts.most_common(1) or [("indeterminate", 0)])[0]
    if top_n / total < 0.6:
        dominant = "hybrid"
    else:
        dominant = top_cat
    return {
        "dominant_strategy": dominant,
        "category_counts": dict(counts),
        "examples": examples,
    }


# -- 3.3 Evidence-to-claim sequencing ---------------------------------------

_CITATION_PATTERN = re.compile(r"\(\s*[A-Z][A-Za-z\-]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][A-Za-z\-]+))?,?\s+\d{4}[a-z]?\s*\)")
_BRACKET_CITE = re.compile(r"\[\d+\]")
_ANECDOTAL_MARKERS = [
    "when i was", "i remember", "i used to", "growing up", "my friend",
    "my mom", "my dad", "my brother", "my sister", "in my experience",
    "i once", "back when",
]
_HYPOTHETICAL_MARKERS = [
    "imagine", "suppose", "let us say", "let's say", "what if", "say that",
    "consider a", "consider the case",
]


def _detect_evidence_types(p_text: str) -> dict:
    lower = p_text.lower()
    return {
        "citations": bool(_CITATION_PATTERN.search(p_text)) or bool(_BRACKET_CITE.search(p_text)),
        "quoted_material": '"' in p_text or '“' in p_text,
        "anecdotal": any(m in lower for m in _ANECDOTAL_MARKERS),
        "hypothetical": any(m in lower for m in _HYPOTHETICAL_MARKERS),
        "rhetorical_question": "?" in p_text,
    }


def _detect_interpretation(p_text: str) -> bool:
    lower = p_text.lower()
    return any(m in lower for m in wordlists.INTERPRETATION_MARKERS)


def _claim_evidence_pattern(p_doc: Doc, p_text: str) -> str:
    """Approximate the dominant claim/evidence sequencing in a paragraph."""
    sents = _paragraph_sentences(p_doc)
    if not sents:
        return "no_content"

    has_external = (
        bool(_CITATION_PATTERN.search(p_text))
        or bool(_BRACKET_CITE.search(p_text))
        or '"' in p_text
        or '“' in p_text
    )
    has_interpretation = _detect_interpretation(p_text)

    if not has_external:
        return "claim_then_elaboration"

    # Find position of first evidence marker and first interpretation marker.
    lower = p_text.lower()
    interp_positions = [
        lower.find(m) for m in wordlists.INTERPRETATION_MARKERS if m in lower
    ]
    first_interp = min(interp_positions) if interp_positions else -1

    cite_match = _CITATION_PATTERN.search(p_text) or _BRACKET_CITE.search(p_text)
    quote_pos = min(
        (p_text.find(c) for c in '"“' if c in p_text),
        default=-1,
    )
    evidence_positions = [
        pos for pos in (cite_match.start() if cite_match else -1, quote_pos)
        if pos >= 0
    ]
    first_evidence = min(evidence_positions) if evidence_positions else -1

    # First sentence position.
    first_sent_end = sents[0].end_char

    if first_evidence < first_sent_end and not has_interpretation:
        return "evidence_then_claim"
    if has_interpretation:
        if first_interp > first_evidence > 0:
            return "claim_evidence_interpretation"
        return "claim_evidence_interpretation"
    return "claim_evidence_no_interpretation"


def analyze_evidence_claim(paragraphs: list[str], paragraph_docs: list[Doc]) -> dict:
    patterns: list[str] = []
    evidence_types: Counter = Counter()
    for p_text, p_doc in zip(paragraphs, paragraph_docs):
        pat = _claim_evidence_pattern(p_doc, p_text)
        patterns.append(pat)
        types = _detect_evidence_types(p_text)
        for k, v in types.items():
            if v:
                evidence_types[k] += 1

    counts = Counter(patterns)
    dominant = counts.most_common(1)[0][0] if counts else "no_content"

    return {
        "pattern_counts": dict(counts),
        "dominant_pattern": dominant,
        "evidence_types": dict(evidence_types),
        "primary_evidence_type": (
            evidence_types.most_common(1)[0][0] if evidence_types else "none"
        ),
    }


# -- 3.4 Metadiscourse ------------------------------------------------------

def _count_phrases(text: str, phrases: list[str]) -> tuple[int, Counter]:
    counter: Counter = Counter()
    lower = text.lower()
    total = 0
    for phrase in phrases:
        c = len(re.findall(r"\b" + re.escape(phrase) + r"\b", lower))
        if c:
            counter[phrase] = c
            total += c
    return total, counter


def analyze_metadiscourse(doc: Doc) -> dict:
    text = doc.text
    n_words = sum(1 for t in doc if t.is_alpha) or 1
    per_500 = lambda n: round((n / n_words) * 500, 2)

    textual_total, textual_hits = _count_phrases(text, wordlists.METADISCOURSE_TEXTUAL)
    interpersonal_total, interpersonal_hits = _count_phrases(
        text, wordlists.METADISCOURSE_INTERPERSONAL
    )

    return {
        "textual_total": textual_total,
        "textual_per_500": per_500(textual_total),
        "textual_top": textual_hits.most_common(10),
        "interpersonal_total": interpersonal_total,
        "interpersonal_per_500": per_500(interpersonal_total),
        "interpersonal_top": interpersonal_hits.most_common(10),
    }


def analyze(doc: Doc, paragraphs: list[str], paragraph_docs: list[Doc]) -> dict:
    return {
        "paragraph_structure": analyze_paragraph_structure(paragraph_docs),
        "transitions": analyze_transitions(paragraph_docs),
        "evidence_claim": analyze_evidence_claim(paragraphs, paragraph_docs),
        "metadiscourse": analyze_metadiscourse(doc),
    }
