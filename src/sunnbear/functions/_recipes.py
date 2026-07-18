"""Declarative parameter grids: how a formula's parameter sweeps are specified.

Three small pieces compose, innermost first::

    ParamSpacing   how one axis maps grid positions to values
                   (LINEAR, or LOG2/LOG10 where the grid lives in exponent space)
        │
    ParamAxis      one swept parameter: a named grid from `start` to `stop`
        │          in steps of `step`, materialized by values() as ParamValues
        │          that carry this axis's notation (a LOG2 axis emits 2^g)
        │
    ParamRecipe    one or more axes, combined into parameter tuples by tuples():
                   - product=True  (default) -> the axes' Cartesian product
                   - product=False           -> a coupled sweep, in which the
                     axes advance together at their own resolutions and their
                     lengths need not match (see ParamRecipe._coupled_param_sweep)

A formula holds a *tuple* of recipes and its candidates are their concatenation,
so recipes are additive: anything the small grammar above cannot express is
written as one more recipe rather than as a richer axis. Every recipe's axis
names must match the formula's declared `param_names`, which is what fixes the
meaning of tuple position (`Formula._validate_recipes`).

Grid values are canonicalized on `ParamValue` construction, so they print short,
stay human-screenable, and reproduce exactly.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum
from math import lcm

from ._identity import ParamValue


# ==================================================================================================
#  ParamSpacing
# ==================================================================================================
class ParamSpacing(StrEnum):
    """How an axis's grid positions map to parameter values."""

    LINEAR = "linear"  # value = grid position
    LOG2 = "log2"  # value = 2 ** grid position
    LOG10 = "log10"  # value = 10 ** grid position


# ==================================================================================================
#  ParamAxis
# ==================================================================================================
@dataclass(frozen=True)
class ParamAxis:
    """One swept parameter: a named grid from `start` to `stop` in steps of `step`.

    For logarithmic spacings the grid lives in exponent space (e.g. LOG2 with
    ``start=0, stop=2, step=1`` yields values ``1.0, 2.0, 4.0``).
    """

    param_name: str  # name of the parameter this axis sweeps, e.g. "p1" (descriptive)
    start: float
    stop: float
    step: float
    spacing: ParamSpacing = ParamSpacing.LINEAR

    def __post_init__(self) -> None:
        """Validate that the grid is well-formed (positive step, stop not before start)."""
        if self.step <= 0.0:
            raise ValueError(f"ParamAxis step must be > 0 (got {self.step}).")
        if self.stop < self.start:
            raise ValueError(f"ParamAxis stop must be >= start (got {self.start}..{self.stop}).")

    def values(self) -> tuple[ParamValue, ...]:
        """Materialize the axis's grid as `ParamValue`s carrying this axis's notation.

        The accumulated float error in ``start + i * step`` is absorbed by
        `ParamValue` construction, which canonicalizes to 10 significant
        digits — so no separate grid rounding is needed here, and the grid is
        never empty (``stop >= start`` with ``step > 0`` gives at least one
        point, which the coupled sweep relies on).
        """
        n_points = round((self.stop - self.start) / self.step) + 1
        grid = [self.start + i * self.step for i in range(n_points)]
        if self.spacing == ParamSpacing.LOG2:
            return tuple(ParamValue.exponential(2, g) for g in grid)
        if self.spacing == ParamSpacing.LOG10:
            return tuple(ParamValue.exponential(10, g) for g in grid)
        return tuple(ParamValue.decimal(g) for g in grid)


# ==================================================================================================
#  ParamRecipe
# ==================================================================================================
@dataclass(frozen=True)
class ParamRecipe:
    """A set of axes materializing parameter tuples, as a full product or coupled.

    ``product=True`` (default): the axes span their Cartesian product.
    ``product=False``: the axes advance together along a shared axis, each at
    its own resolution (see `_coupled_param_sweep`); their lengths need not match.
    """

    axes: tuple[ParamAxis, ...]
    product: bool = True

    def param_names(self) -> tuple[str, ...]:
        """Return the axis names, in tuple position order."""
        return tuple(axis.param_name for axis in self.axes)

    # --------------------------------------------------------------------------
    #  Coupled sweep
    # --------------------------------------------------------------------------
    @staticmethod
    def _coupled_param_sweep(per_axis: list[tuple[ParamValue, ...]]) -> Iterator[tuple[ParamValue, ...]]:
        """Advance every axis together along one shared position, whatever their lengths.

        Think of each axis as occupying the interval ``[0, 1]``, divided into
        one plateau per value: an axis with ``n`` values gives plateau ``k`` the
        stretch around ``k / (n - 1)``, so consecutive plateaus meet at the
        boundaries ``(2k + 1) / (2 * (n - 1))``. A short axis therefore has few,
        widely spaced boundaries and a long axis has many closely spaced ones.

        The sweep walks the *union* of all axes' boundaries from 0 to 1,
        emitting the current value of every axis after each crossing. A 5-value
        and a 3-value axis line up like this::

            p1 (5 values):  0  |  1  |  2  |  3  |  4      boundaries: 1/8 3/8 5/8 7/8
            p2 (3 values):  0     |     1     |     2      boundaries:   1/4     3/4

            shared position:  0 --+--+--+--+--+--+-- 1
                                 1/8 | 3/8 5/8 | 7/8
                                    1/4       3/4

            emitted:  (0,0) (1,0) (1,1) (2,1) (3,1) (3,2) (4,2)

        Two properties follow, and they are the whole point: each axis steps at
        its own resolution, and no axis ever loses a value — so axis lengths
        need neither match nor be reconciled, where a fixed-count sample of the
        shared position would silently skip plateaus of the finer axis. Usually
        one coordinate steps at a time; axes whose boundaries coincide step
        together (any two even-length axes share the boundary ``1/2``).
        Equal-length axes reduce to a plain zip, and axes that each hold a
        single value yield exactly one tuple.

        The implementation is a merge walk: instead of sampling positions and
        locating each axis within them, the boundaries become a sorted event
        stream, and each event advances the axes it belongs to. Scaling every
        boundary by the least common multiple of the ``2 * (n - 1)``
        denominators turns them into plain integers, so ordering and
        coincidence are exact integer comparisons — no tolerances, and no
        rational arithmetic in the loop. (The predecessor framework, which
        established these semantics, instead sampled floats either side of each
        boundary with an absolute epsilon.) Assumes every axis holds at least
        one value, which `ParamAxis.values` guarantees.
        """
        denominators = [2 * (len(values) - 1) for values in per_axis if len(values) > 1]
        scale = lcm(*denominators) if denominators else 1
        events: list[tuple[int, int]] = []
        for axis, values in enumerate(per_axis):
            if len(values) < 2:
                continue
            per_step = scale // (2 * (len(values) - 1))
            events += [((2 * k + 1) * per_step, axis) for k in range(len(values) - 1)]
        events.sort()

        indices = [0] * len(per_axis)
        yield tuple(values[0] for values in per_axis)
        for _, coinciding in itertools.groupby(events, key=lambda event: event[0]):
            for _, axis in coinciding:
                indices[axis] += 1
            yield tuple(values[index] for values, index in zip(per_axis, indices, strict=True))

    def tuples(self) -> Iterator[tuple[ParamValue, ...]]:
        """Materialize the recipe's parameter tuples."""
        per_axis = [axis.values() for axis in self.axes]
        if self.product:
            yield from itertools.product(*per_axis)
        else:
            yield from self._coupled_param_sweep(per_axis)

    # --------------------------------------------------------------------------
    #  Single-axis conveniences
    # --------------------------------------------------------------------------
    @classmethod
    def linear(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe with a linear grid."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamSpacing.LINEAR),))

    @classmethod
    def log2(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe gridded in log2 exponent space."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamSpacing.LOG2),))

    @classmethod
    def log10(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe gridded in log10 exponent space."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamSpacing.LOG10),))
