import io
import subprocess
import sys

from arabic_text_normalizer.cli import main


def test_cli_argument(capsys):
    assert main(["أَحْمَد"]) == 0
    assert capsys.readouterr().out == "احمد\n"


def test_cli_flags(capsys):
    main(["--taa-marbuta", "--digits", "مدرسة", "٢٠٢٦"])
    assert capsys.readouterr().out == "مدرسه 2026\n"


def test_cli_keep_flags(capsys):
    main(["--keep-alef", "--keep-diacritics", "أَحمد"])
    assert capsys.readouterr().out == "أَحمد\n"


def test_cli_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("إسلام\nمكتبــة\n"))
    main([])
    assert capsys.readouterr().out == "اسلام\nمكتبة\n"


def test_module_entry_point():
    result = subprocess.run(
        [sys.executable, "-m", "arabic_text_normalizer", "آمال"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    assert result.stdout == "امال\n"
