import json

import pytest

import plotkit.web


@pytest.mark.parametrize("name", ["editorial", "cobalt"])
def test_export_bakes_the_style_into_the_script(tmp_path, name):
    out = plotkit.web.export(tmp_path / "site", name)
    src = out.read_text()
    assert "const plotkit" in src
    baked = json.loads(src.split("plotkit.style = ")[1].rstrip().rstrip(";"))
    assert baked == plotkit.web.style(name)
    assert baked["bg"] == plotkit.themes.get_variant(name).bg
    assert len(baked["dashes"]) == len(plotkit.plots.line.STYLES)
