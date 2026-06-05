"""Tolerant name comparison for the carnet-vs-receipt name check.

Used to raise a human-review red flag when the client's name on the carnet does
not match the name on the receipt. Tolerant by design (ignores case, accents and
word order, and survives a misspelled token) so a doctor's typo doesn't trigger a
false alarm — only a genuinely different name does.
"""

from app.core.normalize import normalize_text

# Share of the shorter name's tokens that must appear in the other to be a match.
_MATCH_RATIO = 0.6


def _tokens(name: str | None) -> set[str]:
    norm = normalize_text(name)
    if not norm:
        return set()
    return {w for w in norm.split() if len(w) >= 2}


def names_match(a: str | None, b: str | None) -> bool:
    """True if the two names plausibly refer to the same person."""
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return True  # can't compare -> don't flag
    ratio = len(ta & tb) / min(len(ta), len(tb))
    return ratio >= _MATCH_RATIO


def names_mismatch(receipt_name: str | None, carnet_name: str | None) -> bool:
    """True only when both names exist and clearly differ (=> human review)."""
    if not receipt_name or not carnet_name:
        return False
    return not names_match(receipt_name, carnet_name)
