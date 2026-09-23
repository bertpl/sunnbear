import pytest

from sunnbear._core.functions.catalog.c02_standard_function_families.c01_polynomials.f01_cubic import Cubic
from sunnbear._core.functions.catalog.c02_standard_function_families.c01_polynomials.f02_odd_power import OddPower
from sunnbear.exceptions import InvalidParamsError, UnknownFormulaError
from sunnbear.functions import (
    Formula,
    FormulaRegistry,
    FunctionId,
    ParamAxis,
    ParamRecipe,
    ParamValue,
)

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
    """Both compilation paths (jitted cubic, plain odd power) produce working f(x, c) callables."""
    # --- arrange ----------------------
    candidate = formula_cls().build_all_candidates()[0]  # p1 = 0.0 resp. 1.0

    # --- act / assert -----------------
    assert candidate.xc_fun(2.0, 1.0) == pytest.approx(candidate.xc_fun(2.0, 0.0) - 1.0)


@pytest.mark.usefixtures("isolated_registry")
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
            return (ParamRecipe.decimal("p1", 0.0, 1.0, 0.5), ParamRecipe.decimal("p1", 0.5, 1.5, 0.5))

    # --- act --------------------------
    params = [c.id.param_values for c in DupTest().build_all_candidates()]

    # --- assert -----------------------
    assert params == [(0.0,), (0.5,), (1.0,), (1.5,)]


# ==================================================================================================
#  registration
# ==================================================================================================
@pytest.mark.usefixtures("isolated_registry")
def test_subclass_definition_registers():
    # --- arrange / act ----------------
    cls = define_formula_cls((99, 998))

    # --- assert -----------------------
    assert any(type(f) is cls for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_registry")
def test_defining_a_non_positive_number_is_rejected_at_class_definition():
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="only positive integers"):
        define_formula_cls((99, 0))


@pytest.mark.usefixtures("isolated_registry")
def test_zero_param_formula_yields_exactly_one_candidate():
    """A formula without parameters materializes the single empty tuple, once."""
    # --- act --------------------------
    candidates = define_formula_cls((99, 992))().build_all_candidates()

    # --- assert -----------------------
    assert len(candidates) == 1
    assert candidates[0].id.params == ()
    assert str(candidates[0].id) == "f99.992"


def test_registry_holds_one_instance_per_formula():
    """Enumeration and reconstruction hand out the same registered instance."""
    # --- act --------------------------
    [enumerated] = [f for f in FormulaRegistry.formulas() if type(f) is Cubic]
    candidate_a = FormulaRegistry.candidate_from_id("f2.1.1-0.2")
    candidate_b = FormulaRegistry.candidate_from_id("f2.1.1-0.4")

    # --- assert -----------------------
    assert candidate_a.formula is candidate_b.formula is enumerated


@pytest.mark.usefixtures("isolated_registry")
def test_formulas_defined_after_first_use_are_registered():
    """A formula defined after a call to `formulas()` appears in the next call: registration is at class definition."""
    # --- arrange ----------------------
    FormulaRegistry.formulas()

    # --- act --------------------------
    cls = define_formula_cls((99, 994))

    # --- assert -----------------------
    assert any(type(f) is cls for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_registry")
def test_abstract_intermediates_are_not_registered():
    # --- arrange ----------------------
    class PolynomialBase(Formula):
        """Abstract intermediate: adds no hooks, implements none."""

    # --- act / assert -----------------
    assert all(type(f) is not PolynomialBase for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_registry")
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
            # a DECIMAL axis hits 4.0 as "4.0"; a POW2 axis hits it as "2^2.0" — same value, different notation
            return (ParamRecipe.decimal("p1", 4.0, 4.0, 1.0), ParamRecipe.pow2("p1", 2.0, 2.0, 1.0))

    # --- act --------------------------
    ids = [c.id for c in CrossNotation().build_all_candidates()]

    # --- assert -----------------------
    assert [str(fid) for fid in ids] == ["f99.995-4.0"]  # first-seen notation wins


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


@pytest.mark.usefixtures("isolated_registry")
def test_recipe_axis_order_must_match_declared_params():
    """Transposed axes would silently swap parameter values, so they must be rejected."""
    # --- arrange ----------------------
    transposed = ParamRecipe(axes=(ParamAxis("p2", 7.0, 7.0, 1.0), ParamAxis("p1", 3.0, 3.0, 1.0)))
    cls = _formula_cls(
        990,
        ("p1", "p2"),
        (transposed,),
        fun=lambda x, c, p1, p2: x - c,
    )

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="recipe axes must match the declared parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_recipe_arity_must_match_declared_params():
    # --- arrange ----------------------
    cls = _formula_cls(989, ("p1", "p2"), (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),), fun=lambda x, c, p1, p2: x - c)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="recipe axes must match the declared parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_declared_params_must_match_parametrized_fun_signature():
    # --- arrange ----------------------
    cls = _formula_cls(988, ("p1",), (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),), fun=lambda x, c, other: x - c)

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="parametrized_fun takes"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_declared_params_must_match_interval_bounds_signature():
    """Right arity but wrong names in interval_bounds is drift too — the cross-check covers every hook."""
    # --- arrange ----------------------
    cls = _formula_cls(
        981,
        ("p1",),
        (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),),
        interval_bounds=lambda self, other: (-1.0, 1.0),
    )

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="interval_bounds takes"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_declared_params_must_match_overridden_validity_hook_signature():
    # --- arrange ----------------------
    cls = _formula_cls(980, ("p1",), (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),))
    cls.is_param_tuple_valid = lambda self, other: True

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="is_param_tuple_valid takes"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_varargs_parametrized_fun_is_rejected():
    """Hooks must name their parameters, so declaration/implementation/recipes stay cross-checkable."""
    # --- arrange ----------------------
    cls = _formula_cls(987, ("p1",), (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),), fun=lambda x, c, *params: x - c)

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="must name its parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_varargs_interval_bounds_is_rejected():
    # --- arrange ----------------------
    cls = _formula_cls(
        984,
        ("p1",),
        (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),),
        interval_bounds=lambda self, *params: (-1.0, 1.0),
    )

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="interval_bounds must name its parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_varargs_overridden_validity_hook_is_rejected():
    """The base default legitimately takes *params, so only overrides are checked."""
    # --- arrange ----------------------
    cls = _formula_cls(983, ("p1",), (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),))
    cls.is_param_tuple_valid = lambda self, *params: True

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="is_param_tuple_valid must name its parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_unoverridden_validity_hook_is_not_checked():
    """A formula that does not override is_param_tuple_valid inherits the *params default, and is fine."""
    # --- arrange ----------------------
    cls = _formula_cls(982, ("p1",), (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),))

    # --- act / assert -----------------
    assert [c.id.param_values for c in cls().build_all_candidates()] == [(0.0,), (1.0,)]


@pytest.mark.usefixtures("isolated_registry")
def test_declared_params_without_recipes_is_rejected():
    # --- arrange ----------------------
    cls = _formula_cls(986, ("p1",), ())

    # --- act / assert -----------------
    with pytest.raises(ValueError, match="defines no recipes"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_formula_yielding_no_candidates_is_rejected():
    # --- arrange ----------------------
    cls = _formula_cls(985, ("p1",), (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),))
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


@pytest.mark.usefixtures("isolated_registry")
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


# ==================================================================================================
#  candidate_from_id / calibrated
# ==================================================================================================
def test_candidate_from_id_and_string():
    # --- act --------------------------
    tf_from_id = FormulaRegistry.candidate_from_id(FunctionId((2, 1, 1), (ParamValue.decimal(0.2),))).calibrated(
        -5.0, 5.0
    )
    tf_from_str = FormulaRegistry.candidate_from_id("f2.1.1-0.2").calibrated(-5.0, 5.0)

    # --- assert -----------------------
    for tf in (tf_from_id, tf_from_str):
        assert tf.id == FunctionId((2, 1, 1), (ParamValue.decimal(0.2),))
        assert (tf.a, tf.b, tf.c_min, tf.c_max) == (-2.0, 2.0, -5.0, 5.0)
        assert tf.xc_fun(2.0, 0.0) == pytest.approx(8.0 - 0.4)


def test_build_x_fun():
    # --- arrange ----------------------
    tf = FormulaRegistry.candidate_from_id("f2.1.1-0.0").calibrated(-5.0, 5.0)

    # --- act --------------------------
    f = tf.build_x_fun(c=1.0)

    # --- assert -----------------------
    assert f(2.0) == pytest.approx(7.0)


def test_candidate_from_id_unknown_formula():
    with pytest.raises(UnknownFormulaError):
        FormulaRegistry.candidate_from_id("f9.9-0.2")


def test_candidate_from_id_invalid_params():
    with pytest.raises(InvalidParamsError):
        FormulaRegistry.candidate_from_id(FunctionId((2, 1, 2), (ParamValue.decimal(2.0),)))  # even power: invalid


def test_catalog_brackets_change_sign_within_c_range():
    # --- arrange ----------------------
    tf = FormulaRegistry.candidate_from_id("f2.1.2-5.0").calibrated(-1.0, 1.0)

    # --- act / assert -----------------
    for c in (-1.0, 0.0, 1.0):
        assert tf.xc_fun(tf.a, c) * tf.xc_fun(tf.b, c) < 0
