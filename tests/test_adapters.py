import datetime as dt
import pathlib
import subprocess
import sys

import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest

from plotkit import DataError
from plotkit.data import DataAdapter

pl = pytest.importorskip("polars")

RAW = {
    "a": [1.0, 2.5, 3.0, 4.0],
    "n": [1, None, 3, 4],
    "g": ["u", "v", "u", None],
    "t": [dt.datetime(2024, 1, d) for d in (1, 2, 3, 4)],
}


def frames():
    return {
        "pandas": pd.DataFrame(RAW),
        "polars": pl.DataFrame(RAW),
        "lazy": pl.LazyFrame(RAW),
    }


def test_frame_parity():
    ref = DataAdapter.to_frame(pd.DataFrame(RAW))
    for name in ("polars", "lazy"):
        pdt.assert_frame_equal(DataAdapter.to_frame(frames()[name]), ref, obj=name)


def test_categorical_polars_becomes_strings():
    s = pl.Series("c", ["u", "v"], dtype=pl.Categorical)
    assert list(DataAdapter.to_series(s)) == ["u", "v"]


def test_series_and_arraylikes():
    ref = pd.Series([1.0, 2.0, 3.0], name="v")
    for obj in (ref, pl.Series("v", [1.0, 2.0, 3.0]), pl.DataFrame({"v": [1.0, 2.0, 3.0]})):
        pdt.assert_series_equal(DataAdapter.to_series(obj), ref)
    pdt.assert_series_equal(DataAdapter.to_series(pl.LazyFrame({"v": [1.0, 2.0, 3.0]})), ref)
    assert list(DataAdapter.to_series([1, 2, 3])) == [1, 2, 3]
    assert list(DataAdapter.to_series(np.arange(3), name="k").index) == [0, 1, 2]
    assert DataAdapter.to_series(np.arange(3), name="k").name == "k"
    with pytest.raises(DataError):
        DataAdapter.to_series(np.zeros((2, 2)))
    with pytest.raises(DataError):
        DataAdapter.to_series(pl.DataFrame({"a": [1], "b": [2]}))


def test_other_frame_inputs():
    assert DataAdapter.to_frame({"a": [1, 2]}).shape == (2, 1)
    assert DataAdapter.to_frame(np.zeros((3, 2))).shape == (3, 2)
    assert DataAdapter.to_frame(pd.Series([1], name="s")).columns.tolist() == ["s"]
    assert DataAdapter.to_frame(pl.Series("p", [1, 2])).columns.tolist() == ["p"]

    class Duck:
        def to_pandas(self):
            return pd.DataFrame({"z": [1]})

    assert DataAdapter.to_frame(Duck()).columns.tolist() == ["z"]
    with pytest.raises(DataError):
        DataAdapter.to_frame(np.zeros(3))
    with pytest.raises(DataError):
        DataAdapter.to_frame(object())


def test_normalize_parity_and_labels():
    results = {k: DataAdapter.normalize(f, x="a", y="n", hue="g") for k, f in frames().items()}
    ref = results["pandas"]
    for r in results.values():
        pdt.assert_frame_equal(r.frame, ref.frame)
        assert r.labels == {"x": "a", "y": "n", "hue": "g"}
        assert r.has("hue") and not r.has("size")


def test_normalize_arrays_positional():
    s = pd.Series([1, 2, 3], index=[10, 20, 30], name="s")
    out = DataAdapter.normalize(x=s, y=[4, 5, 6], hue=None)
    assert out.frame.index.tolist() == [0, 1, 2]
    assert out.labels == {"x": "s", "y": None}
    out2 = DataAdapter.normalize(frames()["polars"], x="a", y=pl.Series("w", [1, 2, 3, 4]))
    assert out2.labels["y"] == "w"


def test_normalize_errors():
    with pytest.raises(DataError, match="not in data"):
        DataAdapter.normalize(pd.DataFrame(RAW), x="nope")
    with pytest.raises(DataError, match="no data"):
        DataAdapter.normalize(x="a")
    with pytest.raises(DataError, match="unequal"):
        DataAdapter.normalize(x=[1, 2], y=[1, 2, 3])


def test_polars_never_imported_for_pandas():
    code = (
        "import sys, pandas as pd\n"
        "sys.modules['polars'] = None\n"
        "from plotkit.data import DataAdapter\n"
        "n = DataAdapter.normalize(pd.DataFrame({'a': [1, 2]}), x='a')\n"
        "assert n.frame['x'].tolist() == [1, 2]\n"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_only_adapter_mentions_polars():
    src = pathlib.Path(__file__).parents[1] / "src" / "plotkit"
    for f in src.rglob("*.py"):
        if f.name == "adapter.py" or f.name == "__init__.py" and f.parent.name == "data":
            continue
        text = f.read_text()
        assert "import polars" not in text and "from polars" not in text, f
