"""Command-line interface: ``arabic-normalize``."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .normalizer import NormalizeOptions, normalize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arabic-normalize",
        description="Normalize Arabic text for search and NLP. "
        "Reads TEXT arguments, or stdin line by line if none are given.",
    )
    parser.add_argument("text", nargs="*", help="text to normalize (default: read stdin)")

    parser.add_argument(
        "--taa-marbuta", action="store_true", help="convert ة to ه (off by default)"
    )
    parser.add_argument(
        "--digits", action="store_true", help="convert Arabic/Persian digits to 0-9"
    )
    parser.add_argument(
        "--keep-alef", action="store_true", help="do not unify أ إ آ ٱ to ا"
    )
    parser.add_argument(
        "--keep-alef-maqsura", action="store_true", help="do not convert ى to ي"
    )
    parser.add_argument(
        "--keep-diacritics", action="store_true", help="do not remove tashkeel"
    )
    parser.add_argument(
        "--keep-tatweel", action="store_true", help="do not remove tatweel (ـ)"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def options_from_args(args: argparse.Namespace) -> NormalizeOptions:
    return NormalizeOptions(
        unify_alef=not args.keep_alef,
        alef_maqsura_to_yaa=not args.keep_alef_maqsura,
        taa_marbuta_to_haa=args.taa_marbuta,
        remove_diacritics=not args.keep_diacritics,
        remove_tatweel=not args.keep_tatweel,
        normalize_digits=args.digits,
    )


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    opts = options_from_args(args)

    if args.text:
        print(normalize(" ".join(args.text), opts))
    else:
        for line in sys.stdin:
            sys.stdout.write(normalize(line, opts))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
