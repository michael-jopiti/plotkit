"""The only place that knows about DataFrame backends.

Everything else in plotkit receives a plain :class:`pandas.DataFrame`. polars is
never imported: its objects are recognised by duck typing, so polars stays optional.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from plotkit.exceptions import DataError


@dataclass(frozen=True)
class Normalized:
    """Plot data in internal form.

    Attributes
    ----------
    frame
        One column per role that was given (``"x"``, ``"y"``, ``"hue"``, ...),
        with a fresh ``RangeIndex``.
    labels
        Original column/series name per role, for axis and legend labels
        (``None`` when the input was unnamed).
    """

    frame: pd.DataFrame
    labels: dict[str, str | None]

    def has(self, role: str) -> bool:
        """Whether ``role`` was provided."""
        return role in self.frame.columns


class DataAdapter:
    """Convert pandas, polars (eager or lazy), mappings and array-likes to pandas."""

    @classmethod
    def to_frame(cls, data: Any) -> pd.DataFrame:
        """Convert a frame-like object to a :class:`pandas.DataFrame`.

        Accepts pandas/polars DataFrames, polars ``LazyFrame`` (collected), mappings,
        2-D arrays and objects with ``to_pandas()``.

        Raises
        ------
        DataError
            If ``data`` cannot be interpreted as a table.
        """
        if isinstance(data, pd.DataFrame):
            return data
        if isinstance(data, pd.Series):
            return data.to_frame()
        if cls._is_polars(data):
            if hasattr(data, "collect"):  # LazyFrame
                data = data.collect()
            if hasattr(data, "columns"):
                return pd.DataFrame({c: data[c].to_numpy() for c in data.columns})
            return cls.to_series(data).to_frame()
        if isinstance(data, Mapping):
            return pd.DataFrame(data)
        if hasattr(data, "to_pandas"):
            return cls.to_frame(data.to_pandas())
        arr = np.asarray(data)
        if arr.ndim == 2:
            return pd.DataFrame(arr)
        raise DataError(f"cannot convert {type(data).__name__} to a table")

    @classmethod
    def to_series(cls, obj: Any, name: str | None = None) -> pd.Series:
        """Convert a 1-D array-like (pandas/polars Series, list, ndarray) to a Series."""
        if isinstance(obj, pd.Series):
            s = obj
        elif cls._is_polars(obj):
            if hasattr(obj, "collect"):
                obj = obj.collect()
            if hasattr(obj, "columns"):
                if len(obj.columns) != 1:
                    raise DataError("expected one column, got a multi-column frame")
                obj = obj[obj.columns[0]]
            s = pd.Series(obj.to_numpy(), name=obj.name)
        else:
            arr = np.asarray(obj)
            if arr.ndim != 1:
                raise DataError(f"expected 1-D data, got {arr.ndim}-D")
            s = pd.Series(arr)
        return s if name is None else s.rename(name)

    @staticmethod
    def resolve(name: str, columns: Any) -> str:
        """Match a label like ``"Usage (%)"`` to a column, ignoring case, spaces and unit.

        Raises
        ------
        DataError
            If no single column matches; the message lists the columns.
        """
        if name in columns:
            return name

        def norm(s: Any) -> str:
            return re.sub(r"\s*\(.*?\)\s*$", "", str(s)).strip().casefold().replace(" ", "_")

        hits = [c for c in columns if norm(c) == norm(name)]
        if len(hits) == 1:
            return str(hits[0])
        raise DataError(
            f"{name!r} matches no column; columns: {list(columns)} "
            "(name the column with the x= / y= option)"
        )

    @classmethod
    def vector(cls, data: Any, name: str | None = None) -> pd.Series:
        """One 1-D column: ``data`` itself when it is 1-D, else column ``name`` of a frame.

        Raises
        ------
        DataError
            If ``data`` is a table and ``name`` is not one of its columns.
        """
        try:
            return cls.to_series(data)
        except DataError:
            frame = cls.to_frame(data)
            return frame[cls.resolve(str(name), frame.columns)]

    @classmethod
    def normalize(cls, data: Any = None, **roles: Any) -> Normalized:
        """Resolve plot roles into one normalized frame.

        Parameters
        ----------
        data
            Frame-like source for roles given as column names. May be ``None`` when
            every role is an array-like.
        **roles
            ``x=``, ``y=``, ``hue=``, ...: each ``None`` (skipped), a column name in
            ``data``, or an array-like of the same length. Arrays are matched by
            position, not by index.

        Raises
        ------
        DataError
            For a missing column, a column name without ``data``, or unequal lengths.
        """
        frame = None if data is None else cls.to_frame(data)
        cols: dict[str, pd.Series] = {}
        labels: dict[str, str | None] = {}
        for role, spec in roles.items():
            label: str | None
            if spec is None:
                continue
            if isinstance(spec, str):
                if frame is None:
                    raise DataError(f"{role}={spec!r} is a column name but no data was given")
                series, label = frame[cls.resolve(spec, frame.columns)], spec
            else:
                series = cls.to_series(spec)
                label = None if series.name is None else str(series.name)
            cols[role] = series.reset_index(drop=True)
            labels[role] = label
        lengths = {len(s) for s in cols.values()}
        if len(lengths) > 1:
            raise DataError(
                f"inputs have unequal lengths: { {r: len(s) for r, s in cols.items()} }"
            )
        return Normalized(pd.DataFrame(cols), labels)

    @staticmethod
    def _is_polars(obj: Any) -> bool:
        return type(obj).__module__.split(".")[0] == "polars"
