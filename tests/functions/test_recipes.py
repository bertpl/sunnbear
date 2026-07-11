import pytest

from sunnbear.functions import ParamAxis, ParamRecipe, Spacing


# ==================================================================================================
#  ParamAxis
# ==================================================================================================
def test_axis_linear_values_are_grid_rounded():
    # --- arrange ----------------------
    axis = ParamAxis("p1", 0.0, 1.0, step=0.2)

    # --- act / assert -----------------
    assert axis.values() == (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)


def test_axis_log2_values():
    # --- arrange ----------------------
    axis = ParamAxis("p1", 0.0, 2.0, step=1.0, spacing=Spacing.LOG2)

    # --- act / assert -----------------
    assert axis.values() == (1.0, 2.0, 4.0)


def test_axis_log10_values():
    # --- arrange ----------------------
    axis = ParamAxis("p1", -1.0, 1.0, step=1.0, spacing=Spacing.LOG10)

    # --- act / assert -----------------
    assert axis.values() == (0.1, 1.0, 10.0)


def test_axis_single_point():
    assert ParamAxis("p1", 3.0, 3.0, step=1.0).values() == (3.0,)


@pytest.mark.parametrize("start, stop, step", [(0.0, 1.0, 0.0), (0.0, 1.0, -0.1), (2.0, 1.0, 0.5)])
def test_axis_rejects_bad_grid(start, stop, step):
    with pytest.raises(ValueError):
        ParamAxis("p1", start, stop, step)


# ==================================================================================================
#  ParamRecipe
# ==================================================================================================
def test_recipe_product():
    # --- arrange ----------------------
    recipe = ParamRecipe(axes=(ParamAxis("p1", 0.0, 1.0, 1.0), ParamAxis("p2", 5.0, 6.0, 1.0)))

    # --- act / assert -----------------
    assert list(recipe.tuples()) == [(0.0, 5.0), (0.0, 6.0), (1.0, 5.0), (1.0, 6.0)]


def test_recipe_joint_sweep():
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(ParamAxis("p1", 0.0, 1.0, 1.0), ParamAxis("p2", 5.0, 6.0, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert list(recipe.tuples()) == [(0.0, 5.0), (1.0, 6.0)]


def test_recipe_joint_sweep_rejects_unequal_lengths():
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(ParamAxis("p1", 0.0, 2.0, 1.0), ParamAxis("p2", 5.0, 6.0, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    with pytest.raises(ValueError):
        list(recipe.tuples())


def test_recipe_single_axis_convenience():
    # --- arrange / act ----------------
    recipe = ParamRecipe.log2("p1", 0.0, 1.0, step=0.5)

    # --- assert -----------------------
    assert recipe.param_names() == ("p1",)
    assert list(recipe.tuples()) == [(1.0,), (2**0.5,), (2.0,)]
