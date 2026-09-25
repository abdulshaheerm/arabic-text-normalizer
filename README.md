# arabic-text-normalizer

[![tests](https://github.com/abdulshaheerm/arabic-text-normalizer/actions/workflows/tests.yml/badge.svg)](https://github.com/abdulshaheerm/arabic-text-normalizer/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A small, dependency-free Python library for normalizing Arabic text before search indexing, retrieval, and NLP.

```python
from arabic_text_normalizer import normalize

normalize("إِلَى المَكْتَبَــــةِ")   # → "الي المكتبة"
```

## Features

| Step | Example | Default |
|---|---|---|
| Unify alef forms (أ إ آ ٱ → ا) | `أحمد` → `احمد` | on |
| Alef maqsura → yaa (ى → ي) | `مستشفى` → `مستشفي` | on |
| Remove diacritics (tashkeel) | `السَّلَامُ` → `السلام` | on |
| Remove tatweel (ـ) | `مكتبــــة` → `مكتبة` | on |
| Taa marbuta → haa (ة → ه) | `مدرسة` → `مدرسه` | **off** |
| Arabic/Persian digits → 0-9 | `٢٠٢٦` → `2026` | **off** |

Input is NFC-normalized first, so decomposed characters (for example ا + combining madda) are handled the same as their precomposed forms. Non-Arabic text passes through unchanged.

## Before / after

| Input | Options | Output |
|---|---|---|
| `أحمد / إسلام / آمال` | default | `احمد / اسلام / امال` |
| `مستشفى` | default | `مستشفي` |
| `السَّلَامُ عَلَيْكُمْ` | default | `السلام عليكم` |
| `مكتبــــة` | default | `مكتبة` |
| `مدرسة` | `taa_marbuta_to_haa=True` | `مدرسه` |
| `عام ٢٠٢٦ / ۱۴۰۵` | `normalize_digits=True` | `عام 2026 / 1405` |
| `إِلَى المَكْتَبَــــةِ فِي عَامِ ٢٠٢٦` | taa marbuta + digits | `الي المكتبه في عام 2026` |

## Why this matters for search

Arabic writes the same word in several ways. People often leave out the hamza (`احمد` vs. `أحمد`), write ى and ي interchangeably, stretch words with tatweel for layout, and add diacritics only sometimes. A search engine that compares raw strings treats all of these as different words, so a user typing `احمد` misses every document that says `أحمد`.

Normalizing **both documents and queries** with the same settings maps these variants to one form:

- **Better recall.** Keyword search (BM25, SQL `LIKE`, Elasticsearch) finds matches regardless of spelling variant.
- **Cleaner vocabularies.** Tokenizers and embedding models see fewer spurious variants of the same word.
- **Consistent deduplication.** Near-duplicate records and names collapse to the same key.

The trade-off is precision. More aggressive steps can merge distinct words (for example, with ة → ه some nouns become identical to words ending in a pronoun suffix). That's why taa marbuta and digit conversion are opt-in. Pick your settings once and use them for both indexing and querying.

## Install

```bash
git clone https://github.com/abdulshaheerm/arabic-text-normalizer.git
cd arabic-text-normalizer
pip install -e .
```

No runtime dependencies. Python 3.9+.

## Usage

### Python

```python
from arabic_text_normalizer import normalize, NormalizeOptions

# Defaults
normalize("السَّلَامُ عَلَيْكُمْ")            # "السلام عليكم"

# Override individual options
normalize("مدرسة", taa_marbuta_to_haa=True)   # "مدرسه"

# Or build a reusable options object
search_opts = NormalizeOptions(taa_marbuta_to_haa=True, normalize_digits=True)
normalize("المكتبة ٢٠٢٦", search_opts)        # "المكتبه 2026"
```

`NormalizeOptions` fields: `unify_alef`, `alef_maqsura_to_yaa`, `taa_marbuta_to_haa`, `remove_diacritics`, `remove_tatweel`, `normalize_digits`.

### CLI

```bash
arabic-normalize "السَّلَامُ عَلَيْكُمْ"
# السلام عليكم

arabic-normalize --taa-marbuta --digits "مدرسة ٢٠٢٦"
# مدرسه 2026

cat input.txt | arabic-normalize > normalized.txt   # line by line from stdin

python -m arabic_text_normalizer "آمال"            # also works without the script
```

Flags: `--taa-marbuta`, `--digits`, `--keep-alef`, `--keep-alef-maqsura`, `--keep-diacritics`, `--keep-tatweel`, `--version`.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Tests run on every push and pull request via GitHub Actions (Python 3.9–3.13).

## License

[MIT](LICENSE) © 2026 Abdul Saheer Mecheri
