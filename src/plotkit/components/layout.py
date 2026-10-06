"""Overlap detection: data obstacles for legend placement and text collisions."""

from __future__ import annotations

import itertools

import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.collections import Collection, PathCollection
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.transforms import Bbox

_STEP_PX = 2.0  # line resampling step: finer than any legend gap


class Obstacles:
    """What a legend must not cover, in display pixels.

    Attributes
    ----------
    points
        ``(N, 2)`` densely sampled line vertices and scatter centres.
    boxes
        Bounding boxes of patches, bars, images and filled collections.
    radius
        Largest scatter-marker radius in pixels (legend boxes are padded by it).
    """

    def __init__(self, ax: Axes) -> None:
        pts: list[npt.NDArray[np.float64]] = []
        self.boxes: list[Bbox] = []
        self.radius = 0.0
        px_per_pt = ax.figure.dpi / 72
        for line in ax.lines:
            if line.get_visible() and np.size(line.get_path().vertices):
                pts.append(self._line_points(line))
        for coll in ax.collections:
            if not coll.get_visible():
                continue
            offsets = np.asarray(coll.get_offsets(), dtype=float)
            if isinstance(coll, PathCollection) and offsets.size:
                pts.append(np.asarray(coll.get_offset_transform().transform(offsets), dtype=float))
                sizes = np.asarray(coll.get_sizes(), dtype=float)
                if sizes.size:
                    self.radius = max(self.radius, float(np.sqrt(sizes.max())) / 2 * px_per_pt)
            elif isinstance(coll, Collection):
                self._add_box(coll.get_window_extent())
        for patch in ax.patches:
            if isinstance(patch, Patch) and patch.get_visible():
                self._add_box(patch.get_window_extent())
        for img in ax.images:
            if isinstance(img, AxesImage) and img.get_visible():
                self._add_box(img.get_window_extent())
        self.points = np.concatenate(pts) if pts else np.empty((0, 2))
        self.points = self.points[np.isfinite(self.points).all(axis=1)]

    def _add_box(self, box: Bbox) -> None:
        if box.width > 0 and box.height > 0:
            self.boxes.append(box)

    @staticmethod
    def _line_points(line: Line2D) -> npt.NDArray[np.float64]:
        xy = np.asarray(line.get_transform().transform(line.get_path().vertices), dtype=float)
        xy = xy[np.isfinite(xy).all(axis=1)]
        if len(xy) < 2:
            return xy
        seg = np.hypot(*np.diff(xy, axis=0).T)
        out = [xy[:1]]
        for a, b, d in zip(xy[:-1], xy[1:], seg, strict=True):
            n = max(1, int(d / _STEP_PX))
            t = np.linspace(0, 1, n + 1)[1:, None]
            out.append(a + (b - a) * t)
        return np.concatenate(out)

    def score(self, box: Bbox) -> float:
        """Overlap cost of ``box``: points covered plus 1000 per covered patch box."""
        pad = self.radius
        x0, y0, x1, y1 = box.x0 - pad, box.y0 - pad, box.x1 + pad, box.y1 + pad
        p = self.points
        inside = (p[:, 0] >= x0) & (p[:, 0] <= x1) & (p[:, 1] >= y0) & (p[:, 1] <= y1)
        hit = sum(Bbox.from_extents(x0, y0, x1, y1).overlaps(b) for b in self.boxes)
        return float(inside.sum() + 1000 * hit)


def text_overlaps(fig: Figure) -> list[tuple[str, str]]:
    """Return pairs of overlapping text elements (titles, labels, tick labels, legends).

    Layout is resolved first, so the result reflects the saved figure.
    """
    fig.draw_without_rendering()
    items: list[tuple[str, Bbox]] = []
    for i, ax in enumerate(fig.axes):
        texts = [
            (f"ax{i}.title", ax.title),
            (f"ax{i}.title_left", ax._left_title),  # type: ignore[attr-defined]
            (f"ax{i}.xlabel", ax.xaxis.label),
            (f"ax{i}.ylabel", ax.yaxis.label),
        ]
        for axis, name in ((ax.xaxis, "xtick"), (ax.yaxis, "ytick")):
            lo, hi = sorted(axis.get_view_interval())
            texts += [
                (f"ax{i}.{name}", t.label1)
                for t in axis.get_major_ticks()
                if lo <= t.get_loc() <= hi
            ]
        for name, t in texts:
            if t.get_visible() and t.get_text():
                items.append((name, t.get_window_extent()))
        leg = ax.get_legend()
        if leg is not None:
            items.append((f"ax{i}.legend", leg.get_window_extent()))
    return [(na, nb) for (na, a), (nb, b) in itertools.combinations(items, 2) if a.overlaps(b)]
