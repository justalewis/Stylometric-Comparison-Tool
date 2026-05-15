"""Section 5: comparative summary.

Each feature comparator returns a dict:
    {"feature": str, "a": str, "b": str, "rating": str, "explanation": str}

`rating` is one of: "Strong Match", "Partial Match", "No Match", "Indeterminate".
"""

from __future__ import annotations

STRONG = "Strong Match"
PARTIAL = "Partial Match"
NO = "No Match"
INDET = "Indeterminate"


def _within_pct(a: float, b: float, pct: float) -> bool:
    """True if smaller is at least (1 - pct/100) * larger."""
    if a == 0 and b == 0:
        return True
    if a == 0 or b == 0:
        return False
    small, large = sorted((a, b))
    return small / large >= (1 - pct / 100)


def _cmp_ttr(a: dict, b: dict) -> dict:
    ta = a["lexical"]["ttr"]
    tb = b["lexical"]["ttr"]
    a_words = a["meta"]["word_count"]
    b_words = b["meta"]["word_count"]
    if a_words == 0 or b_words == 0:
        rating = INDET
        expl = "Empty text."
    elif max(a_words, b_words) / min(a_words, b_words) > 2:
        rating = INDET
        expl = "Word counts differ by more than 2x; TTR not comparable."
    else:
        diff = abs(ta["ratio"] - tb["ratio"])
        if diff <= 0.05:
            rating = STRONG
            expl = f"Ratios within {diff:.3f} of each other."
        elif diff <= 0.10:
            rating = PARTIAL
            expl = f"Ratios differ by {diff:.3f}."
        else:
            rating = NO
            expl = f"Ratios differ by {diff:.3f} (greater than 0.10)."
    return {
        "feature": "1.1 Type-Token Ratio",
        "a": f"{ta['ratio']:.3f} ({ta['types']}/{ta['tokens']})",
        "b": f"{tb['ratio']:.3f} ({tb['types']}/{tb['tokens']})",
        "rating": rating,
        "explanation": expl,
    }


def _lean(ratio: float, total_categorized: int) -> str:
    if total_categorized == 0:
        return "no categorized words"
    if ratio >= 0.60:
        return "Latinate"
    if ratio <= 0.40:
        return "Germanic"
    return "mixed"


def _cmp_latinate(a: dict, b: dict) -> dict:
    a_lg = a["lexical"]["latinate_germanic"]
    b_lg = b["lexical"]["latinate_germanic"]
    la = a_lg["latinate_ratio"]
    lb = b_lg["latinate_ratio"]
    total_a = a_lg["latinate_count"] + a_lg["germanic_count"]
    total_b = b_lg["latinate_count"] + b_lg["germanic_count"]
    lean_a, lean_b = _lean(la, total_a), _lean(lb, total_b)
    if lean_a == "no categorized words" or lean_b == "no categorized words":
        rating = INDET
        expl = "One or both texts had no categorized vocabulary."
    elif lean_a == lean_b and lean_a != "mixed":
        rating = STRONG
        expl = f"Both lean {lean_a}."
    elif lean_a == "mixed" and lean_b == "mixed":
        rating = PARTIAL
        expl = "Both texts sit in the 0.40-0.60 middle range."
    elif {lean_a, lean_b} == {"Latinate", "Germanic"}:
        rating = NO
        expl = f"Opposite leans: Text A {la:.2f} ({lean_a}); Text B {lb:.2f} ({lean_b})."
    else:
        rating = PARTIAL
        expl = f"One text leans {lean_a}, the other sits {lean_b}."
    return {
        "feature": "1.2 Latinate/Germanic",
        "a": f"{la:.2f} ({lean_a})",
        "b": f"{lb:.2f} ({lean_b})",
        "rating": rating,
        "explanation": expl,
    }


def _cmp_pet_words(a: dict, b: dict) -> dict:
    ha = a["lexical"]["pet_words"]["habitual_word_set"]
    hb = b["lexical"]["pet_words"]["habitual_word_set"]
    pa = a["lexical"]["pet_words"]["habitual_phrase_set"]
    pb = b["lexical"]["pet_words"]["habitual_phrase_set"]
    shared_words = ha & hb
    shared_phrases = pa & pb
    shared_total = len(shared_words) + len(shared_phrases)
    if not ha and not hb and not pa and not pb:
        rating = INDET
        expl = "Neither text produced habitual words or phrases."
    elif shared_total >= 2:
        rating = STRONG
        expl = (
            f"{shared_total} shared habitual markers: "
            + ", ".join(sorted(shared_words | shared_phrases)[:6])
        )
    elif shared_total == 1:
        rating = PARTIAL
        expl = f"1 shared habitual marker: {next(iter(shared_words | shared_phrases))}"
    else:
        rating = NO
        expl = "No habitual words or phrases overlap."
    return {
        "feature": "1.3 Pet Words & Phrases",
        "a": ", ".join(sorted(ha | pa)[:6]) or "(none)",
        "b": ", ".join(sorted(hb | pb)[:6]) or "(none)",
        "rating": rating,
        "explanation": expl,
    }


def _cmp_hedges(a: dict, b: dict) -> dict:
    da = a["lexical"]["hedges"]["dominant_pattern"]
    db = b["lexical"]["hedges"]["dominant_pattern"]
    if da == db:
        rating = STRONG
        expl = f"Both texts share a {da} hedge pattern."
    elif {da, db} == {"informal", "formal"}:
        rating = NO
        expl = "One text leans informal, the other formal."
    else:
        rating = PARTIAL
        expl = f"Text A pattern: {da}; Text B pattern: {db}."
    a_str = (
        f"informal {a['lexical']['hedges']['informal_per_500']}/500w, "
        f"formal {a['lexical']['hedges']['formal_per_500']}/500w ({da})"
    )
    b_str = (
        f"informal {b['lexical']['hedges']['informal_per_500']}/500w, "
        f"formal {b['lexical']['hedges']['formal_per_500']}/500w ({db})"
    )
    return {
        "feature": "1.4 Hedges/Fillers/Intensifiers",
        "a": a_str,
        "b": b_str,
        "rating": rating,
        "explanation": expl,
    }


def _cmp_sentence_length(a: dict, b: dict) -> dict:
    sa = a["syntactic"]["sentence_length"]
    sb = b["syntactic"]["sentence_length"]
    if sa["count"] == 0 or sb["count"] == 0:
        return {
            "feature": "2.1 Sentence Length",
            "a": "n/a", "b": "n/a", "rating": INDET,
            "explanation": "One or both texts had no sentences.",
        }
    mean_close = abs(sa["mean"] - sb["mean"]) <= 3
    sd_close = abs(sa["stdev"] - sb["stdev"]) <= 3
    if mean_close and sd_close:
        rating = STRONG
        expl = "Means within 3 words and SDs within 3."
    elif mean_close or sd_close:
        rating = PARTIAL
        expl = f"{'Means' if mean_close else 'SDs'} close; the other diverges."
    else:
        rating = NO
        expl = "Both means and SDs differ substantially."
    return {
        "feature": "2.1 Sentence Length",
        "a": f"mean {sa['mean']}, SD {sa['stdev']}",
        "b": f"mean {sb['mean']}, SD {sb['stdev']}",
        "rating": rating,
        "explanation": expl,
    }


def _cmp_openers(a: dict, b: dict) -> dict:
    oa = a["syntactic"]["openers"]
    ob = b["syntactic"]["openers"]
    top_a, top_b = oa["top_category"], ob["top_category"]
    second_a, second_b = oa["second_category"], ob["second_category"]
    pa = oa["percentages"]
    pb = ob["percentages"]
    if top_a == top_b:
        top_diff = abs(pa[top_a] - pb[top_b])
        second_match = second_a == second_b
        second_diff = abs(pa.get(second_a, 0) - pb.get(second_b, 0)) if second_match else 999
        if second_match and top_diff <= 15 and second_diff <= 15:
            rating = STRONG
            expl = f"Top two categories agree (top: {top_a})."
        elif top_diff <= 15:
            rating = PARTIAL
            expl = f"Top category matches ({top_a}) but secondary diverges."
        else:
            rating = PARTIAL
            expl = f"Top category matches ({top_a}) but proportions differ by {top_diff:.1f}pp."
    else:
        rating = NO
        expl = f"Top categories differ: A → {top_a}; B → {top_b}."
    return {
        "feature": "2.2 Sentence Openers",
        "a": f"{top_a} {pa.get(top_a, 0)}%, then {second_a} {pa.get(second_a, 0)}%",
        "b": f"{top_b} {pb.get(top_b, 0)}%, then {second_b} {pb.get(second_b, 0)}%",
        "rating": rating,
        "explanation": expl,
    }


def _cmp_coord_subord(a: dict, b: dict) -> dict:
    ta = a["syntactic"]["coord_subord"]["tendency"]
    tb = b["syntactic"]["coord_subord"]["tendency"]
    ra = a["syntactic"]["coord_subord"]["subordination_to_coordination"]
    rb = b["syntactic"]["coord_subord"]["subordination_to_coordination"]
    if "indeterminate" in (ta, tb):
        rating = INDET
        expl = "One text had too few clauses to classify."
    elif ta == tb:
        rating = STRONG
        expl = f"Both texts show {ta}."
    elif {ta, tb} == {"high subordination", "high coordination"}:
        rating = NO
        expl = "Opposite tendencies."
    else:
        rating = PARTIAL
        expl = f"Adjacent tendencies: A → {ta}; B → {tb}."
    return {
        "feature": "2.3 Coordination/Subordination",
        "a": f"{ta} (sub/coord = {ra})",
        "b": f"{tb} (sub/coord = {rb})",
        "rating": rating,
        "explanation": expl,
    }


def _cmp_punctuation(a: dict, b: dict) -> dict:
    pa = a["syntactic"]["punctuation"]["per_500"]
    pb = b["syntactic"]["punctuation"]["per_500"]
    matches = 0
    total_types = len(pa)
    for key in pa:
        if pa[key] == 0 and pb[key] == 0:
            matches += 1  # both absent counts as match
        elif _within_pct(pa[key], pb[key], 50):
            matches += 1
    if matches >= 5:
        rating = STRONG
    elif matches >= 3:
        rating = PARTIAL
    else:
        rating = NO
    expl = f"{matches} of {total_types} punctuation types used at similar rate."
    summary_a = ", ".join(f"{k[:4]}:{v}" for k, v in pa.items() if v > 0) or "sparse"
    summary_b = ", ".join(f"{k[:4]}:{v}" for k, v in pb.items() if v > 0) or "sparse"
    return {
        "feature": "2.4 Punctuation",
        "a": summary_a,
        "b": summary_b,
        "rating": rating,
        "explanation": expl,
    }


def _cmp_paragraph_structure(a: dict, b: dict) -> dict:
    pa = a["discourse"]["paragraph_structure"]
    pb = b["discourse"]["paragraph_structure"]
    pos_match = pa["dominant_topic_position"] == pb["dominant_topic_position"]
    length_close = abs(pa["mean_sentences"] - pb["mean_sentences"]) <= 1
    if pos_match and length_close:
        rating = STRONG
        expl = f"Both: dominant topic position {pa['dominant_topic_position']}, similar paragraph length."
    elif pos_match or length_close:
        rating = PARTIAL
        expl = "One of position/length matches, the other diverges."
    else:
        rating = NO
        expl = "Both dominant position and mean length differ."
    return {
        "feature": "3.1 Paragraph Structure",
        "a": f"{pa['paragraph_count']} pgs, mean {pa['mean_sentences']} sents, topic: {pa['dominant_topic_position']}",
        "b": f"{pb['paragraph_count']} pgs, mean {pb['mean_sentences']} sents, topic: {pb['dominant_topic_position']}",
        "rating": rating,
        "explanation": expl,
    }


def _cmp_transitions(a: dict, b: dict) -> dict:
    ta = a["discourse"]["transitions"]["dominant_strategy"]
    tb = b["discourse"]["transitions"]["dominant_strategy"]
    if "indeterminate" in (ta, tb):
        return {
            "feature": "3.2 Transitions",
            "a": ta, "b": tb, "rating": INDET,
            "explanation": "One text had fewer than 2 paragraphs.",
        }
    if ta == tb:
        rating = STRONG
        expl = f"Both texts use {ta} transitions."
    elif {ta, tb} == {"explicit_transitional", "implicit"}:
        rating = NO
        expl = "One uses explicit transitions, the other relies on implicit logical connection."
    else:
        rating = PARTIAL
        expl = f"Adjacent strategies: A → {ta}; B → {tb}."
    return {
        "feature": "3.2 Transitions",
        "a": ta,
        "b": tb,
        "rating": rating,
        "explanation": expl,
    }


def _cmp_evidence_claim(a: dict, b: dict) -> dict:
    ea = a["discourse"]["evidence_claim"]
    eb = b["discourse"]["evidence_claim"]
    pattern_match = ea["dominant_pattern"] == eb["dominant_pattern"]
    type_match = ea["primary_evidence_type"] == eb["primary_evidence_type"]
    if pattern_match and type_match:
        rating = STRONG
        expl = f"Both: {ea['dominant_pattern']} with {ea['primary_evidence_type']} evidence."
    elif pattern_match:
        rating = PARTIAL
        expl = f"Same claim/evidence pattern ({ea['dominant_pattern']}) but different evidence types."
    else:
        rating = NO
        expl = "Different claim/evidence patterns."
    return {
        "feature": "3.3 Evidence/Claim",
        "a": f"{ea['dominant_pattern']} ({ea['primary_evidence_type']})",
        "b": f"{eb['dominant_pattern']} ({eb['primary_evidence_type']})",
        "rating": rating,
        "explanation": expl,
    }


def _cmp_metadiscourse(a: dict, b: dict) -> dict:
    ma = a["discourse"]["metadiscourse"]
    mb = b["discourse"]["metadiscourse"]
    textual_close = _within_pct(ma["textual_per_500"], mb["textual_per_500"], 50)
    interpersonal_close = _within_pct(
        ma["interpersonal_per_500"], mb["interpersonal_per_500"], 50
    )
    if textual_close and interpersonal_close:
        rating = STRONG
        expl = "Both subcategory rates are within 50% of each other."
    elif textual_close or interpersonal_close:
        rating = PARTIAL
        expl = (
            "Textual rates close; interpersonal diverges."
            if textual_close
            else "Interpersonal rates close; textual diverges."
        )
    else:
        rating = NO
        expl = "Both textual and interpersonal rates diverge."
    return {
        "feature": "3.4 Metadiscourse",
        "a": f"textual {ma['textual_per_500']}/500w, interpersonal {ma['interpersonal_per_500']}/500w",
        "b": f"textual {mb['textual_per_500']}/500w, interpersonal {mb['interpersonal_per_500']}/500w",
        "rating": rating,
        "explanation": expl,
    }


_REGISTER_ORDER = ["formal", "semi-formal", "mixed", "informal"]


def _cmp_register(a: dict, b: dict) -> dict:
    ca = a["register"]["classification"]["classification"]
    cb = b["register"]["classification"]["classification"]
    ea = set(a["register"]["classification"]["evidence"])
    eb = set(b["register"]["classification"]["evidence"])
    if ca == cb and (ea & eb):
        rating = STRONG
        expl = f"Both {ca} with overlapping markers."
    elif ca == cb:
        rating = STRONG
        expl = f"Both classified as {ca}."
    else:
        try:
            ia = _REGISTER_ORDER.index(ca)
            ib = _REGISTER_ORDER.index(cb)
            distance = abs(ia - ib)
        except ValueError:
            distance = 99
        if distance == 1:
            rating = PARTIAL
            expl = f"Adjacent register categories: {ca} vs. {cb}."
        else:
            rating = NO
            expl = f"Register levels differ substantially: {ca} vs. {cb}."
    return {
        "feature": "4.1 Register",
        "a": ca,
        "b": cb,
        "rating": rating,
        "explanation": expl,
    }


def _cmp_consistency(a: dict, b: dict) -> dict:
    ka = a["register"]["consistency"]
    kb = b["register"]["consistency"]
    if "note" in ka or "note" in kb:
        return {
            "feature": "4.2 Register Consistency",
            "a": ka.get("note", "consistent"),
            "b": kb.get("note", "consistent"),
            "rating": INDET,
            "explanation": "One or both texts had insufficient paragraphs.",
        }
    if ka["consistent"] and kb["consistent"]:
        rating = STRONG
        expl = "Both texts hold register throughout."
    elif (not ka["consistent"]) and (not kb["consistent"]):
        shifts_a = [(s["from"], s["to"]) for s in ka["shifts"]]
        shifts_b = [(s["from"], s["to"]) for s in kb["shifts"]]
        if shifts_a == shifts_b:
            rating = STRONG
            expl = "Both texts shift register in matching directions."
        elif set(shifts_a) & set(shifts_b):
            rating = PARTIAL
            expl = "Both shift, partial overlap in direction."
        else:
            rating = NO
            expl = "Both shift, but in different directions."
    else:
        rating = NO
        expl = "One text is consistent; the other shifts register."
    a_summary = "consistent" if ka["consistent"] else f"shifts at pg {[s['paragraph_index'] for s in ka['shifts']]}"
    b_summary = "consistent" if kb["consistent"] else f"shifts at pg {[s['paragraph_index'] for s in kb['shifts']]}"
    return {
        "feature": "4.2 Register Consistency",
        "a": a_summary,
        "b": b_summary,
        "rating": rating,
        "explanation": expl,
    }


def _cmp_pronouns(a: dict, b: dict) -> dict:
    pa = a["register"]["pronouns"]
    pb = b["register"]["pronouns"]
    da, db = pa["dominant_category"], pb["dominant_category"]
    if da == "none" and db == "none":
        rating = STRONG
        expl = "Both texts avoid personal pronouns."
    elif da == db:
        rate_a = pa["per_500"][da]
        rate_b = pb["per_500"][db]
        if _within_pct(rate_a, rate_b, 50):
            rating = STRONG
            expl = f"Both lean on {da} pronouns at similar rates."
        else:
            rating = PARTIAL
            expl = f"Both lean {da}, but rates differ ({rate_a} vs. {rate_b} per 500w)."
    else:
        rating = NO
        expl = f"Dominant categories differ: A → {da}; B → {db}."
    return {
        "feature": "4.3 Pronoun Profile",
        "a": f"{da}: {pa['per_500'].get(da, 0)}/500w",
        "b": f"{db}: {pb['per_500'].get(db, 0)}/500w",
        "rating": rating,
        "explanation": expl,
    }


_COMPARATORS = [
    _cmp_ttr, _cmp_latinate, _cmp_pet_words, _cmp_hedges,
    _cmp_sentence_length, _cmp_openers, _cmp_coord_subord, _cmp_punctuation,
    _cmp_paragraph_structure, _cmp_transitions, _cmp_evidence_claim,
    _cmp_metadiscourse,
    _cmp_register, _cmp_consistency, _cmp_pronouns,
]


def _narrative(rows: list[dict]) -> str:
    counts = {STRONG: 0, PARTIAL: 0, NO: 0, INDET: 0}
    for r in rows:
        counts[r["rating"]] += 1
    n = len(rows)
    strong_features = [r["feature"] for r in rows if r["rating"] == STRONG]
    no_features = [r["feature"] for r in rows if r["rating"] == NO]

    parts = []
    parts.append(
        f"Across {n} features, the comparison produced "
        f"{counts[STRONG]} Strong Match, {counts[PARTIAL]} Partial Match, "
        f"{counts[NO]} No Match, and {counts[INDET]} Indeterminate ratings."
    )
    if strong_features:
        top_strong = ", ".join(s.split(" ", 1)[1] for s in strong_features[:4])
        parts.append(f"Strongest convergence: {top_strong}.")
    if no_features:
        top_no = ", ".join(s.split(" ", 1)[1] for s in no_features[:4])
        parts.append(f"Sharpest divergence: {top_no}.")
    if counts[STRONG] >= 10:
        parts.append(
            "The profiles converge across most measured dimensions; "
            "the analyst should weigh whether the divergences are topic- or genre-driven before drawing conclusions."
        )
    elif counts[NO] >= 6:
        parts.append(
            "The profiles diverge on a majority of features; the texts appear to come from different stylistic systems."
        )
    else:
        parts.append(
            "The profiles show a mixed pattern: notable convergence in some dimensions, divergence in others."
        )
    parts.append(
        "This summary reports findings only; it does not assert authorship, AI generation, or academic integrity conclusions."
    )
    return " ".join(parts)


def compare(profile_a: dict, profile_b: dict) -> dict:
    rows = [cmp(profile_a, profile_b) for cmp in _COMPARATORS]
    counts = {STRONG: 0, PARTIAL: 0, NO: 0, INDET: 0}
    for r in rows:
        counts[r["rating"]] += 1
    return {
        "rows": rows,
        "counts": counts,
        "narrative": _narrative(rows),
    }
