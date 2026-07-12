"""Declarative parameter-grid recipes that materialize candidate parameter tuples.

A recipe spans one or more axes, each sweeping one named parameter over a
linear or logarithmic grid. Grid values are rounded to their grid resolution
so printed parameter values stay short, human-screenable, and exactly
reproducible. The grammar is deliberately small (range + spacing + step +
product flag); anything fancier is expressed by adding another recipe —
recipes are additive.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum


# ==================================================================================================
#  Spacing
# ==================================================================================================
class Spacing(StrEnum):
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

    name: str
    start: float
    stop: float
    step: float
    spacing: Spacing = Spacing.LINEAR

    def __post_init__(self) -> None:
        """Validate that the grid is well-formed (positive step, stop not before start)."""
        if self.step <= 0.0:
            raise ValueError(f"ParamAxis step must be > 0 (got {self.step}).")
        if self.stop < self.start:
            raise ValueError(f"ParamAxis stop must be >= start (got {self.start}..{self.stop}).")

    def values(self) -> tuple[float, ...]:
        """Materialize the axis's grid values, rounded to the grid resolution."""
        decimals = max(_decimals(self.start), _decimals(self.step))
        n_points = round((self.stop - self.start) / self.step) + 1
        grid = [round(self.start + i * self.step, decimals) for i in range(n_points)]
        grid = [g for g in grid if g <= self.stop + 10 ** -(decimals + 6)]
        if self.spacing == Spacing.LOG2:
            return tuple(2.0**g for g in grid)
        if self.spacing == Spacing.LOG10:
            return tuple(10.0**g for g in grid)
        return tuple(grid)


def _decimals(value: float) -> int:
    """Count decimal digits in a value's shortest repr (0 for integers and exponent notation)."""
    text = repr(value)
    if "e" in text or "E" in text or "." not in text:
        return 0
    return len(text.split(".")[1])


# ==================================================================================================
#  ParamRecipe
# ==================================================================================================
@dataclass(frozen=True)
class ParamRecipe:
    """A set of axes materializing parameter tuples, as a full product or swept jointly.

    With ``product=True`` (default) the axes span their Cartesian product; with
    ``product=False`` all axes advance together (and must have equal lengths).
    """

    axes: tuple[ParamAxis, ...]
    product: bool = True

    def param_names(self) -> tuple[str, ...]:
        """Return the axis names, in tuple position order."""
        return tuple(axis.name for axis in self.axes)

    def tuples(self) -> Iterator[tuple[float, ...]]:
        """Materialize the recipe's parameter tuples.

        Raises:
            ValueError: If ``product=False`` and the axes have unequal lengths.
        """
        per_axis = [axis.values() for axis in self.axes]
        if self.product:
            yield from itertools.product(*per_axis)
        else:
            lengths = {len(values) for values in per_axis}
            if len(lengths) > 1:
                raise ValueError("Jointly swept axes must have equal lengths.")
            yield from zip(*per_axis, strict=True)

    # --------------------------------------------------------------------------
    #  Single-axis conveniences
    # --------------------------------------------------------------------------
    @classmethod
    def linear(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe with a linear grid."""
        return cls(axes=(ParamAxis(name, start, stop, step, Spacing.LINEAR),))

    @classmethod
    def log2(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe gridded in log2 exponent space."""
        return cls(axes=(ParamAxis(name, start, stop, step, Spacing.LOG2),))

    @classmethod
    def log10(cls, name: str, start: float, stop: float, step: float) -> "ParamRecipe":
        """Build a single-axis recipe gridded in log10 exponent space."""
        return cls(axes=(ParamAxis(name, start, stop, step, Spacing.LOG10),))
