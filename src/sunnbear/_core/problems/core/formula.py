"""The `Formula` base class: hand-written function families plus generation metadata.

A formula owns three parameter layers with distinct roles: the recipe-given
``p`` tuple (bound once per test problem, and chosen deliberately to set that test problem's properties),
the Monte-Carlo parameter ``c`` (varied per benchmark run), and — downstream,
never stored here — the tolerance ``xtol``.

Concrete formulas subclass `Formula` and implement 3 small hooks
(`parametrized_fun`, `interval_bounds`, `recipes`); everything mechanical — numba
compilation (once per formula, see `Formula._compiled_formula`), identity
construction, candidate assembly and enumeration, registration — lives on the
base class, so a formula module contains nothing but the mathematics. Subclasses
register themselves on definition (``__init_subclass__``), which also lets
downstream users contribute formulas without touching this package.
"""

import functools
import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import ClassVar

import numba

from .effect_of_c import EffectOfC
from .identity import ProblemId
from .param import FormulaParam
from .param_values import DEDUP_DIGITS, ParamNotation, deduplicate_param_tuples
from .presentation import FormulaPresentation, LatexTemplate
from .recipes import ParamRecipe
from .registry import FormulaRegistry
from .source import FormulaSource
from .taxonomy import FormulaTaxonomyNode
from .test_cases import FormulaTestCase
from .test_problem import CandidateTestProblem
from .types import XCFun, XFun


# ==================================================================================================
#  Formula
# ==================================================================================================
class Formula(FormulaTaxonomyNode, ABC):
    """A `Formula` holds one hand-written formula: its mathematics and the metadata to build candidate test problems.

    Class attributes:
        number: The formula's place in the taxonomy, e.g. ``(2, 1, 1)``; its parent category is
            ``number[:-1]``, and every formula belongs to a category, so the number has at least
            2 elements.
        name: Display name, e.g. "Odd power".
        params: The formula's declared parameters (`FormulaParam`), in tuple-position order. Every recipe and every
            hook signature is validated against the parameters' names (`param_names`), which also label ids and reports.
            Empty for a formula without parameters.
        jit: Whether `parametrized_fun` is numba-compiled (default) — set
            False for formulas numba cannot compile.
        test_cases: The formula's own test cases (`FormulaTestCase`), which
            the generic formula test runs; every registered formula must
            declare at least 1.
        source: The formula's publication (`FormulaSource`), or None (default)
            for a formula that no publication gives.
        presentation: What a reader sees of the formula (`FormulaPresentation`), or None (default). The catalog's
            tests require it of every shipped formula.
        effect_of_c: How the formula's code applies ``c`` (`EffectOfC`), or None (default). The catalog's tests
            require it of every shipped formula, and check it by evaluating the formula.
    """

    params: ClassVar[tuple[FormulaParam, ...]] = ()
    jit: ClassVar[bool] = True
    test_cases: ClassVar[tuple[FormulaTestCase, ...]] = ()
    source: ClassVar[FormulaSource | None] = None
    presentation: ClassVar[FormulaPresentation | None] = None
    effect_of_c: ClassVar[EffectOfC | None] = None
    # populated lazily per concrete class by _compiled_formula (annotation only — no value,
    # so the `in cls.__dict__` cache check below is not satisfied by this declaration)
    _compiled_formula_cache: ClassVar["Callable[..., float]"]

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Validate every concrete subclass and register it with `FormulaRegistry`, at class definition.

        `inspect.isabstract` cannot decide concreteness here, because this hook runs before the ABC
        machinery records the new class's abstract methods.

        Raises:
            TypeError: If the subclass declares ``param_names``: `Formula` derives it from `params`, and a class
                attribute of that name would hide the derived property.
            ValueError: If a concrete subclass's presentation names a parameter that it does not declare, or leaves a
                declared parameter out of its definitions, expression and interval (`_validate_presentation`).
        """
        super().__init_subclass__(**kwargs)
        if "param_names" in cls.__dict__:
            raise TypeError(f"{cls.__name__} declares param_names; declare its parameters in params instead.")
        is_concrete = not any(
            getattr(getattr(cls, name), "__isabstractmethod__", False) for name in Formula.__abstractmethods__
        )
        if is_concrete:
            cls._validate_number_and_name(min_number_length=2)
            cls._validate_presentation()
            FormulaRegistry.register_formula(cls)

    @property
    def param_names(self) -> tuple[str, ...]:
        """Return the names of `params`, in tuple-position order, as ids, recipes and hook signatures use them."""
        return tuple(param.name for param in self.params)

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
    def interval_bounds(self, *params: float) -> tuple[float, float]:
        """Return the bracketing x-interval ``(a, b)``: ``f`` changes sign between ``a`` and ``b``.

        Overrides must name their parameters, as for `parametrized_fun`. A formula whose interval
        does not depend on its parameters returns a fixed one, wide enough for the calibrated c-range.
        """

    @abstractmethod
    def recipes(self) -> tuple[ParamRecipe, ...]:
        """Return the recipes, grids or tables, that materialize candidate parameter tuples.

        The order matters where recipes overlap: among near-duplicate tuples, the one from the
        first recipe is kept (see `build_all_candidates`).
        """

    def is_param_tuple_valid(self, *params: float) -> bool:
        """Accept or reject a parameter tuple up front (default: accept all).

        This default is generic over arity; an override must name its
        parameters, as for `parametrized_fun`.
        """
        return True

    # --------------------------------------------------------------------------
    #  Framework-owned assembly
    # --------------------------------------------------------------------------
    def param_dict_to_tuple(self, params: dict[str, float]) -> tuple[float, ...]:
        """Resolve a name-keyed parameter dict to positional order (`param_names`).

        Raises:
            ValueError: If `params`'s keys are not exactly `param_names`.
        """
        if set(params) != set(self.param_names):
            raise ValueError(
                f"{type(self).__name__}: params {sorted(params)} do not match param_names {list(self.param_names)}."
            )
        return tuple(params[name] for name in self.param_names)

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
        - **Lazy (first bind), not at class definition**: importing the catalog
          must stay cheap; numba decoration and compilation are only paid by
          processes that bind a parameter tuple of the formula.
        - **Compiled when the formula is first bound, not at its first call**:
          the explicit all-float64 signature makes numba compile at decoration,
          which happens in the first `bind_xc_fun` or `bind_x_fun`. The first
          call usually happens inside `Solver.solve`, whose flop-counting
          context replaces the functions of the `math` module with counting
          wrappers, and numba cannot compile a call to those.
        """
        cls = type(self)
        if "_compiled_formula_cache" not in cls.__dict__:
            fn = cls.parametrized_fun
            param_names = _declared_hook_param_names(fn, cls.__name__, "parametrized_fun", n_leading=2)
            if cls.jit:
                signature = f"float64({', '.join(['float64'] * (2 + len(param_names)))})"
                cls._compiled_formula_cache = numba.njit(signature)(fn)
            else:
                cls._compiled_formula_cache = fn
        return cls._compiled_formula_cache

    def build_candidate(self, param_values: "tuple[float, ...]") -> CandidateTestProblem:
        """Build one candidate test problem for a bound parameter tuple."""
        problem_id = ProblemId(self.number, self.param_names, tuple(param_values))
        a, b = self.interval_bounds(*problem_id.param_values)
        return CandidateTestProblem(id=problem_id, formula=self, a=a, b=b)

    def bind_xc_fun(self, values: "tuple[float, ...]") -> XCFun:
        """Bind a parameter tuple over the once-per-class compiled body, yielding ``f(x, c)``."""
        compiled = self._compiled_formula()

        def xc_fun(x: float, c: float) -> float:
            """Evaluate the formula with its parameter tuple bound."""
            return compiled(x, c, *values)

        return xc_fun

    def bind_x_fun(self, values: "tuple[float, ...]", c: float) -> XFun:
        """Bind a parameter tuple *and* `c` in one closure over the compiled body, yielding ``f(x)``.

        Deliberately not a wrapper around `bind_xc_fun`: this is the solver hot
        path, so it costs one Python call per evaluation rather than two.
        """
        compiled = self._compiled_formula()

        def x_fun(x: float) -> float:
            """Evaluate the formula with its parameter tuple and c bound."""
            return compiled(x, c, *values)

        return x_fun

    def build_all_candidates(self, digits: int = DEDUP_DIGITS) -> "tuple[CandidateTestProblem, ...]":
        """Build every candidate this formula defines: recipe tuples, filtered and deduplicated.

        Candidates come back in the order the recipes generate their tuples, and **among
        near-duplicates the tuple from the earliest recipe in `recipes` is kept**. The tuples go
        through 3 passes, in this order:

        1. **Validity.** Tuples the formula rejects are dropped first, so a
           rejected tuple can never displace a valid near-twin by arriving ahead
           of it in the next pass.
        2. **Near-duplicate removal** at `digits` significant digits
           (`deduplicate_param_tuples`), which collapses values that differ
           only because of float rounding error. This happens on the parameter tuples, before identities
           exist: the formula number is the same for every tuple here, so it
           carries no information for the collapse.
        3. **Construction** (identities included), so the per-candidate work is
           paid only for survivors.

        Eager rather than lazy, and validating: a malformed formula fails here,
        at corpus-build time, instead of somewhere downstream. See
        `_validate_recipes` for what is checked.

        Args:
            digits: Significant digits at which two parameter tuples count as
                the same test problem.

        Raises:
            ValueError: If a recipe disagrees with `param_names`, if
                `param_names` disagrees with `parametrized_fun`'s signature, or
                if no candidate survives `is_param_tuple_valid`.
        """
        recipes = self.recipes()
        self._validate_recipes(recipes)
        self._validate_param_name_consistency()

        param_tuples = (p for recipe in recipes for p in recipe.tuples()) if recipes else iter([()])
        valid_tuples = (param_values for param_values in param_tuples if self.is_param_tuple_valid(*param_values))
        candidates = [
            self.build_candidate(param_values) for param_values in deduplicate_param_tuples(valid_tuples, digits)
        ]

        if not candidates:
            raise ValueError(
                f"Formula {type(self).__name__} produced no candidates: every parameter tuple was "
                "rejected by is_param_tuple_valid. A formula that contributes nothing is a bug."
            )
        return tuple(candidates)

    # --------------------------------------------------------------------------
    #  LaTeX of the presentation
    # --------------------------------------------------------------------------
    def texts_for_a_reader(self) -> tuple[str, ...]:
        """Return its texts for a reader: its parameters' meanings, its recipes' summaries, its presentation's texts."""
        meanings = [param.meaning for param in self.params if param.meaning is not None]
        summaries = [recipe.summary for recipe in self.recipes() if recipe.summary is not None]
        if self.presentation is not None:
            return (*meanings, *summaries, *self.presentation.texts_for_a_reader)
        else:
            return (*meanings, *summaries)

    def latex_with_symbols(self, text: str) -> str:
        r"""Return `text`, in sunnbear's LaTeX notation, with each placeholder replaced by its parameter's symbol.

        Each symbol is wrapped in ``\prm{…}`` (`LatexTemplate.substitute`). A formula's texts for a reader are always
        rendered with its parameters' symbols.

        Raises:
            ValueError: If `text` breaks sunnbear's LaTeX notation (`LatexTemplate`), or names a parameter that the
                formula does not declare or that has no `latex_symbol`.
        """
        symbols = {param.name: param.latex_symbol for param in self.params if param.latex_symbol is not None}
        return LatexTemplate(text).substitute(symbols)

    def latex_with_values(self, text: str, param_values: tuple[float, ...]) -> str:
        r"""Return `text`, in sunnbear's LaTeX notation, with each placeholder replaced by a test problem's value.

        Each value is spelled as the test problem's id spells it, written in LaTeX
        (`ParamNotation.spell_value_in_latex`), and wrapped in ``\prm{…}``. The values are substituted, not simplified:
        ``1 - \param{m}`` at ``m = 0.5`` gives ``1 - \prm{0.5}``.

        Args:
            text: A definition's side, the expression or the interval of the formula's presentation.
            param_values: The test problem's parameter values, in the order of `params`.

        Raises:
            ValueError: If `param_values` does not hold 1 value per parameter, if a value has no spelling
                (`ParamNotation.spell_value_in_latex`), if `text` breaks sunnbear's LaTeX notation (`LatexTemplate`),
                or if `text` names a parameter that the formula does not declare.
        """
        values = dict(zip(self.param_names, param_values, strict=True))
        return LatexTemplate(text).substitute(
            {name: ParamNotation.spell_value_in_latex(value) for name, value in values.items()}
        )

    def latex_display(self, param_values: tuple[float, ...] | None = None) -> str:
        r"""Return the presentation as 1 LaTeX display: its definitions, then ``f(\x, \c) = `` and its expression.

        With definitions, the display is an ``aligned`` environment of 1 line per definition, then the line of
        ``f(\x, \c)``, aligned at their ``=``; without, it is the 1 line ``f(\x, \c) = …``.

        Args:
            param_values: A test problem's parameter values, in the order of `params`, for the display with values;
                None (default) for the display with the parameters' symbols.

        Raises:
            ValueError: If the formula declares no presentation, or if a line cannot be rendered, as in
                `latex_with_symbols` and `latex_with_values`.
        """
        if self.presentation is None:
            raise ValueError(f"{self.label} declares no presentation.")
        if param_values is None:
            render = self.latex_with_symbols
        else:
            render = functools.partial(self.latex_with_values, param_values=param_values)
        rendered = [(render(left), render(right)) for left, right in self.presentation.display_lines]
        if len(rendered) > 1:
            body = r" \\ ".join(f"{left} &= {right}" for left, right in rendered)
            return rf"\begin{{aligned}} {body} \end{{aligned}}"
        else:
            left, right = rendered[0]
            return f"{left} = {right}"

    # --------------------------------------------------------------------------
    #  Validation
    # --------------------------------------------------------------------------
    def _validate_recipes(self, recipes: "tuple[ParamRecipe, ...]") -> None:
        """Check that every recipe's parameter names agree with `param_names`.

        Axis order determines tuple order, which lands positionally on
        `parametrized_fun` — so axes declared in the wrong order silently
        transpose parameter values rather than failing. This check makes that
        impossible; it needs no introspection, so it holds for every formula. A
        formula that declares parameters but defines no recipes is rejected here
        too, since it can never materialize a tuple.

        Raises:
            ValueError: If a recipe's parameter names disagree with `param_names`, or if
                `param_names` is non-empty but no recipes are defined.
        """
        for recipe in recipes:
            if recipe.param_names() != self.param_names:
                raise ValueError(
                    f"Formula {type(self).__name__} declares the parameters {self.param_names} but a recipe gives "
                    f"{recipe.param_names()}; recipe parameter names must match the declared parameters, in order."
                )
        if not recipes and self.param_names:
            raise ValueError(
                f"Formula {type(self).__name__} declares the parameters {self.param_names} but defines no recipes."
            )

    def _validate_param_name_consistency(self) -> None:
        """Check that `param_names` matches the signature of every hook that receives the tuple.

        Independent of the recipes: this catches drift between the declaration
        (`params`) and the implementations — `parametrized_fun`, `interval_bounds`,
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
            ("interval_bounds", cls.interval_bounds, 1),  # after self
        ]
        if cls.is_param_tuple_valid is not Formula.is_param_tuple_valid:
            hooks.append(("is_param_tuple_valid", cls.is_param_tuple_valid, 1))  # after self
        for hook, fun, n_leading in hooks:
            signature_names = _declared_hook_param_names(fun, cls.__name__, hook, n_leading)
            if signature_names != self.param_names:
                raise ValueError(
                    f"Formula {cls.__name__} declares the parameters {self.param_names} but "
                    f"{hook} takes {signature_names}; the two must agree."
                )

    @classmethod
    def _validate_presentation(cls) -> None:
        """Check that the presentation and the meanings name only declared parameters, and that its math names each one.

        The meanings are those of the parameters, and the presentation's math is its definitions, expression and
        interval.

        A formula without a presentation is not checked; the catalog's tests require one of every shipped formula.

        Raises:
            ValueError: If a placeholder names an undeclared parameter, or a parameter appears in none of the
                definitions, the expression and the interval.
        """
        if cls.presentation is not None:
            param_names = [param.name for param in cls.params]
            meaning_names = {
                name
                for param in cls.params
                if param.meaning is not None
                for name in LatexTemplate(param.meaning).placeholder_names
            }
            undeclared = sorted((cls.presentation.placeholder_names | meaning_names) - set(param_names))
            if undeclared:
                raise ValueError(f"{cls.__name__}'s presentation names the undeclared parameters {undeclared}.")
            absent = [name for name in param_names if name not in cls.presentation.math_placeholder_names]
            if absent:
                raise ValueError(
                    f"{cls.__name__}'s presentation leaves the parameters {absent} out of its definitions, expression "
                    "and interval."
                )


def _declared_hook_param_names(fun: "Callable[..., object]", owner: str, hook: str, n_leading: int) -> tuple[str, ...]:
    """Return a hook's parameter names after its `n_leading` fixed arguments.

    The concrete-signature gate for formula hooks: every hook that receives the
    parameter tuple positionally must *name* its parameters, so that the
    declaration (`Formula.params`), the implementation, and the recipes
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
