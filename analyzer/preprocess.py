"""Text preprocessing: identify and strip quoted material before analysis.

The spec requires excluding quoted material from all lexical and syntactic
counts, while still reporting *presence* and *length* of quoted material as
a feature. We handle three quotation forms:

  1. Double-quoted spans: "..." or "..." (curly quotes)
  2. Block quotes: lines beginning with '>' or indented by 4+ spaces
  3. Long quoted blocks delimited by triple quotes (rare but possible)

Single quotes are NOT stripped because they collide with contractions (don't,
it's) and possessives. Writers occasionally use single quotes for nested or
scare quotes, but stripping them robustly is not worth the false-positive
cost.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# Curly and straight double quotes.
_DOUBLE_QUOTE_OPEN = '“"'
_DOUBLE_QUOTE_CLOSE = '”"'
_QUOTED_PATTERN = re.compile(
    r"[" + re.escape(_DOUBLE_QUOTE_OPEN) + r"]"
    r"([^" + re.escape(_DOUBLE_QUOTE_OPEN + _DOUBLE_QUOTE_CLOSE) + r"]{2,})"
    r"[" + re.escape(_DOUBLE_QUOTE_CLOSE) + r"]"
)

# Block quote: a line starting with '>' (markdown style) or 4+ leading spaces.
_BLOCK_QUOTE_LINE = re.compile(r"^(?:>\s?.*|    .+)$", re.MULTILINE)


@dataclass
class QuoteReport:
    """Summary of quoted material identified in a text."""
    stripped_text: str
    quoted_spans: list[str]
    quoted_word_count: int
    original_word_count: int

    @property
    def quoted_ratio(self) -> float:
        if self.original_word_count == 0:
            return 0.0
        return self.quoted_word_count / self.original_word_count


def _word_count(s: str) -> int:
    return len(re.findall(r"\b\w+\b", s))


def strip_quotes(text: str) -> QuoteReport:
    """Remove quoted material from text and report what was removed."""
    original_words = _word_count(text)
    spans: list[str] = []

    # Block quotes first (line-oriented).
    def _capture_block(match: re.Match[str]) -> str:
        spans.append(match.group(0))
        return ""

    without_blocks = _BLOCK_QUOTE_LINE.sub(_capture_block, text)

    # Then inline double-quoted spans.
    def _capture_inline(match: re.Match[str]) -> str:
        spans.append(match.group(1))
        return " "

    stripped = _QUOTED_PATTERN.sub(_capture_inline, without_blocks)

    # Collapse the whitespace gaps left by stripping.
    stripped = re.sub(r"[ \t]+", " ", stripped)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    stripped = stripped.strip()

    quoted_words = sum(_word_count(s) for s in spans)

    return QuoteReport(
        stripped_text=stripped,
        quoted_spans=spans,
        quoted_word_count=quoted_words,
        original_word_count=original_words,
    )


def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs on blank lines. Drops empty paragraphs."""
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if p.strip()]
