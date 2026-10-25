import math

import pytest
from counted_float import FlopCountingContext

from sunnbear._core.functions.catalog.c02_standard_function_families.c01_polynomials.f01_cubic import Cubic
from sunnbear._core.functions.catalog.c02_standard_function_families.c01_polynomials.f02_odd_power import OddPower
from sunnbear._core.functions.core import (
    Formula,
    FormulaRegistry,
    ParamAxis,
    ParamGrid,
    ParamRecipe,
    ProblemId,
)
from sunnbear._core.functions.core.exceptions import InvalidParamsError, UnknownFormulaError

from .example_taxonomy_nodes import define_formula_cls


# ==================================================================================================
#  formulas / candidates
# ==================================================================================================
def test_formulas_contains_catalog_sorted():
    # --- act --------------------------
    registered = FormulaRegistry.formulas()

    # --- assert -----------------------
    assert [f.number for f in registered] == sorted(f.number for f in registered)
    assert {type(f) for f in registered} >= {Cubic, OddPower}


def test_candidates_materializes_recipe_grid():
    # --- act --------------------------
    cubic_candidates = list(Cubic().build_all_candidates())

    # --- assert -----------------------
    assert [c.id.param_values for c in cubic_candidates] == [(0.0,), (0.2,), (0.4,), (0.6,), (0.8,), (1.0,)]
    assert all(c.id.formula_number == Cubic.number for c in cubic_candidates)
    assert all((c.a, c.b) == (-2.0, 2.0) for c in cubic_candidates)


def test_candidates_applies_validity_filter():
    # --- act --------------------------
    odd_candidates = list(OddPower().build_all_candidates())

    # --- assert -----------------------
    assert [c.id.param_values for c in odd_candidates] == [(1.0,), (3.0,), (5.0,), (7.0,)]


@pytest.mark.parametrize("formula_cls", [Cubic, OddPower])
def test_candidates_functions_evaluate(formula_cls):
    """The cubic and the odd power each produce a working f(x, c) callable."""
    # --- arrange ----------------------
    candidate = formula_cls().build_all_candidates()[0]  # p1 = 0.0 resp. 1.0

    # --- act / assert -----------------
    assert candidate.xc_fun(2.0, 1.0) == pytest.approx(candidate.xc_fun(2.0, 0.0) - 1.0)


@pytest.mark.usefixtures("isolated_formula_registry")
def test_candidates_deduplicates_across_recipes():
    # --- arrange ----------------------
    class DupTest(Formula):
        number = (99, 999)
        name = "Dup test"
        param_names = ("p1",)
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float, p1: float) -> float:
            return x - c

        def interval_bounds(self, p1: float) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return (ParamGrid.decimal("p1", 0.0, 1.0, 0.5), ParamGrid.decimal("p1", 0.5, 1.5, 0.5))

    # --- act --------------------------
    params = [c.id.param_values for c in DupTest().build_all_candidates()]

    # --- assert -----------------------
    assert params == [(0.0,), (0.5,), (1.0,), (1.5,)]


# ==================================================================================================
#  registration
# ==================================================================================================
@pytest.mark.usefixtures("isolated_formula_registry")
def test_subclass_definition_registers():
    # --- arrange / act ----------------
    cls = define_formula_cls((99, 998))

    # --- assert -----------------------
    assert any(type(f) is cls for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_formula_registry")
def test_defining_a_non_positive_number_is_rejected_at_class_definition():
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="only positive integers"):
        define_formula_cls((99, 0))


@pytest.mark.usefixtures("isolated_formula_registry")
def test_zero_param_formula_yields_exactly_one_candidate():
    """A formula without parameters materializes the single empty tuple, once."""
    # --- act --------------------------
    candidates = define_formula_cls((99, 992))().build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == 1
    assert candidates[0].id.param_values == ()
    assert str(candidates[0].id) == "f99.992"


def test_registry_holds_one_instance_per_formula():
    """Enumeration and reconstruction hand out the same registered instance."""
    # --- act --------------------------
    [enumerated] = [f for f in FormulaRegistry.formulas() if type(f) is Cubic]
    candidate_a = FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]")
    candidate_b = FormulaRegistry.candidate_from_id("f2.1.1[p1=0.4]")

    # --- assert -----------------------
    assert candidate_a.formula is candidate_b.formula is enumerated


@pytest.mark.usefixtures("isolated_formula_registry")
def test_formulas_defined_after_first_use_are_registered():
    """A formula defined after a call to `formulas()` appears in the next call: registration is at class definition."""
    # --- arrange ----------------------
    FormulaRegistry.formulas()

    # --- act --------------------------
    cls = define_formula_cls((99, 994))

    # --- assert -----------------------
    assert any(type(f) is cls for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_formula_registry")
def test_abstract_intermediates_are_not_registered():
    # --- arrange ----------------------
    class PolynomialBase(Formula):
        """Abstract intermediate: adds no hooks, implements none."""

    # --- act / assert -----------------
    assert all(type(f) is not PolynomialBase for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_formula_registry")
def test_candidates_deduplicates_across_notations():
    # --- arrange ----------------------
    class CrossNotation(Formula):
        number = (99, 995)
        name = "Cross notation"
        param_names = ("p1",)
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float, p1: float) -> float:
            return x - c

        def interval_bounds(self, p1: float) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            # a DECIMAL axis builds 4.0 and a POW2 axis builds 2^2.0: the same float, so one value
            return (ParamGrid.decimal("p1", 4.0, 4.0, 1.0), ParamGrid.pow2("p1", 2.0, 2.0, 1.0))

    # --- act --------------------------
    ids = [c.id for c in CrossNotation().build_all_candidates()]

    # --- assert -----------------------
    assert [str(fid) for fid in ids] == ["f99.995[p1=4.0]"]


# ==================================================================================================
#  recipe validation
# ==================================================================================================
def _formula_cls(number_last_element: int, declared: tuple[str, ...], recipes: tuple, fun=None, interval_bounds=None):
    """Build a throwaway Formula numbered ``(99, number_last_element)``; declaration and recipes vary independently."""
    namespace = {
        "number": (99, number_last_element),
        "name": f"Varying {number_last_element}",
        "param_names": declared,
        "jit": False,
        "parametrized_fun": staticmethod(fun or (lambda x, c, p1: x - c)),
        "interval_bounds": interval_bounds or (lambda self, p1: (-1.0, 1.0)),
        "recipes": lambda self: recipes,
    }
    return type(f"Varying{number_last_element}", (Formula,), namespace)


@pytest.mark.usefixtures("isolated_formula_registry")
def test_recipe_axis_order_must_match_declared_params():
    """Transposed axes would silently swap parameter values, so they must be rejected."""
    # --- arrange ----------------------
    transposed = ParamGrid(axes=(ParamAxis("p2", 7.0, 7.0, 1.0), ParamAxis("p1", 3.0, 3.0, 1.0)))
    cls = _formula_cls(
        990,
        ("p1", "p2"),
        (transposed,),
        fun=lambda x, c, p1, p2: x - c,
    )

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="recipe parameter names must match the declared parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_recipe_arity_must_match_declared_params():
    # --- arrange ----------------------
    cls = _formula_cls(989, ("p1", "p2"), (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),), fun=lambda x, c, p1, p2: x - c)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="recipe parameter names must match the declared parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_declared_params_must_match_parametrized_fun_signature():
    # --- arrange ----------------------
    cls = _formula_cls(988, ("p1",), (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),), fun=lambda x, c, other: x - c)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="parametrized_fun takes"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_declared_params_must_match_interval_bounds_signature():
    """Right arity but wrong names in interval_bounds is drift too — the cross-check covers every hook."""
    # --- arrange ----------------------
    cls = _formula_cls(
        981,
        ("p1",),
        (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),),
        interval_bounds=lambda self, other: (-1.0, 1.0),
    )

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="interval_bounds takes"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_declared_params_must_match_overridden_validity_hook_signature():
    # --- arrange ----------------------
    cls = _formula_cls(980, ("p1",), (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),))
    cls.is_param_tuple_valid = lambda self, other: True

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="is_param_tuple_valid takes"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_varargs_parametrized_fun_is_rejected():
    """Hooks must name their parameters, so declaration/implementation/recipes stay cross-checkable."""
    # --- arrange ----------------------
    cls = _formula_cls(987, ("p1",), (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),), fun=lambda x, c, *params: x - c)

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="must name its parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_varargs_interval_bounds_is_rejected():
    # --- arrange ----------------------
    cls = _formula_cls(
        984,
        ("p1",),
        (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),),
        interval_bounds=lambda self, *params: (-1.0, 1.0),
    )

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="interval_bounds must name its parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_varargs_overridden_validity_hook_is_rejected():
    """The base default legitimately takes *params, so only overrides are checked."""
    # --- arrange ----------------------
    cls = _formula_cls(983, ("p1",), (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),))
    cls.is_param_tuple_valid = lambda self, *params: True

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="is_param_tuple_valid must name its parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_unoverridden_validity_hook_is_not_checked():
    """A formula that does not override is_param_tuple_valid inherits the *params default, and is fine."""
    # --- arrange ----------------------
    cls = _formula_cls(982, ("p1",), (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),))

    # --- act / assert -----------------
    assert [c.id.param_values for c in cls().build_all_candidates()] == [(0.0,), (1.0,)]


@pytest.mark.usefixtures("isolated_formula_registry")
def test_declared_params_without_recipes_is_rejected():
    # --- arrange ----------------------
    cls = _formula_cls(986, ("p1",), ())

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="defines no recipes"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_formula_yielding_no_candidates_is_rejected():
    # --- arrange ----------------------
    cls = _formula_cls(985, ("p1",), (ParamGrid.decimal("p1", 0.0, 1.0, 1.0),))
    cls.is_param_tuple_valid = lambda self, p1: False

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="produced no candidates"):
        cls().build_all_candidates()


def test_every_catalog_formula_validates():
    """Guards the catalog itself: a malformed formula module fails here, not in a pipeline run."""
    for formula in FormulaRegistry.formulas():
        assert formula.build_all_candidates(), formula.name


# ==================================================================================================
#  compilation
# ==================================================================================================
def test_compiled_formula_is_cached_per_class():
    # --- arrange ----------------------
    first_instance, second_instance = Cubic(), Cubic()

    # --- act / assert -----------------
    assert first_instance._compiled_formula() is second_instance._compiled_formula()
    assert Cubic()._compiled_formula() is not OddPower()._compiled_formula()


@pytest.mark.usefixtures("isolated_formula_registry")
def test_compiled_formula_rejects_plain_method():
    # --- arrange ----------------------
    class PlainMethod(Formula):
        number = (99, 996)
        name = "Plain method"
        jit = False

        def parametrized_fun(self, x: float, c: float) -> float:  # not a staticmethod: rejected
            return x - c

        def interval_bounds(self) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return ()

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="staticmethod"):
        # the candidate defers compilation, so the guard fires on first callable use
        _ = PlainMethod().build_candidate(()).xc_fun


@pytest.mark.usefixtures("isolated_formula_registry")
def test_formula_without_jit_keeps_its_plain_python_function():
    """A formula with `jit = False` keeps its plain Python `parametrized_fun` as its compiled function."""
    # --- arrange ----------------------
    formula_cls = define_formula_cls((99, 994))

    # --- act / assert -----------------
    assert formula_cls()._compiled_formula() is formula_cls.parametrized_fun


@pytest.mark.usefixtures("isolated_formula_registry")
def test_bound_formula_calls_math_functions_inside_flop_counting():
    """A formula compiled when its first parameter tuple is bound runs inside the flop-counting context of a solve.

    That context replaces the `math` functions with counting wrappers, and numba cannot compile a call to such a
    wrapper, so the formula must be compiled before the context starts.
    """

    # --- arrange ----------------------
    class Sine(Formula):
        number = (99, 995)
        name = "Sine"

        @staticmethod
        def parametrized_fun(x: float, c: float) -> float:
            return math.sin(x) - c

        def interval_bounds(self) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return ()

    # compile another formula first, as the earlier solves of a run do, so that numba has loaded its registries
    # before `Sine` is bound
    Cubic().build_all_candidates()[0].xc_fun(0.0, 0.0)
    x_fun = Sine().bind_x_fun((), 0.25)

    # --- act --------------------------
    with FlopCountingContext():
        value = x_fun(0.5)

    # --- assert -----------------------
    assert value == pytest.approx(math.sin(0.5) - 0.25)


# ==================================================================================================
#  candidate_from_id / calibrated
# ==================================================================================================
def test_candidate_from_id_and_string():
    """A `ProblemId` and its rendered string rebuild the same calibrated test problem."""
    # --- act --------------------------
    problem_from_id = FormulaRegistry.candidate_from_id(ProblemId((2, 1, 1), ("p1",), (0.2,))).calibrated(-5.0, 5.0)
    problem_from_str = FormulaRegistry.candidate_from_id("f2.1.1[p1=0.2]").calibrated(-5.0, 5.0)

    # --- assert -----------------------
    for problem in (problem_from_id, problem_from_str):
        assert problem.id == ProblemId((2, 1, 1), ("p1",), (0.2,))
        assert (problem.a, problem.b, problem.c_min, problem.c_max) == (-2.0, 2.0, -5.0, 5.0)
        assert problem.xc_fun(2.0, 0.0) == pytest.approx(8.0 - 0.4)


def test_build_x_fun():
    """`build_x_fun` fixes `c` and returns the test problem's function as a function of `x` alone."""
    # --- arrange ----------------------
    problem = FormulaRegistry.candidate_from_id("f2.1.1[p1=0.0]").calibrated(-5.0, 5.0)

    # --- act --------------------------
    f = problem.build_x_fun(c=1.0)

    # --- assert -----------------------
    assert f(2.0) == pytest.approx(7.0)


def test_candidate_from_id_unknown_formula():
    """An id whose formula number is not registered raises `UnknownFormulaError`."""
    with pytest.raises(UnknownFormulaError):
        FormulaRegistry.candidate_from_id("f9.9[p1=0.2]")


def test_candidate_from_id_invalid_params():
    """An id whose parameter values fail the formula's validity criteria raises `InvalidParamsError`."""
    with pytest.raises(InvalidParamsError):
        FormulaRegistry.candidate_from_id(
            ProblemId((2, 1, 2), ("p1",), (2.0,))  # even power: invalid
        )


@pytest.mark.parametrize(
    "text",
    [
        "f2.1.1[slope=0.2]",  # wrong name
        "f2.1.1",  # parameter missing
        "f2.1.1[p1=0.2,p2=0.4]",  # extra parameter
    ],
)
def test_candidate_from_id_rejects_param_names_that_differ_from_the_formula(text):
    """An id whose parameter names differ from the formula's `param_names` is rejected."""
    with pytest.raises(InvalidParamsError, match="do not match"):
        FormulaRegistry.candidate_from_id(text)


def test_catalog_brackets_change_sign_within_c_range():
    # --- arrange ----------------------
    problem = FormulaRegistry.candidate_from_id("f2.1.2[p1=5.0]").calibrated(-1.0, 1.0)

    # --- act / assert -----------------
    for c in (-1.0, 0.0, 1.0):
        assert problem.xc_fun(problem.a, c) * problem.xc_fun(problem.b, c) < 0
