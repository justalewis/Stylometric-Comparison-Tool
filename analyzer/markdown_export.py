"""Render a comparison result as a Markdown report."""

from __future__ import annotations

from io import StringIO


def _section_meta(p: dict, out: StringIO) -> None:
    m = p["meta"]
    out.write(f"- Word count: {m['word_count']}\n")
    out.write(f"- Paragraphs: {m['paragraph_count']}\n")
    if m["quoted_spans"]:
        out.write(
            f"- Quoted material removed: {m['quoted_spans']} spans, "
            f"{m['quoted_word_count']} words ({m['quoted_ratio']*100:.1f}% of original)\n"
        )
    if m["small_sample_warning"]:
        out.write("- ⚠ Sample below 250 words; results may be unreliable\n")
    out.write("\n")


def _section_lexical(p: dict, out: StringIO) -> None:
    out.write("### Lexical\n\n")
    ttr = p["lexical"]["ttr"]
    out.write(f"- **TTR**: {ttr['ratio']:.3f} ({ttr['types']} types / {ttr['tokens']} tokens)\n")
    lg = p["lexical"]["latinate_germanic"]
    out.write(
        f"- **Latinate/Germanic**: {lg['latinate_ratio']:.2f} "
        f"({lg['latinate_count']} Latinate / {lg['germanic_count']} Germanic)\n"
    )
    pw = p["lexical"]["pet_words"]
    habitual = ", ".join(f"{w} ({c})" for w, c, _ in pw["habitual_words"][:8]) or "(none)"
    phrases = ", ".join(f"\"{p_}\" ({c})" for p_, c, _ in pw["habitual_phrases"][:5]) or "(none)"
    out.write(f"- **Habitual words**: {habitual}\n")
    out.write(f"- **Habitual phrases**: {phrases}\n")
    h = p["lexical"]["hedges"]
    out.write(
        f"- **Hedges/Fillers**: informal {h['informal_per_500']}/500w, "
        f"intensifiers {h['intensifier_per_500']}/500w, "
        f"formal {h['formal_per_500']}/500w → dominant: {h['dominant_pattern']}\n"
    )
    out.write("\n")


def _section_syntactic(p: dict, out: StringIO) -> None:
    out.write("### Syntactic\n\n")
    sl = p["syntactic"]["sentence_length"]
    out.write(
        f"- **Sentence length**: {sl['count']} sentences, mean {sl['mean']}, "
        f"median {sl['median']}, SD {sl['stdev']}\n"
    )
    if sl.get("shortest"):
        out.write(
            f"  - Shortest ({sl['shortest']['length']}w): \"{sl['shortest']['text'][:140]}\"\n"
        )
    if sl.get("longest"):
        out.write(
            f"  - Longest ({sl['longest']['length']}w): \"{sl['longest']['text'][:140]}\"\n"
        )
    op = p["syntactic"]["openers"]
    out.write("- **Sentence openers** (top categories):\n")
    for label, count, pct in op["ranked"][:4]:
        out.write(f"  - {label}: {count} ({pct}%)\n")
    cs = p["syntactic"]["coord_subord"]
    out.write(
        f"- **Coordination/Subordination**: {cs['tendency']} "
        f"(sub/coord ratio {cs['subordination_to_coordination']}, "
        f"comma splices: {cs['comma_splices']})\n"
    )
    pu = p["syntactic"]["punctuation"]["per_500"]
    punct_summary = ", ".join(f"{k} {v}" for k, v in pu.items() if v > 0) or "(sparse)"
    out.write(f"- **Punctuation per 500w**: {punct_summary}\n\n")


def _section_discourse(p: dict, out: StringIO) -> None:
    out.write("### Discourse\n\n")
    ps = p["discourse"]["paragraph_structure"]
    out.write(
        f"- **Paragraphs**: {ps['paragraph_count']}, "
        f"mean {ps['mean_sentences']} sentences, "
        f"range {ps['min_sentences']}–{ps['max_sentences']}\n"
    )
    out.write(
        f"  - Dominant topic-sentence position: {ps['dominant_topic_position']} "
        f"(heuristic estimate)\n"
    )
    tr = p["discourse"]["transitions"]
    out.write(f"- **Transition strategy**: {tr['dominant_strategy']}\n")
    ec = p["discourse"]["evidence_claim"]
    out.write(
        f"- **Evidence/Claim**: {ec['dominant_pattern']}, "
        f"primary evidence type: {ec['primary_evidence_type']}\n"
    )
    md = p["discourse"]["metadiscourse"]
    out.write(
        f"- **Metadiscourse**: textual {md['textual_per_500']}/500w, "
        f"interpersonal {md['interpersonal_per_500']}/500w\n\n"
    )


def _section_register(p: dict, out: StringIO) -> None:
    out.write("### Register\n\n")
    cl = p["register"]["classification"]
    out.write(f"- **Classification**: {cl['classification']}\n")
    if cl["evidence"]:
        out.write(f"  - Markers: {'; '.join(cl['evidence'])}\n")
    cons = p["register"]["consistency"]
    if "note" in cons:
        out.write(f"- **Consistency**: {cons['note']}\n")
    elif cons["consistent"]:
        out.write("- **Consistency**: stable throughout\n")
    else:
        for s in cons["shifts"]:
            out.write(f"  - Shift at paragraph {s['paragraph_index']+1}: {s['from']} → {s['to']}\n")
    pr = p["register"]["pronouns"]
    pron_summary = ", ".join(f"{k}: {v}" for k, v in pr["per_500"].items() if v > 0) or "(none)"
    out.write(f"- **Pronouns per 500w**: {pron_summary}\n")
    out.write(f"  - Dominant category: {pr['dominant_category']}\n\n")


def render_markdown(result: dict) -> str:
    """Render the full comparison result as Markdown."""
    out = StringIO()
    out.write("# Stylometric Comparison Report\n\n")
    if result.get("topic"):
        out.write(f"**Topic hint:** {result['topic']}\n\n")

    out.write("## Text A Profile\n\n")
    _section_meta(result["profile_a"], out)
    _section_lexical(result["profile_a"], out)
    _section_syntactic(result["profile_a"], out)
    _section_discourse(result["profile_a"], out)
    _section_register(result["profile_a"], out)

    out.write("## Text B Profile\n\n")
    _section_meta(result["profile_b"], out)
    _section_lexical(result["profile_b"], out)
    _section_syntactic(result["profile_b"], out)
    _section_discourse(result["profile_b"], out)
    _section_register(result["profile_b"], out)

    out.write("## Comparative Summary\n\n")
    out.write("| Feature | Text A | Text B | Rating | Explanation |\n")
    out.write("|---|---|---|---|---|\n")
    for row in result["comparison"]["rows"]:
        a = row["a"].replace("|", "\\|")
        b = row["b"].replace("|", "\\|")
        expl = row["explanation"].replace("|", "\\|")
        out.write(
            f"| {row['feature']} | {a} | {b} | **{row['rating']}** | {expl} |\n"
        )
    out.write("\n")

    counts = result["comparison"]["counts"]
    out.write("### Tallies\n\n")
    for k, v in counts.items():
        out.write(f"- {k}: {v}\n")
    out.write("\n### Narrative\n\n")
    out.write(result["comparison"]["narrative"])
    out.write("\n")
    return out.getvalue()
