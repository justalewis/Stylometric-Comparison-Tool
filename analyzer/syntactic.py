"""Section 2: syntactic patterns.

  2.1 Sentence length distribution
  2.2 Sentence-opening patterns
  2.3 Coordination vs. subordination tendency
  2.4 Punctuation patterns
"""

from __future__ import annotations

import re
import statistics
from collections import Counter

from spacy.tokens import Doc, Span

from . import wordlists


# -- 2.1 Sentence length -----------------------------------------------------

def _sentence_word_count(sent: Span) -> int:
    return sum(1 for t in sent if t.is_alpha)


def analyze_sentence_length(doc: Doc) -> dict:
    sents = [s for s in doc.sents if _sentence_word_count(s) >= 1]
    lengths = [_sentence_word_count(s) for s in sents]
    if not lengths:
        return {
            "count": 0, "mean": 0.0, "median": 0.0, "stdev": 0.0,
            "shortest": None, "longest": None, "buckets": {},
        }
    buckets = {
        "short_1_10": sum(1 for x in lengths if 1 <= x <= 10),
        "medium_11_20": sum(1 for x in lengths if 11 <= x <= 20),
        "long_21_30": sum(1 for x in lengths if 21 <= x <= 30),
        "very_long_31_plus": sum(1 for x in lengths if x >= 31),
    }
    shortest_i = lengths.index(min(lengths))
    longest_i = lengths.index(max(lengths))
    return {
        "count": len(lengths),
        "mean": round(statistics.mean(lengths), 2),
        "median": statistics.median(lengths),
        "stdev": round(statistics.stdev(lengths), 2) if len(lengths) > 1 else 0.0,
        "shortest": {"length": lengths[shortest_i], "text": sents[shortest_i].text.strip()},
        "longest": {"length": lengths[longest_i], "text": sents[longest_i].text.strip()},
        "buckets": buckets,
    }


# -- 2.2 Sentence openers ---------------------------------------------------

_OPENER_LABELS = [
    "pronoun_subject",
    "noun_subject",
    "transitional_connector",
    "adverbial_or_prepositional",
    "participial_or_gerund",
    "coordinating_conjunction",
    "other",
]


def _first_non_punct(sent: Span):
    for t in sent:
        if not (t.is_punct or t.is_space):
            return t
    return None


def _opener_category(sent: Span) -> tuple[str, str]:
    """Return (category, opening_snippet)."""
    tok = _first_non_punct(sent)
    if tok is None:
        return "other", ""
    snippet = sent.text.strip().split(" ")
    snippet_preview = " ".join(snippet[:4])
    lower_start = sent.text.strip().lower()

    # Check curated transitional phrases first (multiword).
    for phrase in wordlists.TRANSITIONAL_PHRASES:
        if lower_start.startswith(phrase):
            return "transitional_connector", snippet_preview
    if tok.lower_ in wordlists.TRANSITIONAL_CONNECTORS:
        return "transitional_connector", snippet_preview

    # Coordinating conjunction opener.
    if tok.lower_ in wordlists.COORDINATORS and tok.pos_ in ("CCONJ", "ADP", "ADV"):
        return "coordinating_conjunction", snippet_preview

    # Participial / gerund: present or past participle as opener.
    if tok.tag_ in ("VBG", "VBN"):
        return "participial_or_gerund", snippet_preview

    # Subject-first: pronoun.
    if tok.pos_ == "PRON" and tok.dep_ in ("nsubj", "nsubjpass", "ROOT"):
        return "pronoun_subject", snippet_preview

    # Subject-first: demonstrative determiners ("This", "These") acting as subject.
    if tok.lower_ in ("this", "that", "these", "those") and tok.dep_ in ("nsubj", "nsubjpass"):
        return "pronoun_subject", snippet_preview

    # Subject-first: noun/proper noun.
    if tok.pos_ in ("NOUN", "PROPN") and tok.dep_ in ("nsubj", "nsubjpass", "ROOT"):
        return "noun_subject", snippet_preview

    # Adverbial / prepositional opener.
    if tok.pos_ in ("ADV", "ADP", "SCONJ"):
        return "adverbial_or_prepositional", snippet_preview

    # Determiner + noun phrase as subject ("The most immediate concern").
    if tok.pos_ == "DET":
        # Walk forward to next non-DET, non-ADJ token to find head.
        for nxt in sent:
            if nxt.i <= tok.i:
                continue
            if nxt.pos_ in ("NOUN", "PROPN"):
                return "noun_subject", snippet_preview
            if nxt.pos_ not in ("ADJ", "DET", "ADV"):
                break

    return "other", snippet_preview


def analyze_sentence_openers(doc: Doc) -> dict:
    sents = [s for s in doc.sents if _sentence_word_count(s) >= 1]
    cats: list[str] = []
    examples: dict[str, list[str]] = {label: [] for label in _OPENER_LABELS}
    for sent in sents:
        cat, snippet = _opener_category(sent)
        cats.append(cat)
        if len(examples[cat]) < 3:
            examples[cat].append(snippet)
    total = len(cats) or 1
    counts = Counter(cats)
    percentages = {
        label: round(counts.get(label, 0) / total * 100, 1)
        for label in _OPENER_LABELS
    }
    ranked = sorted(
        ((label, counts.get(label, 0), percentages[label]) for label in _OPENER_LABELS),
        key=lambda x: -x[1],
    )
    return {
        "total": total,
        "counts": dict(counts),
        "percentages": percentages,
        "ranked": ranked,
        "examples": examples,
        "top_category": ranked[0][0] if ranked else None,
        "second_category": ranked[1][0] if len(ranked) > 1 else None,
    }


# -- 2.3 Coordination vs subordination --------------------------------------

def analyze_coord_subord(doc: Doc) -> dict:
    coord_clauses = 0
    coord_terms: Counter = Counter()
    sub_clauses = 0
    sub_terms: Counter = Counter()
    relative_clauses = 0
    rel_terms: Counter = Counter()

    for tok in doc:
        # Coordinating conjunction linking clauses: CCONJ with cc dep whose
        # head is a verb that has at least one VERB conjunct child.
        if tok.pos_ == "CCONJ" and tok.lower_ in wordlists.COORDINATORS:
            head = tok.head
            if head.pos_ in ("VERB", "AUX"):
                has_verb_conj = any(
                    c.dep_ == "conj" and c.pos_ in ("VERB", "AUX") for c in head.children
                )
                if has_verb_conj:
                    coord_clauses += 1
                    coord_terms[tok.lower_] += 1

        # Subordinating conjunction.
        if tok.pos_ == "SCONJ" or tok.lower_ in wordlists.SUBORDINATORS:
            # Avoid double-counting "as" / "since" when used as prepositions.
            if tok.dep_ in ("mark", "advmod") or tok.pos_ == "SCONJ":
                sub_clauses += 1
                sub_terms[tok.lower_] += 1

        # Relative clause.
        if tok.dep_ == "relcl":
            relative_clauses += 1
            # The introducing word is usually a child with WDT/WP tag.
            for child in tok.children:
                if child.tag_ in ("WDT", "WP", "WP$", "WRB"):
                    rel_terms[child.lower_] += 1
                    break

    # Comma splice heuristic: comma followed by an independent clause without
    # a coordinating conjunction. Look for sentences containing pattern
    # "..., <Pronoun/Noun> <finite verb> ..." with no CCONJ between.
    splice_count = _detect_comma_splices(doc)

    total_sub = sub_clauses + relative_clauses
    total_coord = coord_clauses
    denom = total_coord if total_coord else 1
    ratio = round(total_sub / denom, 2)

    return {
        "coord_clauses": coord_clauses,
        "coord_terms": coord_terms.most_common(),
        "subordinate_clauses": sub_clauses,
        "subordinate_terms": sub_terms.most_common(),
        "relative_clauses": relative_clauses,
        "relative_terms": rel_terms.most_common(),
        "comma_splices": splice_count,
        "subordination_to_coordination": ratio,
        "tendency": _classify_coord_subord(ratio, total_coord, total_sub),
    }


def _detect_comma_splices(doc: Doc) -> int:
    """Best-effort comma splice detection. Returns approximate count."""
    splices = 0
    for sent in doc.sents:
        toks = [t for t in sent if not t.is_space]
        for i, tok in enumerate(toks[:-2]):
            if tok.text != ",":
                continue
            nxt = toks[i + 1]
            after = toks[i + 2]
            if nxt.pos_ == "CCONJ":
                continue
            # Pattern: comma, then [PRON or NOUN/PROPN], then finite verb.
            if nxt.pos_ in ("PRON", "NOUN", "PROPN") and after.pos_ in ("VERB", "AUX"):
                if after.tag_ not in ("VBG", "VBN"):
                    splices += 1
    return splices


def _classify_coord_subord(ratio: float, coord: int, sub: int) -> str:
    if coord == 0 and sub == 0:
        return "indeterminate"
    if ratio >= 1.5:
        return "high subordination"
    if ratio >= 0.75:
        return "balanced"
    return "high coordination"


# -- 2.4 Punctuation --------------------------------------------------------

def analyze_punctuation(doc: Doc) -> dict:
    text = doc.text
    n_words = sum(1 for t in doc if t.is_alpha) or 1
    per_500 = lambda n: round((n / n_words) * 500, 2)

    semicolons = text.count(";")
    colons = text.count(":")
    em_dashes = text.count("—") + len(re.findall(r"\b--\b|(?<=\w) -- (?=\w)", text))
    parens = text.count("(")
    exclamations = text.count("!")
    questions = text.count("?")
    ellipses = text.count("...") + text.count("…")
    commas = text.count(",")

    return {
        "raw": {
            "semicolons": semicolons,
            "colons": colons,
            "em_dashes": em_dashes,
            "parentheses": parens,
            "exclamation_points": exclamations,
            "question_marks": questions,
            "ellipses": ellipses,
            "commas": commas,
        },
        "per_500": {
            "semicolons": per_500(semicolons),
            "colons": per_500(colons),
            "em_dashes": per_500(em_dashes),
            "parentheses": per_500(parens),
            "exclamation_points": per_500(exclamations),
            "question_marks": per_500(questions),
            "ellipses": per_500(ellipses),
            "commas": per_500(commas),
        },
    }


def analyze(doc: Doc) -> dict:
    return {
        "sentence_length": analyze_sentence_length(doc),
        "openers": analyze_sentence_openers(doc),
        "coord_subord": analyze_coord_subord(doc),
        "punctuation": analyze_punctuation(doc),
    }
