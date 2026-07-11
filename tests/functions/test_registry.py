import pytest

from sunnbear.errors import InvalidParamsError, UnknownFormulaError
from sunnbear.functions import FunctionId, build, candidates, formulas
from sunnbear.functions.examples import CUBIC, ODD_POWER


# ==================================================================================================
#  formulas / candidates
# ==================================================================================================
def test_formulas_contains_examples_sorted():
    # --- act --------------------------
    registered = formulas()

    # --- assert -----------------------
    assert [f.number for f in registered] == sorted(f.number for f in registered)
    assert CUBIC in registered
    assert ODD_POWER in registered


def test_candidates_materializes_recipe_grid():
    # --- act --------------------------
    cubic_candidates = list(candidates(CUBIC))

    # --- assert -----------------------
    assert [c.id.params for c in cubic_candidates] == [(0.0,), (0.2,), (0.4,), (0.6,), (0.8,), (1.0,)]
    assert all(c.id.formula == CUBIC.number for c in cubic_candidates)
    assert all((c.a, c.b) == (-2.0, 2.0) for c in cubic_candidates)


def test_candidates_applies_validity_filter():
    # --- act --------------------------
    odd_candidates = list(candidates(ODD_POWER))

    # --- assert -----------------------
    assert [c.id.params for c in odd_candidates] == [(1.0,), (3.0,), (5.0,), (7.0,)]


def test_candidates_functions_evaluate():
    # --- arrange ----------------------
    candidate = next(iter(candidates(CUBIC)))  # p1 = 0.0

    # --- act / assert -----------------
    assert candidate.fun(2.0, 0.0) == pytest.approx(8.0)
    assert candidate.fun(2.0, 1.0) == pytest.approx(7.0)


def test_candidates_deduplicates_across_recipes():
    # --- arrange ----------------------
    from sunnbear.functions import Formula, ParamRecipe

    formula = Formula(
        number=999,
        name="dup_test",
        make=lambda p1: (lambda x, c: x - c),
        bracket=lambda p1: (-1.0, 1.0),
        param_names=("p1",),
        recipes=(ParamRecipe.linear("p1", 0.0, 1.0, 0.5), ParamRecipe.linear("p1", 0.5, 1.5, 0.5)),
    )

    # --- act --------------------------
    params = [c.id.params for c in candidates(formula)]

    # --- assert -----------------------
    assert params == [(0.0,), (0.5,), (1.0,), (1.5,)]


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


def test_example_brackets_change_sign_within_c_range():
    # --- arrange ----------------------
    tf = build("f102-5.0", c_range=(-1.0, 1.0))

    # --- act / assert -----------------
    for c in (-1.0, 0.0, 1.0):
        assert tf.fun(tf.a, c) * tf.fun(tf.b, c) < 0
