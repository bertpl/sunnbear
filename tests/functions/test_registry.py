import pytest

import sunnbear.functions._formula as formula_module
from sunnbear.errors import InvalidParamsError, UnknownFormulaError
from sunnbear.functions import (
    Formula,
    FormulaRegistry,
    FunctionId,
    ParamAxis,
    ParamRecipe,
    ParamValue,
)
from sunnbear.functions.catalog.f1xx_polynomials.f101_cubic import F101_Cubic
from sunnbear.functions.catalog.f1xx_polynomials.f102_odd_power import F102_OddPower


@pytest.fixture
def isolated_registry(monkeypatch):
    """Snapshot the auto-registration list and reset the registry's populated state.

    Test-defined Formula subclasses don't leak past the test, and each test sees a
    fresh population (so its own subclasses are discovered despite the snapshot
    semantics of `FormulaRegistry._ensure_registry_populated`).
    """
    monkeypatch.setattr(formula_module, "registered_formula_classes", list(formula_module.registered_formula_classes))
    monkeypatch.setattr(FormulaRegistry, "_formulas", None)
    monkeypatch.setattr(FormulaRegistry, "_formulas_by_number", None)


# ==================================================================================================
#  formulas / candidates
# ==================================================================================================
def test_formulas_contains_catalog_sorted():
    # --- act --------------------------
    registered = FormulaRegistry.formulas()

    # --- assert -----------------------
    assert [f.number for f in registered] == sorted(f.number for f in registered)
    assert {type(f) for f in registered} >= {F101_Cubic, F102_OddPower}


def test_candidates_materializes_recipe_grid():
    # --- act --------------------------
    cubic_candidates = list(F101_Cubic().build_all_candidates())

    # --- assert -----------------------
    assert [c.id.param_values for c in cubic_candidates] == [(0.0,), (0.2,), (0.4,), (0.6,), (0.8,), (1.0,)]
    assert all(c.id.formula == F101_Cubic.number for c in cubic_candidates)
    assert all((c.a, c.b) == (-2.0, 2.0) for c in cubic_candidates)


def test_candidates_applies_validity_filter():
    # --- act --------------------------
    odd_candidates = list(F102_OddPower().build_all_candidates())

    # --- assert -----------------------
    assert [c.id.param_values for c in odd_candidates] == [(1.0,), (3.0,), (5.0,), (7.0,)]


@pytest.mark.parametrize("formula_cls", [F101_Cubic, F102_OddPower])
def test_candidates_functions_evaluate(formula_cls):
    """Both compilation paths (jitted f101, plain f102) produce working f(x, c) callables."""
    # --- arrange ----------------------
    candidate = formula_cls().build_all_candidates()[0]  # p1 = 0.0 resp. 1.0

    # --- act / assert -----------------
    assert candidate.xc_fun(2.0, 1.0) == pytest.approx(candidate.xc_fun(2.0, 0.0) - 1.0)


@pytest.mark.usefixtures("isolated_registry")
def test_candidates_deduplicates_across_recipes():
    # --- arrange ----------------------
    class DupTest(Formula):
        number = 999
        name = "dup_test"
        param_names = ("p1",)
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float, p1: float) -> float:
            return x - c

        def bracket(self, p1: float) -> tuple[float, float]:
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
def _minimal_formula_cls(formula_number: int) -> type[Formula]:
    class Minimal(Formula):
        number = formula_number
        name = f"minimal_{formula_number}"
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float) -> float:
            return x - c

        def bracket(self) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return ()

    return Minimal


@pytest.mark.usefixtures("isolated_registry")
def test_subclass_definition_registers():
    # --- arrange / act ----------------
    cls = _minimal_formula_cls(998)

    # --- assert -----------------------
    assert any(type(f) is cls for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_registry")
def test_formulas_rejects_duplicate_numbers():
    # --- arrange ----------------------
    _minimal_formula_cls(997)
    _minimal_formula_cls(997)

    # --- act / assert -----------------
    with pytest.raises(ValueError):
        FormulaRegistry.formulas()


@pytest.mark.usefixtures("isolated_registry")
def test_formulas_rejects_non_positive_number():
    # --- arrange ----------------------
    _minimal_formula_cls(0)

    # --- act / assert -----------------
    with pytest.raises(ValueError):
        FormulaRegistry.formulas()


def test_registry_population_is_a_snapshot():
    """Accessors reuse one population: same tuple, and reconstruction hands out the same instances."""
    # --- act --------------------------
    first, second = FormulaRegistry.formulas(), FormulaRegistry.formulas()
    candidate_a = FormulaRegistry.candidate_from_id("f101-0.2")
    candidate_b = FormulaRegistry.candidate_from_id("f101-0.4")

    # --- assert -----------------------
    assert first is second
    assert candidate_a.formula is candidate_b.formula  # dict hit, not a fresh enumeration


@pytest.mark.usefixtures("isolated_registry")
def test_formulas_defined_after_first_use_are_not_discovered():
    """The snapshot is taken on first accessor call; late definitions are deliberately unsupported."""
    # --- arrange ----------------------
    FormulaRegistry.formulas()  # take the snapshot

    # --- act --------------------------
    cls = _minimal_formula_cls(994)

    # --- assert -----------------------
    assert all(type(f) is not cls for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_registry")
def test_abstract_intermediates_are_not_instantiated():
    # --- arrange ----------------------
    class PolynomialBase(Formula):
        """Abstract intermediate: adds no hooks, implements none."""

    # --- act / assert -----------------
    assert all(type(f) is not PolynomialBase for f in FormulaRegistry.formulas())


@pytest.mark.usefixtures("isolated_registry")
def test_candidates_deduplicates_across_notations():
    # --- arrange ----------------------
    class CrossNotation(Formula):
        number = 995
        name = "cross_notation"
        param_names = ("p1",)
        jit = False

        @staticmethod
        def parametrized_fun(x: float, c: float, p1: float) -> float:
            return x - c

        def bracket(self, p1: float) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            # a DECIMAL axis hits 4.0 as "4.0"; a POW2 axis hits it as "2^2.0" — same value, different notation
            return (ParamRecipe.decimal("p1", 4.0, 4.0, 1.0), ParamRecipe.pow2("p1", 2.0, 2.0, 1.0))

    # --- act --------------------------
    ids = [c.id for c in CrossNotation().build_all_candidates()]

    # --- assert -----------------------
    assert [str(fid) for fid in ids] == ["f995-4.0"]  # first-seen notation wins


# ==================================================================================================
#  recipe validation
# ==================================================================================================
def _formula_cls(number: int, declared: tuple[str, ...], recipes: tuple, fun=None, bracket=None):
    """Build a throwaway Formula whose declaration and recipes can be varied independently."""
    namespace = {
        "number": number,
        "name": f"varying_{number}",
        "param_names": declared,
        "jit": False,
        "parametrized_fun": staticmethod(fun or (lambda x, c, p1: x - c)),
        "bracket": bracket or (lambda self, p1: (-1.0, 1.0)),
        "recipes": lambda self: recipes,
    }
    return type(f"Varying{number}", (Formula,), namespace)


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
def test_varargs_parametrized_fun_is_rejected():
    """Hooks must name their parameters, so declaration/implementation/recipes stay cross-checkable."""
    # --- arrange ----------------------
    cls = _formula_cls(987, ("p1",), (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),), fun=lambda x, c, *params: x - c)

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="must name its parameters"):
        cls().build_all_candidates()


@pytest.mark.usefixtures("isolated_registry")
def test_varargs_bracket_is_rejected():
    # --- arrange ----------------------
    cls = _formula_cls(
        984,
        ("p1",),
        (ParamRecipe.decimal("p1", 0.0, 1.0, 1.0),),
        bracket=lambda self, *params: (-1.0, 1.0),
    )

    # --- act / assert -----------------
    with pytest.raises(TypeError, match="bracket must name its parameters"):
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
    first_instance, second_instance = F101_Cubic(), F101_Cubic()

    # --- act / assert -----------------
    assert first_instance._compiled_formula() is second_instance._compiled_formula()
    assert F101_Cubic()._compiled_formula() is not F102_OddPower()._compiled_formula()


@pytest.mark.usefixtures("isolated_registry")
def test_compiled_formula_rejects_plain_method():
    # --- arrange ----------------------
    class PlainMethod(Formula):
        number = 996
        name = "plain_method"
        jit = False

        def parametrized_fun(self, x: float, c: float) -> float:  # not a staticmethod: rejected
            return x - c

        def bracket(self) -> tuple[float, float]:
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
    tf_from_id = FormulaRegistry.candidate_from_id(FunctionId(101, (ParamValue.decimal(0.2),))).calibrated(-5.0, 5.0)
    tf_from_str = FormulaRegistry.candidate_from_id("f101-0.2").calibrated(-5.0, 5.0)

    # --- assert -----------------------
    for tf in (tf_from_id, tf_from_str):
        assert tf.id == FunctionId(101, (ParamValue.decimal(0.2),))
        assert (tf.a, tf.b, tf.c_min, tf.c_max) == (-2.0, 2.0, -5.0, 5.0)
        assert tf.xc_fun(2.0, 0.0) == pytest.approx(8.0 - 0.4)


def test_build_x_fun():
    # --- arrange ----------------------
    tf = FormulaRegistry.candidate_from_id("f101-0.0").calibrated(-5.0, 5.0)

    # --- act --------------------------
    f = tf.build_x_fun(c=1.0)

    # --- assert -----------------------
    assert f(2.0) == pytest.approx(7.0)


def test_candidate_from_id_unknown_formula():
    with pytest.raises(UnknownFormulaError):
        FormulaRegistry.candidate_from_id("f900-0.2")


def test_candidate_from_id_invalid_params():
    with pytest.raises(InvalidParamsError):
        FormulaRegistry.candidate_from_id(FunctionId(102, (ParamValue.decimal(2.0),)))  # even power: invalid


def test_catalog_brackets_change_sign_within_c_range():
    # --- arrange ----------------------
    tf = FormulaRegistry.candidate_from_id("f102-5.0").calibrated(-1.0, 1.0)

    # --- act / assert -----------------
    for c in (-1.0, 0.0, 1.0):
        assert tf.xc_fun(tf.a, c) * tf.xc_fun(tf.b, c) < 0
