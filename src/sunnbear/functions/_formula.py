"""The `Formula` base class: hand-written function families plus generation metadata.

A formula owns three parameter layers with distinct roles: the recipe-swept
``p`` tuple (bound once per test function, consciously shaping its character),
the Monte-Carlo parameter ``c`` (varied per benchmark run), and — downstream,
never stored here — the tolerance ``xtol``.

Concrete formulas subclass `Formula` and implement three small hooks
(`make_fun`, `bracket`, `recipes`); everything mechanical — numba compilation,
identity construction, `Candidate` assembly, registration — lives on the base
class, so a formula module contains nothing but the mathematics. Subclasses
register themselves on definition (``__init_subclass__``), which also lets
downstream users contribute formulas without touching this package.
"""

from abc import ABC, abstractmethod
from typing import ClassVar, cast

import numba

from ._identity import FunctionId
from ._recipes import ParamRecipe
from ._test_function import Candidate
from ._types import XCFun

# All defined Formula subclasses, in definition order; the registry filters and instantiates.
registered_formula_classes: list[type["Formula"]] = []


# ==================================================================================================
#  Formula
# ==================================================================================================
class Formula(ABC):
    """One hand-written formula: the mathematics plus metadata to spawn candidate test functions.

    Class attributes:
        number: Registry-wide formula number (grouping by type, e.g. 1xx polynomials).
        name: Short human-readable slug.
        param_names: Names of the ``p`` tuple's positions, for display purposes.
        jit: Whether `candidate` numba-compiles the function returned by
            `make_fun` (default) — set False for formulas numba cannot compile.
    """

    number: ClassVar[int]
    name: ClassVar[str]
    param_names: ClassVar[tuple[str, ...]] = ()
    jit: ClassVar[bool] = True

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Register every subclass; abstract intermediates are filtered out by the registry."""
        super().__init_subclass__(**kwargs)
        registered_formula_classes.append(cls)

    # --------------------------------------------------------------------------
    #  Hooks implemented per formula
    # --------------------------------------------------------------------------
    @abstractmethod
    def make_fun(self, *params: float) -> XCFun:
        """Build the plain-Python ``f(x, c)`` with the parameter tuple bound.

        Return an ordinary function; compilation (when `jit` is set) is the
        framework's concern, applied in `candidate`.
        """

    @abstractmethod
    def bracket(self, *params: float) -> tuple[float, float]:
        """Return the x-interval ``(a, b)`` guaranteed to bracket a root."""

    @abstractmethod
    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the grid recipes that materialize candidate parameter tuples."""

    def is_param_tuple_valid(self, *params: float) -> bool:
        """Accept or reject a parameter tuple up front (default: accept all)."""
        return True

    # --------------------------------------------------------------------------
    #  Framework-owned assembly
    # --------------------------------------------------------------------------
    def candidate(self, params: tuple[float, ...]) -> Candidate:
        """Materialize one candidate test function for a bound parameter tuple.

        Applies numba compilation (per `jit`) and assembles identity, function,
        and bracket — formula implementations never construct a `Candidate`
        themselves.
        """
        fun = self.make_fun(*params)
        if self.jit:
            # numba's dispatcher is call-compatible with the plain f(x, c) it wraps
            fun = cast("XCFun", numba.njit(fun))
        a, b = self.bracket(*params)
        return Candidate(id=FunctionId(self.number, params), fun=fun, a=a, b=b)
