"""Core normalization logic for Arabic text."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, replace
from functools import lru_cache
from typing import Dict, Optional

__all__ = ["NormalizeOptions", "normalize", "DEFAULT_OPTIONS"]

# --- Character sets ---------------------------------------------------------

ALEF = "ا"  # ا
ALEF_VARIANTS = (
    "أ",  # أ  alef with hamza above
    "إ",  # إ  alef with hamza below
    "آ",  # آ  alef with madda above
    "ٱ",  # ٱ  alef wasla
)

TAA_MARBUTA = "ة"  # ة
HAA = "ه"  # ه

ALEF_MAQSURA = "ى"  # ى
YAA = "ي"  # ي

TATWEEL = "ـ"  # ـ


def _char_range(start: int, end: int) -> list[str]:
    return [chr(cp) for cp in range(start, end + 1)]


# Harakat, tanween, shadda, sukun, superscript alef and Quranic annotation marks.
DIACRITICS = frozenset(
    _char_range(0x064B, 0x065F)  # fathatan .. wavy hamza below
    + ["ٰ"]  # superscript (dagger) alef
    + _char_range(0x0610, 0x061A)  # Quranic honorifics / small marks
    + _char_range(0x06D6, 0x06DC)  # Quranic small high ligatures
    + _char_range(0x06DF, 0x06E4)  # Quranic small high marks
    + _char_range(0x06E7, 0x06E8)
    + _char_range(0x06EA, 0x06ED)
)

# Arabic-Indic (٠-٩) and Extended Arabic-Indic / Persian (۰-۹) digits.
ARABIC_INDIC_DIGITS = _char_range(0x0660, 0x0669)
PERSIAN_DIGITS = _char_range(0x06F0, 0x06F9)


# --- Options ----------------------------------------------------------------


@dataclass(frozen=True)
class NormalizeOptions:
    """Switches for each normalization step.

    Defaults are tuned for search: steps that are almost always safe are on,
    steps that change meaning or presentation more aggressively are off.
    """

    unify_alef: bool = True
    """أ إ آ ٱ → ا"""

    alef_maqsura_to_yaa: bool = True
    """ى → ي"""

    taa_marbuta_to_haa: bool = False
    """ة → ه (off by default: it merges some distinct words)."""

    remove_diacritics: bool = True
    """Strip tashkeel (harakat, tanween, shadda, sukun, Quranic marks)."""

    remove_tatweel: bool = True
    """Strip the kashida / tatweel stretching character ـ"""

    normalize_digits: bool = False
    """Arabic-Indic and Persian digits → 0-9."""

    def with_(self, **changes: bool) -> "NormalizeOptions":
        """Return a copy with some options changed."""
        return replace(self, **changes)


DEFAULT_OPTIONS = NormalizeOptions()


@lru_cache(maxsize=64)
def _translation_table(options: NormalizeOptions) -> Dict[int, Optional[str]]:
    table: Dict[int, Optional[str]] = {}

    if options.unify_alef:
        for ch in ALEF_VARIANTS:
            table[ord(ch)] = ALEF
    if options.alef_maqsura_to_yaa:
        table[ord(ALEF_MAQSURA)] = YAA
    if options.taa_marbuta_to_haa:
        table[ord(TAA_MARBUTA)] = HAA
    if options.remove_diacritics:
        for ch in DIACRITICS:
            table[ord(ch)] = None
    if options.remove_tatweel:
        table[ord(TATWEEL)] = None
    if options.normalize_digits:
        for i, ch in enumerate(ARABIC_INDIC_DIGITS):
            table[ord(ch)] = str(i)
        for i, ch in enumerate(PERSIAN_DIGITS):
            table[ord(ch)] = str(i)

    return table


# --- Public API -------------------------------------------------------------


def normalize(
    text: str,
    options: Optional[NormalizeOptions] = None,
    **overrides: bool,
) -> str:
    """Normalize Arabic text for search and NLP.

    Args:
        text: Input string. Non-Arabic characters pass through unchanged.
        options: A :class:`NormalizeOptions` instance. Defaults to
            :data:`DEFAULT_OPTIONS`.
        **overrides: Individual option overrides, e.g.
            ``normalize(text, taa_marbuta_to_haa=True)``.

    Returns:
        The normalized string.

    Example:
        >>> normalize("أَحْمَد")
        'احمد'
        >>> normalize("مدرسة", taa_marbuta_to_haa=True)
        'مدرسه'
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be str, got {type(text).__name__}")

    opts = options or DEFAULT_OPTIONS
    if overrides:
        opts = opts.with_(**overrides)

    # Compose first so decomposed input (e.g. ا + U+0653 madda) is treated
    # the same as its precomposed form (آ) by the steps below.
    text = unicodedata.normalize("NFC", text)
    return text.translate(_translation_table(opts))
