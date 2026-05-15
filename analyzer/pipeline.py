"""Top-level orchestrator: load spaCy, build profiles, run comparison."""

from __future__ import annotations

from functools import lru_cache

import spacy
from spacy.language import Language

from . import lexical, syntactic, discourse, register
from .compare import compare as _compare
from .preprocess import strip_quotes, split_paragraphs, QuoteReport


_SPACY_MODEL = "en_core_web_sm"


@lru_cache(maxsize=1)
def load_nlp() -> Language:
    """Load spaCy model (cached). Disable components we don't need for speed."""
    try:
        return spacy.load(_SPACY_MODEL, disable=["ner", "lemmatizer"])
    except OSError as exc:
        raise RuntimeError(
            f"spaCy model '{_SPACY_MODEL}' is not installed. "
            f"Run: python -m spacy download {_SPACY_MODEL}"
        ) from exc


def analyze(text: str, topic: str | None = None, label: str = "Text") -> dict:
    """Produce a stylometric profile for a single text."""
    nlp = load_nlp()
    quote_report: QuoteReport = strip_quotes(text)
    stripped = quote_report.stripped_text

    paragraphs = split_paragraphs(stripped) or ([stripped] if stripped else [])
    doc = nlp(stripped) if stripped else nlp("")
    paragraph_docs = [nlp(p) for p in paragraphs]

    word_count = sum(1 for t in doc if t.is_alpha)

    lex = lexical.analyze(doc, topic)
    syn = syntactic.analyze(doc)
    dis = discourse.analyze(doc, paragraphs, paragraph_docs)
    reg = register.analyze(doc, paragraph_docs, lex, syn)

    return {
        "label": label,
        "meta": {
            "word_count": word_count,
            "paragraph_count": len(paragraphs),
            "quoted_word_count": quote_report.quoted_word_count,
            "quoted_spans": len(quote_report.quoted_spans),
            "quoted_ratio": round(quote_report.quoted_ratio, 3),
            "small_sample_warning": word_count < 250,
        },
        "lexical": lex,
        "syntactic": syn,
        "discourse": dis,
        "register": reg,
    }


def compare(text_a: str, text_b: str, topic: str | None = None) -> dict:
    """Analyze both texts and produce a comparative report."""
    profile_a = analyze(text_a, topic, label="Text A")
    profile_b = analyze(text_b, topic, label="Text B")
    comparison = _compare(profile_a, profile_b)
    return {
        "profile_a": profile_a,
        "profile_b": profile_b,
        "comparison": comparison,
        "topic": topic,
    }
