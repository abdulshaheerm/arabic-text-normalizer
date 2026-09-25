import pytest

from arabic_text_normalizer import DEFAULT_OPTIONS, NormalizeOptions, normalize


# --- Alef -------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("أحمد", "احمد"),
        ("إسلام", "اسلام"),
        ("آمال", "امال"),
        ("ٱلرحمن", "الرحمن"),
    ],
)
def test_unify_alef(raw, expected):
    assert normalize(raw) == expected


def test_decomposed_madda_is_unified():
    # ا + combining madda (U+0653) composes to آ under NFC, then unifies to ا
    assert normalize("آمال") == "امال"


def test_keep_alef():
    assert normalize("أحمد", unify_alef=False) == "أحمد"


# --- Alef maqsura -----------------------------------------------------------

def test_alef_maqsura_to_yaa():
    assert normalize("مستشفى") == "مستشفي"
    assert normalize("على") == "علي"


def test_keep_alef_maqsura():
    assert normalize("على", alef_maqsura_to_yaa=False) == "على"


# --- Taa marbuta ------------------------------------------------------------

def test_taa_marbuta_off_by_default():
    assert normalize("مدرسة") == "مدرسة"


def test_taa_marbuta_to_haa():
    assert normalize("مدرسة", taa_marbuta_to_haa=True) == "مدرسه"


# --- Diacritics -------------------------------------------------------------

def test_remove_diacritics():
    assert normalize("السَّلَامُ عَلَيْكُمْ") == "السلام عليكم"


def test_remove_tanween_and_dagger_alef():
    assert normalize("كتابًا") == "كتابا"
    assert normalize("هٰذا") == "هذا"


def test_keep_diacritics():
    text = "عَلَيْكُمْ"
    assert normalize(text, remove_diacritics=False) == text


# --- Tatweel ----------------------------------------------------------------

def test_remove_tatweel():
    assert normalize("مكتبــــة") == "مكتبة"
    assert normalize("جـمـيـل") == "جميل"


def test_keep_tatweel():
    assert normalize("جـميل", remove_tatweel=False) == "جـميل"


# --- Digits -----------------------------------------------------------------

def test_digits_off_by_default():
    assert normalize("٢٠٢٦") == "٢٠٢٦"


def test_arabic_indic_digits():
    assert normalize("٠١٢٣٤٥٦٧٨٩", normalize_digits=True) == "0123456789"


def test_persian_digits():
    assert normalize("۰۱۲۳۴۵۶۷۸۹", normalize_digits=True) == "0123456789"


# --- General ----------------------------------------------------------------

def test_combined_example():
    raw = "إِلَى المَكْتَبَــــةِ فِي عَامِ ٢٠٢٦"
    opts = NormalizeOptions(taa_marbuta_to_haa=True, normalize_digits=True)
    assert normalize(raw, opts) == "الي المكتبه في عام 2026"


def test_non_arabic_passthrough():
    assert normalize("Hello, world! 123") == "Hello, world! 123"


def test_mixed_text():
    assert normalize("Search: أَهْلًا") == "Search: اهلا"


def test_empty_string():
    assert normalize("") == ""


def test_idempotent():
    raw = "إِلَى المَكْتَبَــــةِ ٢٠٢٦"
    opts = NormalizeOptions(taa_marbuta_to_haa=True, normalize_digits=True)
    once = normalize(raw, opts)
    assert normalize(once, opts) == once


def test_everything_off_is_identity_for_nfc_text():
    off = NormalizeOptions(
        unify_alef=False,
        alef_maqsura_to_yaa=False,
        taa_marbuta_to_haa=False,
        remove_diacritics=False,
        remove_tatweel=False,
        normalize_digits=False,
    )
    text = "أَهْلًا بِكُمْ فِي المَدْرَسَةِ ـ ٢٠٢٦"
    assert normalize(text, off) == text


def test_overrides_do_not_mutate_defaults():
    normalize("مدرسة", taa_marbuta_to_haa=True)
    assert DEFAULT_OPTIONS.taa_marbuta_to_haa is False


def test_unknown_override_raises():
    with pytest.raises(TypeError):
        normalize("نص", not_an_option=True)


def test_non_string_raises():
    with pytest.raises(TypeError):
        normalize(123)  # type: ignore[arg-type]
