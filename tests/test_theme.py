import subprocess
import sys

import matplotlib as mpl
import pytest

from plotkit import ThemeError
from plotkit.themes import PublicationTheme, Theme, apply, get_theme, register_theme, reset


def test_import_does_not_mutate_rcparams():
    code = (
        "import matplotlib as m; before = dict(m.rcParams); import plotkit, plotkit.themes;"
        "assert dict(m.rcParams) == before"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_rc_contract():
    rc = PublicationTheme().rc_params()
    assert rc["figure.facecolor"] == "white" and rc["axes.facecolor"] == "white"
    assert rc["font.family"] == "sans-serif"
    assert rc["mathtext.fontset"] == "cm"
    assert rc["axes.spines.top"] is False and rc["axes.spines.right"] is False
    assert rc["xtick.direction"] == "out" and rc["axes.grid"] is False
    assert rc["pdf.fonttype"] == 42
    assert rc["savefig.dpi"] >= 300
    assert "text.usetex" not in rc


def test_context_restores():
    before = dict(mpl.rcParams)
    with PublicationTheme().context():
        assert mpl.rcParams["axes.spines.top"] is False
    assert dict(mpl.rcParams) == before


def test_apply_reset_roundtrip():
    before = dict(mpl.rcParams)
    prev = apply("publication")
    assert mpl.rcParams["mathtext.fontset"] == "cm"
    reset(prev)
    assert dict(mpl.rcParams) == before
    apply(PublicationTheme())
    reset()
    assert mpl.rcParams["axes.spines.top"] is True


def test_usetex_missing(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    with pytest.raises(ThemeError, match="TeX"):
        PublicationTheme(usetex=True)


def test_usetex_rc(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: "/bin/x")
    rc = PublicationTheme(usetex=True).rc_params()
    assert rc["text.usetex"] and "sansmath" in rc["text.latex.preamble"]


def test_register_theme():
    @register_theme("dark-ish")
    class Mine(Theme):
        def rc_params(self):
            return {"axes.facecolor": "0.9"}

    with get_theme("dark-ish").context():
        assert mpl.rcParams["axes.facecolor"] == "0.9"
