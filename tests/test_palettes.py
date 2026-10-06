import pytest

from plotkit import PaletteError, RegistryError
from plotkit.palettes import (
    CategoricalPalette,
    ContinuousPalette,
    DiscretePalette,
    Palette,
    get_palette,
    register_palette,
)
from tests.cvd import lightness_monotonic, min_delta_e


@pytest.mark.parametrize("n", range(2, 9))
def test_categorical_distinguishable_under_cvd(n):
    assert min_delta_e(CategoricalPalette(n).to_hex()) > 8


@pytest.mark.parametrize("n", range(3, 10))
def test_discrete_distinguishable_and_monotonic(n):
    hexes = DiscretePalette(n).to_hex()
    assert min_delta_e(hexes) > 6
    assert lightness_monotonic(hexes)


@pytest.mark.parametrize("src", ["cividis", "viridis"])
def test_continuous_lightness_monotonic(src):
    p = ContinuousPalette(src)
    assert p.n == 256
    assert lightness_monotonic(p.to_hex()[::8])


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
