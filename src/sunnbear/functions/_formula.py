"""The `Formula` base class: hand-written function families plus generation metadata.

A formula owns three parameter layers with distinct roles: the recipe-swept
``p`` tuple (bound once per test function, consciously shaping its character),
the Monte-Carlo parameter ``c`` (varied per benchmark run), and — downstream,
never stored here — the tolerance ``xtol``.

Concrete formulas subclass `Formula` and implement three small hooks
(`parametrized_fun`, `bracket`, `recipes`); everything mechanical — numba
compilation (once per formula, see `Formula._compiled_formula`), identity
construction, `CandidateTestFunction` assembly, registration — lives on the
base class, so a formula module contains nothing but the mathematics. Subclasses
register themselves on definition (``__init_subclass__``), which also lets
downstream users contribute formulas without touching this package.
"""

import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import ClassVar

import numba

from ._identity import FunctionId, ParamValue
from ._recipes import ParamRecipe
from ._test_function import CandidateTestFunction

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
        jit: Whether `parametrized_fun` is numba-compiled (default) — set
            False for formulas numba cannot compile.
    """

    number: ClassVar[int]
    name: ClassVar[str]
    param_names: ClassVar[tuple[str, ...]] = ()
    jit: ClassVar[bool] = True
    # populated lazily per concrete class by _compiled_formula (annotation only — no value,
    # so the `in cls.__dict__` cache check below is not satisfied by this declaration)
    _compiled_formula_cache: ClassVar["Callable[..., float]"]

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Register every subclass; abstract intermediates are filtered out by the registry."""
        super().__init_subclass__(**kwargs)
        registered_formula_classes.append(cls)

    # --------------------------------------------------------------------------
    #  Hooks implemented per formula
    # --------------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def parametrized_fun(x: float, c: float, *params: float) -> float:
        """The formula itself, in fully parametrized form ``f(x, c, p1, p2, ...)``.

        A plain ``@staticmethod`` (no ``self`` — numba must be able to compile
        it as a free function; the framework guards against accidental plain
        methods). Parameters arrive as runtime arguments, never as closure
        state: compilation (when `jit` is set) then happens once per formula
        rather than once per candidate — see `_compiled_formula`.
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
    def _compiled_formula(self) -> Callable[..., float]:
        """Return this formula's ``parametrized_fun``, numba-compiled at most once per class.

        Subtle by necessity — the choices here, and why:

        - **Cached on the concrete class, not the instance or this base**: all
          instances (and all candidates) of one formula share one compiled
          artifact, which is the point of the parametrized-function design —
          compile cost scales with the number of formulas (~100s), not the
          number of candidates (~100 000s). Closure-level jitting would also
          defeat numba's on-disk cache entirely (dynamically created closures
          have no cache locator).
        - **``cls.__dict__`` membership check, not ``hasattr``**: ``hasattr``
          would find a *parent* class's cached artifact through inheritance
          and wrongly reuse it for a subclass with a different
          ``parametrized_fun``.
        - **Guard against a ``self`` parameter**: the ABC cannot enforce that
          the override is a ``@staticmethod``; a plain method would surface
          later as an inscrutable numba typing error about ``self``, so it is
          rejected here with an actionable message.
        - **Lazy (first use), not at class definition**: importing the catalog
          must stay cheap; numba decoration and compilation are only paid by
          processes that actually evaluate the formula.
        """
        cls = type(self)
        if "_compiled_formula_cache" not in cls.__dict__:
            fn = cls.parametrized_fun
            first_arg = next(iter(inspect.signature(fn).parameters), None)
            if first_arg == "self":
                raise TypeError(
                    f"{cls.__name__}.parametrized_fun must be a @staticmethod taking (x, c, *params); "
                    "it appears to be a plain method (first parameter is 'self')."
                )
            cls._compiled_formula_cache = numba.njit(fn) if cls.jit else fn
        return cls._compiled_formula_cache

    def candidate(self, params: "tuple[ParamValue | float, ...]") -> CandidateTestFunction:
        """Materialize one candidate test function for a bound parameter tuple.

        Binds the parameter values over the once-per-class compiled formula
        (see `_compiled_formula`) in a thin plain-Python closure — formula
        implementations never construct a `CandidateTestFunction` themselves,
        never touch numba, and their non-static hooks receive plain floats
        (`ParamValue` unwrapping is handled here).
        """
        fid = FunctionId(self.number, tuple(params))
        compiled = self._compiled_formula()
        values = fid.param_values

        def fun(x: float, c: float) -> float:
            """Evaluate the formula with its parameter tuple bound."""
            return compiled(x, c, *values)

        a, b = self.bracket(*values)
        return CandidateTestFunction(id=fid, fun=fun, a=a, b=b)
