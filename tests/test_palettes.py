import itertools

import numpy as np
import pytest
from colorspacious import cspace_convert

from plotkit import PaletteError, RegistryError
from plotkit.palettes import (
    CategoricalPalette,
    ContinuousPalette,
    DiscretePalette,
    Palette,
    get_palette,
    register_palette,
)

CVD_TYPES = ["deuteranomaly", "protanomaly", "tritanomaly"]


def simulate(colors, cvd):
    space = {"name": "sRGB1+CVD", "cvd_type": cvd, "severity": 100}
    return np.clip(cspace_convert(np.array(colors), space, "sRGB1"), 0, 1)


def lightness(colors):
    return cspace_convert(np.array(colors), "sRGB1", "CAM02-UCS")[:, 0]


def min_pairwise(colors):
    jab = cspace_convert(np.array(colors), "sRGB1", "CAM02-UCS")
    return min(np.linalg.norm(a - b) for a, b in itertools.combinations(jab, 2))


@pytest.mark.parametrize("cvd", CVD_TYPES)
@pytest.mark.parametrize("n", range(1, 9))
def test_categorical_distinguishable_under_cvd(n, cvd):
    p = CategoricalPalette(n)
    if n > 1:
        assert min_pairwise(simulate(p.colors, cvd)) > 8


@pytest.mark.parametrize("cvd", CVD_TYPES + [None])
@pytest.mark.parametrize("n", range(3, 10))
def test_discrete_distinguishable_and_monotonic(n, cvd):
    cols = DiscretePalette(n).colors
    cols = simulate(cols, cvd) if cvd else np.array(cols)
    assert min_pairwise(cols) > 6
    assert np.all(np.diff(lightness(cols)) > 0)


@pytest.mark.parametrize("src", ["cividis", "viridis"])
def test_continuous_lightness_monotonic(src):
    p = ContinuousPalette(src)
    assert p.n == 256
    assert np.all(np.diff(lightness(p.colors)) > 0)


def test_errors():
    with pytest.raises(PaletteError):
        CategoricalPalette(9)
    with pytest.raises(PaletteError):
        DiscretePalette(2)
    with pytest.raises(PaletteError):
        DiscretePalette(10)


def test_immutable_and_api():
    p = CategoricalPalette(3)
    with pytest.raises(AttributeError):
        p.name = "x"
    with pytest.raises(AttributeError):
        del p.colors
    assert p.n == 3 and p.name == "okabe-ito-3"
    assert p.to_hex() == ["#e69f00", "#56b4e9", "#009e73"]
    assert p.cmap.N == 3
    p.cmap.set_bad("red")  # copy: palette unaffected
    assert p.cmap._rgba_bad != (1.0, 0.0, 0.0, 1.0)
    assert p.show().axes
    assert "n=3" in repr(p)


def test_registry():
    assert get_palette("categorical", 4).n == 4
    assert get_palette("discrete").n == 5
    assert isinstance(get_palette("continuous"), ContinuousPalette)
    with pytest.raises(RegistryError):
        get_palette("nope")
    with pytest.raises(RegistryError):
        register_palette("categorical", lambda n: CategoricalPalette())

    @register_palette("mine")
    def mine(n):
        return CategoricalPalette(2)

    assert isinstance(get_palette("mine"), Palette)
