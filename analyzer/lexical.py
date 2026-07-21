"""Section 1: lexical preferences.

  1.1 Lexical diversity (TTR, MATTR, MTLD)
  1.2 Latinate vs. Germanic vocabulary tendency
  1.3 Pet words and habitual phrases
  1.4 Informal hedges, fillers, and intensifiers
  1.5 Reading level (Flesch-Kincaid Grade, Flesch Reading Ease)
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

import textstat
from spacy.tokens import Doc

from . import wordlists


# Reading-level metrics are meaningless below a handful of full sentences;
# below these thresholds the values return None and the report surfaces a
# warning instead.
READING_MIN_WORDS = 50
READING_MIN_SENTENCES = 3


# Validity bounds for length-robust diversity metrics. Below these counts
# the metric returns None and the report surfaces a warning instead of a
# misleadingly precise number.
MATTR_WINDOW = 100
MATTR_MIN_TOKENS = 200      # need at least 2x the window for a useful average
MTLD_THRESHOLD = 0.72       # McCarthy & Jarvis (2010) standard
MTLD_MIN_TOKENS = 100


def _content_tokens(doc: Doc) -> list[str]:
    """Return lowercased word forms, excluding punctuation, spaces, numbers."""
    return [
        t.lower_
        for t in doc
        if t.is_alpha and not t.is_space
    ]


def _mattr(tokens: list[str], window: int = MATTR_WINDOW) -> float | None:
    """Moving-Average Type-Token Ratio.

    Slides a fixed window across the token list and averages the TTR
    computed within each window. Length-independent: comparable across
    texts of very different total lengths. Returns None when the text is
    shorter than ``MATTR_MIN_TOKENS``.
    """
    n = len(tokens)
    if n < MATTR_MIN_TOKENS or n < window:
        return None
    ratios: list[float] = []
    # Counter-based sliding window: add the entering token, drop the
    # exiting token, recompute distinct-count incrementally.
    window_counts: Counter = Counter(tokens[:window])
    distinct = sum(1 for v in window_counts.values() if v > 0)
    ratios.append(distinct / window)
    for i in range(1, n - window + 1):
        leaving = tokens[i - 1]
        entering = tokens[i + window - 1]
        if leaving != entering:
            window_counts[leaving] -= 1
            if window_counts[leaving] == 0:
                distinct -= 1
            if window_counts[entering] == 0:
                distinct += 1
            window_counts[entering] += 1
        ratios.append(distinct / window)
    return round(sum(ratios) / len(ratios), 3)


def _mtld_one_direction(tokens: list[str], threshold: float = MTLD_THRESHOLD) -> float:
    """Single-pass MTLD (McCarthy & Jarvis 2010). Internal helper."""
    factors = 0.0
    types: set[str] = set()
    running_count = 0
    last_ttr = 1.0
    for tok in tokens:
        types.add(tok)
        running_count += 1
        last_ttr = len(types) / running_count
        if last_ttr <= threshold:
            factors += 1
            types = set()
            running_count = 0
            last_ttr = 1.0
    # Leftover tokens at the tail that didn't reach the threshold:
    # scale them by how close they came.
    if running_count > 0 and last_ttr < 1.0:
        partial = (1.0 - last_ttr) / (1.0 - threshold)
        factors += partial
    if factors <= 0:
        return float(len(tokens))
    return len(tokens) / factors


def _mtld(tokens: list[str], threshold: float = MTLD_THRESHOLD) -> float | None:
    """Bidirectional MTLD: mean of forward and backward single-pass MTLDs."""
    if len(tokens) < MTLD_MIN_TOKENS:
        return None
    fwd = _mtld_one_direction(tokens, threshold)
    bwd = _mtld_one_direction(list(reversed(tokens)), threshold)
    return round((fwd + bwd) / 2, 1)


def analyze_ttr(doc: Doc) -> dict:
    """Compute three lexical-diversity metrics: TTR, MATTR, MTLD.

    TTR is the raw type-token ratio (length-sensitive, kept for backward
    compatibility and for very-short-sample reporting). MATTR and MTLD
    are length-robust alternatives — when both texts are long enough
    they are the more defensible comparison signals.
    """
    tokens = _content_tokens(doc)
    types = set(tokens)
    n_tokens = len(tokens)
    n_types = len(types)
    ratio = round(n_types / n_tokens, 3) if n_tokens else 0.0
    mattr = _mattr(tokens)
    mtld = _mtld(tokens)

    warnings: list[str] = []
    if n_tokens < MTLD_MIN_TOKENS:
        warnings.append(
            f"Sample under {MTLD_MIN_TOKENS} words — MATTR and MTLD suppressed; "
            f"only raw TTR reported (and TTR is mechanically inflated for short texts)."
        )
    elif n_tokens < MATTR_MIN_TOKENS:
        warnings.append(
            f"Sample under {MATTR_MIN_TOKENS} words — MATTR suppressed; "
            f"MTLD and raw TTR reported, but treat as approximate."
        )

    return {
        "tokens": n_tokens,
        "types": n_types,
        "ratio": ratio,
        "mattr": mattr,
        "mtld": mtld,
        "mattr_window": MATTR_WINDOW,
        "mtld_threshold": MTLD_THRESHOLD,
        "warnings": warnings,
    }


def analyze_latinate_germanic(doc: Doc) -> dict:
    tokens = _content_tokens(doc)
    latinate_hits: list[str] = []
    germanic_hits: list[str] = []
    for tok in tokens:
        if tok in wordlists.LATINATE:
            latinate_hits.append(tok)
        elif tok in wordlists.GERMANIC:
            germanic_hits.append(tok)
    total = len(latinate_hits) + len(germanic_hits)
    ratio = round(len(latinate_hits) / total, 3) if total else 0.0
    return {
        "latinate_count": len(latinate_hits),
        "germanic_count": len(germanic_hits),
        "latinate_ratio": ratio,
        "latinate_top": Counter(latinate_hits).most_common(10),
        "germanic_top": Counter(germanic_hits).most_common(10),
    }


def _ngrams(tokens: list[str], n: int) -> Iterable[tuple[str, ...]]:
    return (tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))


def _example_sentence(doc: Doc, target: str) -> str:
    """Return the first sentence containing the target word/phrase, trimmed."""
    target_lower = target.lower()
    for sent in doc.sents:
        if target_lower in sent.text.lower():
            return sent.text.strip()
    return ""


def analyze_pet_words(doc: Doc, topic: str | None = None) -> dict:
    """Flag repeated content words and 2-4 gram phrases not required by topic."""
    tokens = _content_tokens(doc)
    n_tokens = len(tokens)

    # Threshold per the spec: 3+ occurrences, or 2+ if text < 400 words.
    threshold = 2 if n_tokens < 400 else 3

    content_only = [t for t in tokens if t not in wordlists.FUNCTION_WORDS]
    counts = Counter(content_only)
    flagged = [(w, c) for w, c in counts.items() if c >= threshold]
    flagged.sort(key=lambda wc: (-wc[1], wc[0]))

    topic_terms: set[str] = set()
    if topic:
        topic_terms = {w.lower() for w in re.findall(r"\b\w+\b", topic)}

    topical: list[tuple[str, int, str]] = []
    habitual: list[tuple[str, int, str]] = []
    for word, count in flagged:
        example = _example_sentence(doc, word)
        if word in topic_terms:
            topical.append((word, count, example))
        else:
            habitual.append((word, count, example))

    # Multiword phrases (2-4 grams) that recur. Skip n-grams that are entirely
    # function words.
    text_lower = [t.lower_ for t in doc if t.is_alpha or t.is_punct]
    word_tokens_only = [t for t in text_lower if re.match(r"\w", t)]
    phrase_hits: list[tuple[str, int, str]] = []
    seen_phrases: set[str] = set()
    for n in (4, 3, 2):
        gram_counts = Counter(_ngrams(word_tokens_only, n))
        for gram, count in gram_counts.items():
            if count < 2:
                continue
            if all(w in wordlists.FUNCTION_WORDS for w in gram):
                continue
            phrase = " ".join(gram)
            # Skip phrases that are subphrases of an already-recorded longer phrase.
            if any(phrase in longer for longer in seen_phrases):
                continue
            seen_phrases.add(phrase)
            example = _example_sentence(doc, phrase)
            phrase_hits.append((phrase, count, example))
    phrase_hits.sort(key=lambda x: (-x[1], -len(x[0].split()), x[0]))

    return {
        "threshold_used": threshold,
        "habitual_words": habitual[:15],
        "topical_words": topical[:15],
        "habitual_phrases": phrase_hits[:15],
        "habitual_word_set": {w for w, _, _ in habitual},
        "habitual_phrase_set": {p for p, _, _ in phrase_hits},
    }


def _count_pattern(text_lower: str, pattern: str) -> int:
    """Count whole-phrase or whole-word occurrences in lowercased text."""
    rx = re.compile(r"\b" + re.escape(pattern) + r"\b")
    return len(rx.findall(text_lower))


def analyze_hedges(doc: Doc) -> dict:
    """Count informal hedges/fillers, intensifiers, and formal hedges."""
    text_lower = doc.text.lower()
    tokens = _content_tokens(doc)
    n_tokens = len(tokens) or 1

    informal_singles = Counter(t for t in tokens if t in wordlists.INFORMAL_HEDGES_SINGLE)
    informal_multi = Counter()
    for phrase in wordlists.INFORMAL_HEDGES_MULTI:
        c = _count_pattern(text_lower, phrase)
        if c:
            informal_multi[phrase] = c

    intensifier_singles = Counter(t for t in tokens if t in wordlists.INTENSIFIERS_SINGLE)
    intensifier_multi = Counter()
    for phrase in wordlists.INTENSIFIERS_MULTI:
        c = _count_pattern(text_lower, phrase)
        if c:
            intensifier_multi[phrase] = c

    formal_singles = Counter(t for t in tokens if t in wordlists.FORMAL_HEDGES_SINGLE)
    formal_multi = Counter()
    for phrase in wordlists.FORMAL_HEDGES_MULTI:
        c = _count_pattern(text_lower, phrase)
        if c:
            formal_multi[phrase] = c

    informal_total = sum(informal_singles.values()) + sum(informal_multi.values())
    intensifier_total = sum(intensifier_singles.values()) + sum(intensifier_multi.values())
    formal_total = sum(formal_singles.values()) + sum(formal_multi.values())

    per_500 = lambda n: round((n / n_tokens) * 500, 2)

    if informal_total > formal_total and per_500(informal_total) >= 3:
        dominant = "informal"
    elif formal_total > informal_total and per_500(formal_total) >= 2:
        dominant = "formal"
    elif informal_total == 0 and formal_total == 0:
        dominant = "low across the board"
    else:
        dominant = "mixed"

    return {
        "informal_total": informal_total,
        "informal_per_500": per_500(informal_total),
        "informal_top": (informal_singles + informal_multi).most_common(10),
        "intensifier_total": intensifier_total,
        "intensifier_per_500": per_500(intensifier_total),
        "intensifier_top": (intensifier_singles + intensifier_multi).most_common(10),
        "formal_total": formal_total,
        "formal_per_500": per_500(formal_total),
        "formal_top": (formal_singles + formal_multi).most_common(10),
        "dominant_pattern": dominant,
    }


def _fk_grade_label(grade: float) -> str:
    """Human-readable interpretation of a Flesch-Kincaid Grade Level."""
    if grade < 6:  return "elementary"
    if grade < 9:  return "middle school"
    if grade < 13: return "high school"
    if grade < 17: return "college"
    return "graduate / specialist"


def _fre_label(fre: float) -> str:
    """Human-readable band for a Flesch Reading Ease score."""
    if fre >= 90: return "very easy"
    if fre >= 80: return "easy"
    if fre >= 70: return "fairly easy"
    if fre >= 60: return "standard"
    if fre >= 50: return "fairly difficult"
    if fre >= 30: return "difficult"
    return "very difficult"


def analyze_reading_level(doc: Doc) -> dict:
    """Flesch-Kincaid Grade Level + Flesch Reading Ease.

    Both metrics take word length (syllables per word) and sentence length
    into account. Grade Level maps to a US school-grade equivalent;
    Reading Ease is a 0-100 scale where higher = easier to read.
    Undefined on very short samples — returns None + warning when the
    sample has fewer than READING_MIN_WORDS words or READING_MIN_SENTENCES
    sentences.
    """
    text = doc.text.strip()
    n_words = sum(1 for t in doc if t.is_alpha)
    n_sents = sum(1 for _ in doc.sents)
    warnings: list[str] = []

    if not text or n_words < READING_MIN_WORDS or n_sents < READING_MIN_SENTENCES:
        warnings.append(
            f"Sample under {READING_MIN_WORDS} words or "
            f"{READING_MIN_SENTENCES} sentences — reading-level metrics suppressed."
        )
        return {
            "fk_grade": None,
            "fk_grade_label": None,
            "flesch_reading_ease": None,
            "flesch_reading_ease_label": None,
            "warnings": warnings,
        }

    try:
        fk_grade = round(float(textstat.flesch_kincaid_grade(text)), 1)
        fre = round(float(textstat.flesch_reading_ease(text)), 1)
    except Exception:
        return {
            "fk_grade": None,
            "fk_grade_label": None,
            "flesch_reading_ease": None,
            "flesch_reading_ease_label": None,
            "warnings": ["Reading-level calculation failed on this text."],
        }

    return {
        "fk_grade": fk_grade,
        "fk_grade_label": _fk_grade_label(fk_grade),
        "flesch_reading_ease": fre,
        "flesch_reading_ease_label": _fre_label(fre),
        "warnings": warnings,
    }


def analyze(doc: Doc, topic: str | None = None) -> dict:
    return {
        "ttr": analyze_ttr(doc),
        "latinate_germanic": analyze_latinate_germanic(doc),
        "pet_words": analyze_pet_words(doc, topic),
        "hedges": analyze_hedges(doc),
        "reading_level": analyze_reading_level(doc),
    }
