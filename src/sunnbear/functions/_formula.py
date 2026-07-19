"""The `Formula` base class: hand-written function families plus generation metadata.

A formula owns three parameter layers with distinct roles: the recipe-swept
``p`` tuple (bound once per test function, consciously shaping its character),
the Monte-Carlo parameter ``c`` (varied per benchmark run), and — downstream,
never stored here — the tolerance ``xtol``.

Concrete formulas subclass `Formula` and implement three small hooks
(`parametrized_fun`, `bracket`, `recipes`); everything mechanical — numba
compilation (once per formula, see `Formula._compiled_formula`), identity
construction, candidate assembly and enumeration, registration — lives on the
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
        param_names: The formula's declared parameter interface, in tuple-position
            order — the authority every recipe is validated against, and the
            labels reporting uses. Empty for a formula without parameters.
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
        it as a free function). Parameters arrive as runtime arguments, never
        as closure state: compilation (when `jit` is set) then happens once per
        formula rather than once per candidate — see `_compiled_formula`.

        Overrides must **name** their parameters (``(x, c, p1, p2)``), matching
        `param_names`; the ``*params`` here is only this base declaration being
        generic over arity. See `_declared_hook_param_names`.
        """

    @abstractmethod
    def bracket(self, *params: float) -> tuple[float, float]:
        """Return the x-interval ``(a, b)`` guaranteed to bracket a root.

        Overrides must name their parameters, as for `parametrized_fun`.
        """

    @abstractmethod
    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the grid recipes that materialize candidate parameter tuples."""

    def is_param_tuple_valid(self, *params: float) -> bool:
        """Accept or reject a parameter tuple up front (default: accept all).

        This default is generic over arity; an override must name its
        parameters, as for `parametrized_fun`.
        """
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
            _declared_hook_param_names(fn, cls.__name__, "parametrized_fun", n_leading=2)  # signature gate
            cls._compiled_formula_cache = numba.njit(fn) if cls.jit else fn
        return cls._compiled_formula_cache

    def build_candidate(self, params: "tuple[ParamValue, ...]") -> CandidateTestFunction:
        """Build one candidate test function for a bound parameter tuple.

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

    def build_all_candidates(self) -> "tuple[CandidateTestFunction, ...]":
        """Build every candidate this formula defines: recipe tuples, filtered and deduplicated.

        Candidates come back in first-seen recipe order. Deduplication is by
        `FunctionId`, whose equality is notation-blind, so duplicates across
        recipes collapse even when the same value was spelled differently
        (e.g. a linear axis hitting ``4.0`` and a log2 axis hitting ``2^2.0``).

        Eager rather than lazy, and validating: a malformed formula fails here,
        at corpus-build time, instead of somewhere downstream. See
        `_validate_recipes` for what is checked.

        Raises:
            ValueError: If a recipe disagrees with `param_names`, if
                `param_names` disagrees with `parametrized_fun`'s signature, or
                if no candidate survives `is_param_tuple_valid`.
        """
        recipes = self.recipes()
        self._validate_recipes(recipes)
        self._validate_param_name_consistency()

        seen: set[FunctionId] = set()
        candidates: list[CandidateTestFunction] = []
        param_tuples = (p for recipe in recipes for p in recipe.tuples()) if recipes else iter([()])
        for params in param_tuples:
            function_id = FunctionId(self.number, params)
            if function_id in seen or not self.is_param_tuple_valid(*function_id.param_values):
                continue
            seen.add(function_id)
            candidates.append(self.build_candidate(params))

        if not candidates:
            raise ValueError(
                f"Formula {type(self).__name__} produced no candidates: every parameter tuple was "
                "rejected by is_param_tuple_valid. A formula that contributes nothing is a bug."
            )
        return tuple(candidates)

    # --------------------------------------------------------------------------
    #  Validation
    # --------------------------------------------------------------------------
    def _validate_recipes(self, recipes: "tuple[ParamRecipe, ...]") -> None:
        """Check that every recipe's axes agree with `param_names`.

        Axis order determines tuple order, which lands positionally on
        `parametrized_fun` — so axes declared in the wrong order silently
        transpose parameter values rather than failing. This check makes that
        impossible; it needs no introspection, so it holds for every formula. A
        formula that declares parameters but defines no recipes is rejected here
        too, since it can never materialize a tuple.

        Raises:
            ValueError: If a recipe's axes disagree with `param_names`, or if
                `param_names` is non-empty but no recipes are defined.
        """
        for recipe in recipes:
            if recipe.param_names() != self.param_names:
                raise ValueError(
                    f"Formula {type(self).__name__} declares param_names={self.param_names} but a recipe "
                    f"sweeps {recipe.param_names()}; recipe axes must match the declared parameters, in order."
                )
        if not recipes and self.param_names:
            raise ValueError(
                f"Formula {type(self).__name__} declares param_names={self.param_names} but defines no recipes."
            )

    def _validate_param_name_consistency(self) -> None:
        """Check that `param_names` matches the signature of every hook that receives the tuple.

        Independent of the recipes: this catches drift between the declaration
        (`param_names`) and the implementations — `parametrized_fun`, `bracket`,
        and `is_param_tuple_valid` when overridden. Those hooks must name their
        parameters rather than take ``*params``; see `_declared_hook_param_names`
        for why that is required rather than merely conventional.

        Raises:
            ValueError: If a hook's parameter names disagree with `param_names`.
            TypeError: If a hook's signature is malformed (``*params``, or a
                non-static `parametrized_fun`).
        """
        cls = type(self)
        hooks: list[tuple[str, Callable[..., object], int]] = [
            ("parametrized_fun", cls.parametrized_fun, 2),  # after (x, c)
            ("bracket", cls.bracket, 1),  # after self
        ]
        if cls.is_param_tuple_valid is not Formula.is_param_tuple_valid:
            hooks.append(("is_param_tuple_valid", cls.is_param_tuple_valid, 1))  # after self
        for hook, fun, n_leading in hooks:
            signature_names = _declared_hook_param_names(fun, cls.__name__, hook, n_leading)
            if signature_names != self.param_names:
                raise ValueError(
                    f"Formula {cls.__name__} declares param_names={self.param_names} but "
                    f"{hook} takes {signature_names}; the two must agree."
                )


def _declared_hook_param_names(fun: "Callable[..., object]", owner: str, hook: str, n_leading: int) -> tuple[str, ...]:
    """Return a hook's parameter names after its `n_leading` fixed arguments.

    The concrete-signature gate for formula hooks: every hook that receives the
    parameter tuple positionally must *name* its parameters, so that the
    declaration (`Formula.param_names`), the implementation, and the recipes
    can all be checked against one another. A ``*params`` signature would be
    unintrospectable and silently exempt that formula from the cross-checks.

    Args:
        fun: The hook to inspect.
        owner: Formula class name, for error messages.
        hook: Hook name, for error messages.
        n_leading: Fixed leading arguments to skip — ``self`` for a method,
            ``(x, c)`` for `Formula.parametrized_fun`.

    Raises:
        TypeError: If the signature takes ``*params`` instead of naming them,
            or (for `parametrized_fun`) is a plain method rather than a
            ``@staticmethod``.
    """
    parameters = list(inspect.signature(fun).parameters.values())
    if hook == "parametrized_fun" and parameters and parameters[0].name == "self":
        raise TypeError(
            f"{owner}.parametrized_fun must be a @staticmethod taking (x, c, p1, ...); "
            "it appears to be a plain method (first parameter is 'self')."
        )
    if any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in parameters):
        raise TypeError(
            f"{owner}.{hook} must name its parameters (e.g. '{hook}(..., p1, p2)') rather than take *params; "
            "named parameters are what let the declaration, the implementation and the recipes be cross-checked."
        )
    return tuple(p.name for p in parameters[n_leading:])
