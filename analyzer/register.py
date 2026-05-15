"""Section 4: register and stance.

  4.1 Overall register classification
  4.2 Register consistency
  4.3 Pronoun profile
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from spacy.tokens import Doc

from . import wordlists


# -- 4.3 Pronoun profile (computed first; informs 4.1) ---------------------

def analyze_pronouns(doc: Doc) -> dict:
    tokens = [t.lower_ for t in doc if t.is_alpha]
    n_words = len(tokens) or 1
    per_500 = lambda n: round((n / n_words) * 500, 2)

    first_sg = sum(1 for t in tokens if t in wordlists.PRONOUNS_FIRST_SG)
    first_pl = sum(1 for t in tokens if t in wordlists.PRONOUNS_FIRST_PL)
    second = sum(1 for t in tokens if t in wordlists.PRONOUNS_SECOND)
    third = sum(1 for t in tokens if t in wordlists.PRONOUNS_THIRD)
    impersonal_one = sum(
        1 for t in doc
        if t.is_alpha and t.lower_ in wordlists.PRONOUNS_IMPERSONAL_ONE
        and t.pos_ == "PRON"
    )
    # Existential "there" / expletive "it" require POS context.
    existential_there = sum(
        1 for t in doc
        if t.lower_ == "there" and t.dep_ in ("expl",)
    )
    expletive_it = sum(
        1 for t in doc
        if t.lower_ == "it" and t.dep_ == "expl"
    )

    counts = {
        "first_singular": first_sg,
        "first_plural": first_pl,
        "second": second,
        "third": third,
        "impersonal_one": impersonal_one,
        "existential_there": existential_there,
        "expletive_it": expletive_it,
    }
    rates = {k: per_500(v) for k, v in counts.items()}
    # Dominant: categories considered (exclude impersonal/existential/expletive).
    main = {k: v for k, v in counts.items()
            if k in ("first_singular", "first_plural", "second", "third")}
    if not any(main.values()):
        dominant = "none"
    else:
        dominant = max(main, key=main.get)

    return {
        "counts": counts,
        "per_500": rates,
        "dominant_category": dominant,
    }


# -- 4.1 Register classification --------------------------------------------

_CONTRACTION_PATTERN = re.compile(
    r"\b(?:don't|doesn't|didn't|won't|wouldn't|shouldn't|couldn't|can't|"
    r"isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't|"
    r"i'm|i've|i'll|i'd|you're|you've|you'll|you'd|"
    r"he's|she's|it's|we're|we've|we'll|we'd|they're|they've|they'll|they'd|"
    r"that's|there's|here's|what's|who's|let's)\b",
    re.IGNORECASE,
)


def _register_features(
    doc: Doc,
    lexical: dict,
    syntactic: dict,
    pronouns: dict,
) -> dict:
    """Pull the markers used to classify register."""
    text = doc.text
    contractions = len(_CONTRACTION_PATTERN.findall(text))
    n_words = sum(1 for t in doc if t.is_alpha) or 1
    return {
        "contractions": contractions,
        "contractions_per_500": round(contractions / n_words * 500, 2),
        "first_person_singular_per_500": pronouns["per_500"]["first_singular"],
        "second_person_per_500": pronouns["per_500"]["second"],
        "informal_hedges_per_500": lexical["hedges"]["informal_per_500"],
        "formal_hedges_per_500": lexical["hedges"]["formal_per_500"],
        "latinate_ratio": lexical["latinate_germanic"]["latinate_ratio"],
        "exclamation_per_500": syntactic["punctuation"]["per_500"]["exclamation_points"],
        "question_per_500": syntactic["punctuation"]["per_500"]["question_marks"],
        "subord_ratio": syntactic["coord_subord"]["subordination_to_coordination"],
    }


def _classify(feat: dict) -> tuple[str, list[str]]:
    """Return (register_label, list_of_supporting_markers)."""
    score_formal = 0
    score_informal = 0
    evidence: list[str] = []

    if feat["contractions_per_500"] <= 0.1:
        score_formal += 1
        evidence.append("no contractions")
    elif feat["contractions_per_500"] >= 2:
        score_informal += 1
        evidence.append(f"frequent contractions ({feat['contractions_per_500']}/500w)")

    if feat["first_person_singular_per_500"] >= 8:
        score_informal += 1
        evidence.append(f"heavy first-person-singular ({feat['first_person_singular_per_500']}/500w)")
    elif feat["first_person_singular_per_500"] == 0:
        score_formal += 1
        evidence.append("no first-person-singular")

    if feat["second_person_per_500"] >= 2:
        score_informal += 1
        evidence.append(f"second-person address ({feat['second_person_per_500']}/500w)")
    elif feat["second_person_per_500"] == 0:
        score_formal += 1
        evidence.append("no second-person")

    if feat["informal_hedges_per_500"] >= 4:
        score_informal += 1
        evidence.append(f"informal hedges ({feat['informal_hedges_per_500']}/500w)")
    if feat["formal_hedges_per_500"] >= 1.5:
        score_formal += 1
        evidence.append(f"formal hedges ({feat['formal_hedges_per_500']}/500w)")

    if feat["latinate_ratio"] >= 0.60:
        score_formal += 1
        evidence.append(f"Latinate-leaning vocabulary ({feat['latinate_ratio']:.2f})")
    elif feat["latinate_ratio"] <= 0.40 and feat["latinate_ratio"] > 0:
        score_informal += 1
        evidence.append(f"Germanic-leaning vocabulary ({feat['latinate_ratio']:.2f})")

    if feat["exclamation_per_500"] >= 0.5:
        score_informal += 1
        evidence.append("exclamation points present")
    if feat["question_per_500"] >= 1:
        score_informal += 1
        evidence.append("rhetorical questions present")

    diff = score_formal - score_informal
    if diff >= 3:
        return "formal", evidence
    if diff >= 1:
        return "semi-formal", evidence
    if diff <= -3:
        return "informal", evidence
    if diff <= -1:
        return "semi-formal", evidence  # leaning informal but moderate
    return "mixed", evidence


def analyze_register_classification(
    doc: Doc, lexical: dict, syntactic: dict, pronouns: dict
) -> dict:
    feat = _register_features(doc, lexical, syntactic, pronouns)
    label, evidence = _classify(feat)
    return {
        "classification": label,
        "evidence": evidence,
        "feature_summary": feat,
    }


# -- 4.2 Register consistency -----------------------------------------------

def _paragraph_register(p_doc: Doc) -> str:
    """Lightweight per-paragraph register classification."""
    n_words = sum(1 for t in p_doc if t.is_alpha) or 1
    text = p_doc.text
    contractions = len(_CONTRACTION_PATTERN.findall(text)) / n_words * 500
    pron_1sg = sum(1 for t in p_doc if t.is_alpha and t.lower_ in wordlists.PRONOUNS_FIRST_SG) / n_words * 500
    pron_2 = sum(1 for t in p_doc if t.is_alpha and t.lower_ in wordlists.PRONOUNS_SECOND) / n_words * 500
    informal_hits = sum(1 for t in p_doc if t.lower_ in wordlists.INFORMAL_HEDGES_SINGLE)
    informal_per_500 = informal_hits / n_words * 500
    exclam = text.count("!") / n_words * 500

    informal_score = (
        (contractions >= 2) + (pron_1sg >= 8) + (pron_2 >= 2)
        + (informal_per_500 >= 4) + (exclam >= 0.5)
    )
    formal_score = (
        (contractions <= 0.1) + (pron_1sg == 0) + (pron_2 == 0)
    )
    if informal_score >= 3:
        return "informal"
    if formal_score >= 2 and informal_score == 0:
        return "formal"
    return "semi-formal"


def analyze_register_consistency(paragraph_docs: list[Doc]) -> dict:
    if len(paragraph_docs) < 2:
        return {
            "consistent": True,
            "paragraph_classifications": [],
            "shifts": [],
            "note": "Fewer than 2 paragraphs; consistency undefined.",
        }
    classifications = [_paragraph_register(p) for p in paragraph_docs]
    counter = Counter(classifications)
    consistent = len(counter) == 1
    shifts: list[dict[str, Any]] = []
    if not consistent:
        for i in range(1, len(classifications)):
            if classifications[i] != classifications[i - 1]:
                shifts.append({
                    "paragraph_index": i,  # 0-based
                    "from": classifications[i - 1],
                    "to": classifications[i],
                })
    return {
        "consistent": consistent,
        "paragraph_classifications": classifications,
        "shifts": shifts,
    }


def analyze(
    doc: Doc,
    paragraph_docs: list[Doc],
    lexical: dict,
    syntactic: dict,
) -> dict:
    pronouns = analyze_pronouns(doc)
    classification = analyze_register_classification(doc, lexical, syntactic, pronouns)
    consistency = analyze_register_consistency(paragraph_docs)
    return {
        "classification": classification,
        "consistency": consistency,
        "pronouns": pronouns,
    }
