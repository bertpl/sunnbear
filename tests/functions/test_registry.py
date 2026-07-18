import pytest

import sunnbear.functions._formula as formula_module
from sunnbear.errors import InvalidParamsError, UnknownFormulaError
from sunnbear.functions import Formula, FunctionId, ParamRecipe, build, candidates, formulas
from sunnbear.functions.catalog.f1xx_polynomials.f101_cubic import F101_Cubic
from sunnbear.functions.catalog.f1xx_polynomials.f102_odd_power import F102_OddPower


@pytest.fixture
def isolated_registry(monkeypatch):
    """Snapshot the auto-registration list so test-defined Formula subclasses don't leak."""
    monkeypatch.setattr(formula_module, "registered_formula_classes", list(formula_module.registered_formula_classes))


# ==================================================================================================
#  formulas / candidates
# ==================================================================================================
def test_formulas_contains_catalog_sorted():
    # --- act --------------------------
    registered = formulas()

    # --- assert -----------------------
    assert [f.number for f in registered] == sorted(f.number for f in registered)
    assert {type(f) for f in registered} >= {F101_Cubic, F102_OddPower}


def test_candidates_materializes_recipe_grid():
    # --- act --------------------------
    cubic_candidates = list(candidates(F101_Cubic()))

    # --- assert -----------------------
    assert [c.id.params for c in cubic_candidates] == [(0.0,), (0.2,), (0.4,), (0.6,), (0.8,), (1.0,)]
    assert all(c.id.formula == F101_Cubic.number for c in cubic_candidates)
    assert all((c.a, c.b) == (-2.0, 2.0) for c in cubic_candidates)


def test_candidates_applies_validity_filter():
    # --- act --------------------------
    odd_candidates = list(candidates(F102_OddPower()))

    # --- assert -----------------------
    assert [c.id.params for c in odd_candidates] == [(1.0,), (3.0,), (5.0,), (7.0,)]


@pytest.mark.parametrize("formula_cls", [F101_Cubic, F102_OddPower])
def test_candidates_functions_evaluate(formula_cls):
    """Both compilation paths (jitted f101, plain f102) produce working f(x, c) callables."""
    # --- arrange ----------------------
    candidate = next(iter(candidates(formula_cls())))  # p1 = 0.0 resp. 1.0

    # --- act / assert -----------------
    assert candidate.fun(2.0, 1.0) == pytest.approx(candidate.fun(2.0, 0.0) - 1.0)


@pytest.mark.usefixtures("isolated_registry")
def test_candidates_deduplicates_across_recipes():
    # --- arrange ----------------------
    class DupTest(Formula):
        number = 999
        name = "dup_test"
        jit = False

        def make_fun(self, p1: float):
            return lambda x, c: x - c

        def bracket(self, p1: float) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return (ParamRecipe.linear("p1", 0.0, 1.0, 0.5), ParamRecipe.linear("p1", 0.5, 1.5, 0.5))

    # --- act --------------------------
    params = [c.id.params for c in candidates(DupTest())]

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

        def make_fun(self, *params: float):
            return lambda x, c: x - c

        def bracket(self, *params: float) -> tuple[float, float]:
            return (-1.0, 1.0)

        def recipes(self) -> tuple[ParamRecipe, ...]:
            return ()

    return Minimal


@pytest.mark.usefixtures("isolated_registry")
def test_subclass_definition_registers():
    # --- arrange / act ----------------
    cls = _minimal_formula_cls(998)

    # --- assert -----------------------
    assert any(type(f) is cls for f in formulas())


@pytest.mark.usefixtures("isolated_registry")
def test_formulas_rejects_duplicate_numbers():
    # --- arrange ----------------------
    _minimal_formula_cls(997)
    _minimal_formula_cls(997)

    # --- act / assert -----------------
    with pytest.raises(ValueError):
        formulas()


@pytest.mark.usefixtures("isolated_registry")
def test_formulas_rejects_non_positive_number():
    # --- arrange ----------------------
    _minimal_formula_cls(0)

    # --- act / assert -----------------
    with pytest.raises(ValueError):
        formulas()


@pytest.mark.usefixtures("isolated_registry")
def test_abstract_intermediates_are_not_instantiated():
    # --- arrange ----------------------
    class PolynomialBase(Formula):
        """Abstract intermediate: adds no hooks, implements none."""

    # --- act / assert -----------------
    assert all(type(f) is not PolynomialBase for f in formulas())


# ==================================================================================================
#  build
# ==================================================================================================
def test_build_from_id_and_string():
    # --- act --------------------------
    tf_from_id = build(FunctionId(101, (0.2,)), c_range=(-5.0, 5.0))
    tf_from_str = build("f101-0.2", c_range=(-5.0, 5.0))

    # --- assert -----------------------
    for tf in (tf_from_id, tf_from_str):
        assert tf.id == FunctionId(101, (0.2,))
        assert (tf.a, tf.b, tf.c_min, tf.c_max) == (-2.0, 2.0, -5.0, 5.0)
        assert tf.fun(2.0, 0.0) == pytest.approx(8.0 - 0.4)


def test_build_bind():
    # --- arrange ----------------------
    tf = build("f101-0.0", c_range=(-5.0, 5.0))

    # --- act --------------------------
    f = tf.bind(c=1.0)

    # --- assert -----------------------
    assert f(2.0) == pytest.approx(7.0)


def test_build_unknown_formula():
    with pytest.raises(UnknownFormulaError):
        build("f900-0.2", c_range=(-1.0, 1.0))


def test_build_invalid_params():
    with pytest.raises(InvalidParamsError):
        build(FunctionId(102, (2.0,)), c_range=(-1.0, 1.0))  # even power: invalid


def test_catalog_brackets_change_sign_within_c_range():
    # --- arrange ----------------------
    tf = build("f102-5.0", c_range=(-1.0, 1.0))

    # --- act / assert -----------------
    for c in (-1.0, 0.0, 1.0):
        assert tf.fun(tf.a, c) * tf.fun(tf.b, c) < 0
