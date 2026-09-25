"""arabic-text-normalizer: normalize Arabic text for search and NLP."""

from .normalizer import DEFAULT_OPTIONS, NormalizeOptions, normalize

__all__ = ["normalize", "NormalizeOptions", "DEFAULT_OPTIONS"]
__version__ = "0.1.0"
