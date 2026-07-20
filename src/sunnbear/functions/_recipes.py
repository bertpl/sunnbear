"""Declarative parameter grids: how a formula's parameter sweeps are specified.

Three small pieces compose, innermost first::

    ParamNotation  how one axis maps grid arguments to values
        │          (DECIMAL, or POW2/POW10 where the grid lives in exponent space)
        │
    ParamAxis      one swept parameter: a named argument grid from `start` to
        │          `stop` in steps of `step`, materialized by values() through
        │          the axis's notation (a POW2 axis emits 2^g)
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

Whatever the grid produces is canonicalized on `ParamValue` construction — the
argument of the axis's notation — so values print short, stay human-screenable,
and reproduce exactly.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from math import lcm

from ._param_values import CANONICAL_DIGITS, ParamNotation, ParamValue, _canonical

# A grid endpoint or step may drift from an integer ratio by this much (relative) and still
# count as aligned — the same float slack the round() in ParamAxis.values() already tolerates.
# Derived as one decade coarser than the canonical snap, so no input whose noise the snap
# would erase anyway can fail alignment (the extra decade also covers the float error of the
# ratio computation itself).
_ALIGNMENT_TOL = 10.0 ** (1 - CANONICAL_DIGITS)


def _decimal_places(x: float) -> int:
    """Count the decimal places in `x`'s shortest round-trip form (0 for an integer).

    Uses the float's `repr` — the shortest string that round-trips — so it
    matches exactly what a `ParamValue` displays, rather than the full binary
    expansion (`0.1` reads as one place, not seventeen).
    """
    exponent = Decimal(repr(x)).normalize().as_tuple().exponent
    return -exponent if isinstance(exponent, int) and exponent < 0 else 0


# ==================================================================================================
#  ParamAxis
# ==================================================================================================
@dataclass(frozen=True)
class ParamAxis:
    """One swept parameter: a named argument grid from `start` to `stop` in steps of `step`.

    The grid lives in the notation's *argument* space — the value itself for
    DECIMAL, the exponent for POW2/POW10 — and is **inclusive of both
    endpoints**: unlike Python's half-open ``range``, ``stop`` is materialized,
    so ``start=0, stop=2, step=1`` yields three points (a POW2 axis with that
    grid yields values ``1.0, 2.0, 4.0``).
    """

    param_name: str  # name of the parameter this axis sweeps, e.g. "p1" (descriptive)
    start: float
    stop: float
    step: float
    notation: ParamNotation = ParamNotation.DECIMAL

    def __post_init__(self) -> None:
        """Validate that the grid is well-formed: positive step, ordered and aligned endpoints.

        Alignment, both forgiving float noise in the inputs — the multiple-of-step
        check within `_ALIGNMENT_TOL`, the decimal-places check by judging the
        canonicalized form of each quantity (what a `ParamValue` will display),
        not the raw float:

        - `start` and `stop` carry no more decimal places than `step`, so no grid
          value ever displays more precision than the step implies (a `0.05`
          endpoint on a `0.2` step would surface a stray second decimal). A
          single-point axis (``start == stop``) is exempt — with no spacing there
          is no step precision to honor.
        - ``(stop - start)`` is an integer multiple of `step`, so the grid lands
          exactly on `stop` rather than stopping short of the inclusive endpoint.
        """
        if self.step <= 0.0:
            raise ValueError(f"ParamAxis step must be > 0 (got {self.step}).")
        if self.stop < self.start:
            raise ValueError(f"ParamAxis stop must be >= start (got {self.start}..{self.stop}).")
        if self.start != self.stop:
            step_places = _decimal_places(_canonical(self.step))
            for name, endpoint in (("start", self.start), ("stop", self.stop)):
                if _decimal_places(_canonical(endpoint)) > step_places:
                    raise ValueError(
                        f"ParamAxis {name}={endpoint} has more decimal places than step={self.step}; "
                        "grid values would display more precision than the step implies."
                    )
        ratio = (self.stop - self.start) / self.step
        if abs(ratio - round(ratio)) > _ALIGNMENT_TOL * max(1.0, abs(ratio)):
            raise ValueError(
                f"ParamAxis (stop - start) must be an integer multiple of step "
                f"(got start={self.start}, stop={self.stop}, step={self.step}); the grid would not land on stop."
            )

    def values(self) -> tuple[ParamValue, ...]:
        """Materialize the axis's argument grid through this axis's notation.

        The accumulated float error in ``start + i * step`` is absorbed by
        `ParamValue` construction, which canonicalizes the argument to
        `CANONICAL_DIGITS` significant digits — so no separate grid rounding is
        needed here, and the grid is never empty (``stop >= start`` with
        ``step > 0`` gives at least one point, which the coupled sweep relies
        on).
        """
        n_points = round((self.stop - self.start) / self.step) + 1
        return tuple(self.notation.build_param_value(self.start + i * self.step) for i in range(n_points))


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
    def decimal(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe whose grid is the values themselves (DECIMAL notation)."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamNotation.DECIMAL),))

    @classmethod
    def pow2(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe gridded in base-2 exponent space (POW2 notation)."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamNotation.POW2),))

    @classmethod
    def pow10(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe gridded in base-10 exponent space (POW10 notation)."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamNotation.POW10),))
