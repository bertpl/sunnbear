"""A parameter recipe specifies a formula's parameter tuples, as a grid or as a table.

A `ParamRecipe` materializes parameter tuples, and comes in 2 kinds:

- **`ParamGrid`** sweeps a grid. A grid composes 3 small pieces, innermost first::

      ParamNotation  how one axis maps grid arguments to values
          │          (DECIMAL, or a power notation, whose grid arguments are exponents)
          │
      ParamAxis      one swept parameter: a named argument grid from `start` to
          │          `stop` in steps of `step`, materialized by values() through
          │          the axis's notation (a POW2 axis emits 2^g), and optionally
          │          rounded to integers (ParamRounding)
          │
      ParamGrid      one or more axes, combined into parameter tuples by tuples():
                     - product=True  (default) -> the axes' Cartesian product
                     - product=False           -> a coupled sweep, in which the
                       axes advance together at their own resolutions and their
                       lengths need not match (see ParamGrid._coupled_param_sweep)

- **`ParamTable`** lists its tuples one by one, for parameter values that form no grid, such as a paper's
  published values.

A formula holds a *tuple* of recipes and its candidates are their concatenation,
so recipes are additive: anything the small grammar above cannot express is
written as one more recipe, not as a richer axis. Every recipe's parameter
names must match the names of the formula's declared `params`, which is what fixes the
meaning of tuple position (`Formula._validate_recipes`).

When an axis's notation builds each grid value (`ParamNotation.build_value_from_argument`),
it rounds the notation's argument to `CANONICAL_DIGITS` significant digits, so values print
short, are easy for a person to scan, and reproduce exactly.
"""

import itertools
import math
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from fractions import Fraction
from typing import NamedTuple, assert_never

from .param_values import CANONICAL_DIGITS, ParamNotation, _round_argument

# A grid endpoint or step may drift from an integer ratio by this much (relative) and still
# count as aligned — the same float slack the round() in ParamAxis.values() already tolerates.
# Derived as one decade coarser than the canonical snap, so no input whose noise the snap
# would erase anyway can fail alignment (the extra decade also covers the float error of the
# ratio computation itself).
_ALIGNMENT_TOL = 10.0 ** (1 - CANONICAL_DIGITS)


def _decimal_places(x: float) -> int:
    """Count the decimal places in `x`'s shortest round-trip form (0 for an integer).

    Uses the float's `repr` — the shortest string that round-trips — so it
    matches exactly how a spelling writes the argument, not the full binary
    expansion (`0.1` reads as one place, not seventeen).
    """
    exponent = Decimal(repr(x)).normalize().as_tuple().exponent
    return -exponent if isinstance(exponent, int) and exponent < 0 else 0


# ==================================================================================================
#  ParamRounding
# ==================================================================================================
class ParamRounding(StrEnum):
    """`ParamRounding` is a way for a `ParamAxis` to round each of its notation's values to an integer.

    An axis on a logarithmic scale for a parameter that must be an integer, such as a polynomial's degree, rounds its
    values this way. A value halfway between 2 integers of the kind goes to the larger one, so the nearest odd integer
    of 10 is 11.
    """

    NEAREST_INTEGER = "nearest_integer"
    NEAREST_ODD_INTEGER = "nearest_odd_integer"
    NEAREST_EVEN_INTEGER = "nearest_even_integer"

    def round_value(self, value: float) -> float:
        """Return the integer of this kind nearest `value`, the larger one on a tie, as a float."""
        match self:
            case ParamRounding.NEAREST_INTEGER:
                return float(math.floor(value + 0.5))
            case ParamRounding.NEAREST_ODD_INTEGER:
                # an odd integer is 2*k + 1, so round (value - 1)/2 to the nearest k
                return float(2 * math.floor((value - 1.0) / 2.0 + 0.5) + 1)
            case ParamRounding.NEAREST_EVEN_INTEGER:
                return float(2 * math.floor(value / 2.0 + 0.5))
            case _:
                assert_never(self)


# ==================================================================================================
#  ValuePositionRange
# ==================================================================================================
class ValuePositionRange(NamedTuple):
    """`ValuePositionRange` is 1 value of a `ParamAxis` with the part of ``[0, 1]`` in which it applies.

    `ParamAxis.value_position_ranges` explains the positions.
    """

    value: float
    position_start: Fraction
    position_stop: Fraction


# ==================================================================================================
#  ParamAxis
# ==================================================================================================
@dataclass(frozen=True)
class ParamAxis:
    """One swept parameter: a named argument grid from `start` to `stop` in steps of `step`.

    The grid lives in the notation's *argument* space — the value itself for
    DECIMAL, the exponent for a power notation — and is **inclusive of both
    endpoints**: unlike Python's half-open ``range``, ``stop`` is materialized,
    so ``start=0, stop=2, step=1`` yields three points (a POW2 axis with that
    grid yields values ``1.0, 2.0, 4.0``).

    An axis with a `rounding` rounds each of its notation's values to an integer, so several grid points can give
    the same value; the axis yields each value once.
    """

    param_name: str  # name of the parameter this axis sweeps, e.g. "p1" (descriptive)
    start: float
    stop: float
    step: float
    notation: ParamNotation = ParamNotation.DECIMAL
    rounding: ParamRounding | None = None

    def __post_init__(self) -> None:
        """Validate that the grid is well-formed: positive step, ordered and aligned endpoints.

        Alignment, both forgiving float noise in the inputs — the multiple-of-step
        check within `_ALIGNMENT_TOL`, the decimal-places check by judging the
        rounded form of each quantity (the argument as a spelling writes it, e.g. the ``1.2`` of ``2^1.2``),
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
            step_places = _decimal_places(_round_argument(self.step))
            for name, endpoint in (("start", self.start), ("stop", self.stop)):
                if _decimal_places(_round_argument(endpoint)) > step_places:
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

    def values(self) -> tuple[float, ...]:
        """Return the axis's values in grid order, each value once."""
        # rounding never reverses the order of the grid values, so a repeated value sits next to the value that it
        # repeats
        return tuple(value for value, _ in itertools.groupby(self._values_per_grid_point()))

    def value_position_ranges(self) -> tuple[ValuePositionRange, ...]:
        """Return each value of `values` with the part of ``[0, 1]`` in which it applies, for a coupled sweep.

        The grid points sit evenly on ``[0, 1]``: point ``k`` of ``n`` at ``k / (n - 1)``, so a point's position is
        linear in its grid argument, which for a power notation is the exponent.

        Each point applies from the midpoint between it and its lower neighbor to the midpoint between it and its upper
        neighbor, and the first and last points reach 0 and 1; a single-point axis applies on all of ``[0, 1]``.

        A 5-point and a 3-point axis divide ``[0, 1]`` like this::

            p1 (5 points):  0  |  1  |  2  |  3  |  4      boundaries: 1/8 3/8 5/8 7/8
            p2 (3 points):  0     |     1     |     2      boundaries:   1/4     3/4

        When several grid points round to the same value, that value applies across their parts together, so the axis
        has a boundary only where its value changes. The positions are exact fractions.
        """
        values_per_grid_point = self._values_per_grid_point()
        n_points = len(values_per_grid_point)
        # the edges of the points' parts: 0, the midpoints between neighboring points, and 1
        edges = [Fraction(0), *(Fraction(2 * k + 1, 2 * (n_points - 1)) for k in range(n_points - 1)), Fraction(1)]
        value_position_ranges = []
        i_first = 0
        for value, group in itertools.groupby(values_per_grid_point):
            i_next = i_first + len(list(group))
            value_position_ranges.append(ValuePositionRange(value, edges[i_first], edges[i_next]))
            i_first = i_next
        return tuple(value_position_ranges)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _values_per_grid_point(self) -> tuple[float, ...]:
        """Return 1 value per grid point, repeated values included: the notation's value of each argument, rounded.

        The axis's `rounding` rounds each value, if the axis has one.

        The accumulated float error in ``start + i * step`` is removed by
        `ParamNotation.build_value_from_argument`, which rounds the argument to
        `CANONICAL_DIGITS` significant digits — so no separate grid rounding is
        needed here, and the grid is never empty (``stop >= start`` with
        ``step > 0`` gives at least one point, which the coupled sweep relies
        on).
        """
        n_points = round((self.stop - self.start) / self.step) + 1
        values = [self.notation.build_value_from_argument(self.start + i * self.step) for i in range(n_points)]
        if self.rounding is None:
            return tuple(values)
        else:
            return tuple(self.rounding.round_value(value) for value in values)


# ==================================================================================================
#  ParamRecipe
# ==================================================================================================
@dataclass(frozen=True, kw_only=True)
class ParamRecipe(ABC):
    r"""`ParamRecipe` is the base class of a recipe that materializes parameter tuples: a grid or a table.

    Attributes:
        summary: One sentence for a reader on what the recipe covers, such as "The sweep of $\param{b}$ at
            $\param{d} = 1$.". The sentence is a text for a reader in sunnbear's LaTeX notation (`presentation`),
            with its math as ``$…$`` inline and ``$$…$$`` for display. None by default; the catalog's tests require it
            of every recipe of a shipped formula.
    """

    summary: str | None = None

    @abstractmethod
    def param_names(self) -> tuple[str, ...]:
        """Return the names of the recipe's parameters, in tuple position order."""

    @abstractmethod
    def tuples(self) -> Iterator[tuple[float, ...]]:
        """Materialize the recipe's parameter tuples."""


# ==================================================================================================
#  ParamGrid
# ==================================================================================================
@dataclass(frozen=True)
class ParamGrid(ParamRecipe):
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
    def _coupled_param_sweep(per_axis: list[tuple[ValuePositionRange, ...]]) -> Iterator[tuple[float, ...]]:
        """Advance every axis together along one shared position in ``[0, 1]``, whatever their lengths.

        Each axis divides ``[0, 1]`` into the position ranges of its values (`ParamAxis.value_position_ranges`). The
        sweep walks the *union* of all axes' boundaries from 0 to 1, emitting the current value of every axis after
        each crossing. The 5-point and 3-point axes of `ParamAxis.value_position_ranges` line up like this::

            shared position:  0 --+--+--+--+--+--+-- 1
                                 1/8 | 3/8 5/8 | 7/8
                                    1/4       3/4

            emitted:  (0,0) (1,0) (1,1) (2,1) (3,1) (3,2) (4,2)

        Two properties follow, and they are the whole point: each axis steps at
        its own resolution, and no axis ever loses a value — so axis lengths
        need neither match nor be reconciled, where a fixed-count sample of the
        shared position would silently skip values of the finer axis. Usually
        one coordinate steps at a time; axes whose boundaries coincide step
        together (any two unrounded even-length axes share the boundary
        ``1/2``). Unrounded axes of equal length reduce to a plain zip, and
        axes that each hold a single value yield exactly one tuple. An axis has a boundary only where
        its value changes, so the sweep never emits the same tuple twice in a
        row.

        The implementation is a merge walk: instead of sampling positions and
        locating each axis within them, the boundaries become a sorted event
        stream, and each event advances the axes it belongs to. The boundaries
        are exact fractions, so ordering and coincidence need no tolerance.
        The sweep assumes every axis holds at least one value range, which
        `ParamAxis.value_position_ranges` guarantees.
        """
        events = sorted(
            (value_position_range.position_stop, axis)
            for axis, ranges in enumerate(per_axis)
            for value_position_range in ranges[:-1]
        )
        indices = [0] * len(per_axis)
        yield tuple(ranges[0].value for ranges in per_axis)
        for _, coinciding in itertools.groupby(events, key=lambda event: event[0]):
            for _, axis in coinciding:
                indices[axis] += 1
            yield tuple(ranges[index].value for ranges, index in zip(per_axis, indices, strict=True))

    def tuples(self) -> Iterator[tuple[float, ...]]:
        """Materialize the grid's parameter tuples."""
        if self.product:
            yield from itertools.product(*(axis.values() for axis in self.axes))
        else:
            yield from self._coupled_param_sweep([axis.value_position_ranges() for axis in self.axes])

    # --------------------------------------------------------------------------
    #  Single-axis conveniences
    # --------------------------------------------------------------------------
    @classmethod
    def decimal(cls, name: str, start: float, stop: float, step: float, *, summary: str | None = None) -> "ParamGrid":
        """Build a single-axis grid whose values are the grid arguments themselves (DECIMAL notation)."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamNotation.DECIMAL),), summary=summary)

    @classmethod
    def pow2(cls, name: str, start: float, stop: float, step: float, *, summary: str | None = None) -> "ParamGrid":
        """Build a single-axis grid in base-2 exponent space (POW2 notation)."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamNotation.POW2),), summary=summary)

    @classmethod
    def pow10(cls, name: str, start: float, stop: float, step: float, *, summary: str | None = None) -> "ParamGrid":
        """Build a single-axis grid in base-10 exponent space (POW10 notation)."""
        return cls(axes=(ParamAxis(name, start, stop, step, ParamNotation.POW10),), summary=summary)


# ==================================================================================================
#  ParamTable
# ==================================================================================================
@dataclass(frozen=True)
class ParamTable(ParamRecipe):
    """`ParamTable` lists parameter tuples and materializes them in the order listed.

    A table holds values that form no grid, such as a paper's published values (``n = 1, 5, 15, 20``), or
    the combinations of several parameters that the paper gives, where the product of the parameters' values would
    add combinations that the paper does not give.

    Attributes:
        names: The names of the parameters, in tuple position order.
        rows: The parameter tuples, each with 1 value per name. Every value must be a valid parameter value
            (`ParamNotation.is_valid_value`), so that each candidate's `ProblemId` can spell its parameter values.
    """

    names: tuple[str, ...]
    rows: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        """Check that the table has rows, that each row has 1 value per name, and that every value is valid.

        Raises:
            ValueError: If the table has no rows, a row's length differs from the number of names, or a value is
                not a valid parameter value.
        """
        if not self.rows:
            raise ValueError("A ParamTable needs at least 1 row.")
        for row in self.rows:
            if len(row) != len(self.names):
                raise ValueError(f"ParamTable row {row} does not have 1 value for each of the names {self.names}.")
            for value in row:
                if not ParamNotation.is_valid_value(value):
                    raise ValueError(
                        f"ParamTable value {value!r} is not a valid parameter value: no notation spells it with "
                        f"{CANONICAL_DIGITS} significant digits or fewer."
                    )

    def param_names(self) -> tuple[str, ...]:
        """Return the names of the table's parameters, in tuple position order."""
        return self.names

    def tuples(self) -> Iterator[tuple[float, ...]]:
        """Materialize the table's rows, in order, with each value as a float."""
        for row in self.rows:
            yield tuple(float(value) for value in row)
