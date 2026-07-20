import itertools

import pytest

from sunnbear.functions import DecimalParamValue, ExponentialParamValue, ParamAxis, ParamRecipe, ParamSpacing


# ==================================================================================================
#  ParamAxis
# ==================================================================================================
def test_axis_linear_values_are_grid_rounded():
    # --- arrange ----------------------
    axis = ParamAxis("p1", 0.0, 1.0, step=0.2)

    # --- act / assert -----------------
    assert tuple(v.value for v in axis.values()) == (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
    assert all(isinstance(v, DecimalParamValue) for v in axis.values())


def test_axis_log2_values():
    # --- arrange ----------------------
    axis = ParamAxis("p1", 0.0, 2.0, step=1.0, spacing=ParamSpacing.LOG2)

    # --- act / assert -----------------
    assert tuple(v.value for v in axis.values()) == (1.0, 2.0, 4.0)
    assert all(isinstance(v, ExponentialParamValue) for v in axis.values())
    assert [v.display() for v in axis.values()] == ["2^0.0", "2^1.0", "2^2.0"]


def test_axis_log10_values():
    # --- arrange ----------------------
    axis = ParamAxis("p1", -1.0, 1.0, step=1.0, spacing=ParamSpacing.LOG10)

    # --- act / assert -----------------
    assert tuple(v.value for v in axis.values()) == (0.1, 1.0, 10.0)
    assert [v.display() for v in axis.values()] == ["10^-1.0", "10^0.0", "10^1.0"]


def test_axis_single_point():
    assert tuple(v.value for v in ParamAxis("p1", 3.0, 3.0, step=1.0).values()) == (3.0,)


@pytest.mark.parametrize("value", [1e-05, -1e-05, 1e16, -3.5, 0.0])
def test_axis_single_point_preserves_value_exactly(value):
    """Values whose repr uses exponent notation must survive materialization intact."""
    assert tuple(v.value for v in ParamAxis("p1", value, value, step=1.0).values()) == (value,)


@pytest.mark.parametrize(
    "start, stop, step",
    [(-1e-05, -1e-05, 1.0), (1e-09, 1e-09, 1.0), (0.0, 0.0, 1.0), (-1.0, -1.0, 0.25)],
)
def test_axis_never_yields_an_empty_grid(start, stop, step):
    """An empty grid would make coupled sweeps index out of range."""
    assert len(ParamAxis("p1", start, stop, step).values()) >= 1


def test_coupled_sweep_with_tiny_magnitude_axis():
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(ParamAxis("p1", 0.0, 2.0, 1.0), ParamAxis("p2", -1e-05, -1e-05, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert [tuple(v.value for v in p) for p in recipe.tuples()] == [
        (0.0, -1e-05),
        (1.0, -1e-05),
        (2.0, -1e-05),
    ]


@pytest.mark.parametrize(
    "start, stop, step",
    [
        (0.0, 1.0, 0.0),  # step not positive
        (0.0, 1.0, -0.1),  # step not positive
        (2.0, 1.0, 0.5),  # stop before start
        (0.0, 0.9, 0.2),  # grid would not land on stop (0.9 / 0.2 = 4.5)
        (0.05, 0.85, 0.2),  # start carries a finer decimal than the step
    ],
)
def test_axis_rejects_bad_grid(start, stop, step):
    with pytest.raises(ValueError):
        ParamAxis("p1", start, stop, step)


def test_axis_forgives_float_noise_in_endpoints():
    """Decimal places are counted on the canonical form, so noise the snap erases can't fail the check."""
    # --- arrange ----------------------
    noisy_stop = 0.1 + 0.2  # 0.30000000000000004: 17 raw decimal places, 1 canonical

    # --- act --------------------------
    axis = ParamAxis("p1", 0.0, noisy_stop, step=0.1)

    # --- assert -----------------------
    assert tuple(v.value for v in axis.values()) == (0.0, 0.1, 0.2, 0.3)


def test_axis_accepts_offset_but_clean_grid():
    """An offset lattice (1,3,5,7 on step 2) is valid: the endpoints are no finer than the step."""
    # --- act --------------------------
    values = tuple(v.value for v in ParamAxis("p1", 1.0, 7.0, 2.0).values())

    # --- assert -----------------------
    assert values == (1.0, 3.0, 5.0, 7.0)


# ==================================================================================================
#  ParamRecipe
# ==================================================================================================
def test_recipe_product():
    # --- arrange ----------------------
    recipe = ParamRecipe(axes=(ParamAxis("p1", 0.0, 1.0, 1.0), ParamAxis("p2", 5.0, 6.0, 1.0)))

    # --- act / assert -----------------
    assert [tuple(v.value for v in p) for p in recipe.tuples()] == [(0.0, 5.0), (0.0, 6.0), (1.0, 5.0), (1.0, 6.0)]


def test_recipe_coupled_sweep_same_lengths():
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(ParamAxis("p1", 0.0, 1.0, 1.0), ParamAxis("p2", 5.0, 6.0, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert [tuple(v.value for v in p) for p in recipe.tuples()] == [(0.0, 5.0), (1.0, 6.0)]


def test_recipe_coupled_sweep_unequal_lengths():
    """Axes advance one coordinate at a time along a shared axis; lengths need not match."""
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(ParamAxis("p1", 0.0, 4.0, 1.0), ParamAxis("p2", 0.0, 2.0, 1.0)),  # 5 values, 3 values
        product=False,
    )

    # --- act --------------------------
    tuples = [tuple(v.value for v in p) for p in recipe.tuples()]

    # --- assert -----------------------
    assert tuples == [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0), (3.0, 2.0), (4.0, 2.0)]


@pytest.mark.parametrize("n_p1, n_p2", [(5, 3), (32, 50), (101, 11), (7, 7), (2, 9)])
def test_recipe_coupled_sweep_covers_every_value(n_p1, n_p2):
    """No axis ever loses a value, and consecutive tuples differ in exactly the stepping axes."""
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(ParamAxis("p1", 0.0, float(n_p1 - 1), 1.0), ParamAxis("p2", 0.0, float(n_p2 - 1), 1.0)),
        product=False,
    )

    # --- act --------------------------
    tuples = [tuple(v.value for v in p) for p in recipe.tuples()]

    # --- assert -----------------------
    assert {t[0] for t in tuples} == {float(i) for i in range(n_p1)}  # every p1 value appears
    assert {t[1] for t in tuples} == {float(i) for i in range(n_p2)}  # every p2 value appears
    assert max(n_p1, n_p2) <= len(tuples) <= (n_p1 - 1) + (n_p2 - 1) + 1
    assert all(a != b for a, b in itertools.pairwise(tuples))  # no repeats
    assert all(a <= b for a, b in itertools.pairwise(tuples))  # monotone in both axes


def test_recipe_coupled_sweep_equal_lengths_is_a_zip():
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(ParamAxis("p1", 0.0, 3.0, 1.0), ParamAxis("p2", 10.0, 13.0, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert [tuple(v.value for v in p) for p in recipe.tuples()] == [
        (0.0, 10.0),
        (1.0, 11.0),
        (2.0, 12.0),
        (3.0, 13.0),
    ]


def test_recipe_coupled_sweep_all_single_value_axes():
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(ParamAxis("p1", 3.0, 3.0, 1.0), ParamAxis("p2", 7.0, 7.0, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert [tuple(v.value for v in p) for p in recipe.tuples()] == [(3.0, 7.0)]


def test_recipe_coupled_sweep_three_axes():
    # --- arrange ----------------------
    recipe = ParamRecipe(
        axes=(
            ParamAxis("p1", 0.0, 2.0, 1.0),
            ParamAxis("p2", 0.0, 1.0, 1.0),
            ParamAxis("p3", 0.0, 3.0, 1.0),
        ),
        product=False,
    )

    # --- act --------------------------
    tuples = [tuple(v.value for v in p) for p in recipe.tuples()]

    # --- assert -----------------------
    assert {t[0] for t in tuples} == {0.0, 1.0, 2.0}
    assert {t[1] for t in tuples} == {0.0, 1.0}
    assert {t[2] for t in tuples} == {0.0, 1.0, 2.0, 3.0}
    assert tuples[0] == (0.0, 0.0, 0.0)
    assert tuples[-1] == (2.0, 1.0, 3.0)


def test_axis_grid_with_large_magnitude_values():
    assert tuple(v.value for v in ParamAxis("p1", 1e16, 3e16, step=1e16).values()) == (1e16, 2e16, 3e16)


def test_recipe_log10_convenience():
    # --- arrange / act ----------------
    recipe = ParamRecipe.log10("p1", -1.0, 1.0, step=1.0)

    # --- assert -----------------------
    assert [tuple(v.value for v in p) for p in recipe.tuples()] == [(0.1,), (1.0,), (10.0,)]


def test_recipe_single_axis_convenience():
    # --- arrange / act ----------------
    recipe = ParamRecipe.log2("p1", 0.0, 1.0, step=0.5)
    tuples = list(recipe.tuples())

    # --- assert -----------------------
    assert recipe.param_names() == ("p1",)
    # values are canonicalized to 10 significant digits, so compare at that resolution
    assert [p[0].value for p in tuples] == pytest.approx([1.0, 2**0.5, 2.0], rel=1e-9)
    assert [p[0].display() for p in tuples] == ["2^0.0", "2^0.5", "2^1.0"]
