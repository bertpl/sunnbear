import itertools
from fractions import Fraction

import pytest

from sunnbear._core.problems.core import ParamAxis, ParamGrid, ParamNotation, ParamRounding, ParamTable


# ==================================================================================================
#  ParamRounding
# ==================================================================================================
@pytest.mark.parametrize(
    "rounding, value, expected",
    [
        (ParamRounding.NEAREST_INTEGER, 2.4, 2.0),
        (ParamRounding.NEAREST_INTEGER, 2.5, 3.0),  # a tie goes to the larger integer
        (ParamRounding.NEAREST_ODD_INTEGER, 1.0, 1.0),
        (ParamRounding.NEAREST_ODD_INTEGER, 1.995, 1.0),
        (ParamRounding.NEAREST_ODD_INTEGER, 2.0, 3.0),  # a tie goes to the larger integer
        (ParamRounding.NEAREST_ODD_INTEGER, 9.9, 9.0),
        (ParamRounding.NEAREST_ODD_INTEGER, 10.0, 11.0),  # a tie goes to the larger integer
        (ParamRounding.NEAREST_EVEN_INTEGER, 1.0, 2.0),  # a tie goes to the larger integer
        (ParamRounding.NEAREST_EVEN_INTEGER, 2.9, 2.0),
        (ParamRounding.NEAREST_EVEN_INTEGER, 3.1, 4.0),
    ],
)
def test_rounding_gives_the_nearest_integer_of_its_kind(rounding, value, expected):
    """Each rounding gives the nearest integer of its kind, and the larger one on a tie."""
    # --- act / assert -----------------
    assert rounding.round_value(value) == expected


# ==================================================================================================
#  ParamAxis
# ==================================================================================================
def test_axis_decimal_values_are_grid_rounded():
    # --- arrange ----------------------
    axis = ParamAxis("p1", 0.0, 1.0, step=0.2)

    # --- act / assert -----------------
    assert axis.values() == (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)


@pytest.mark.parametrize(
    "notation, start, stop, values, spellings",
    [
        (ParamNotation.POW2, 0.0, 2.0, (1.0, 2.0, 4.0), ["1.0", "2.0", "4.0"]),
        (ParamNotation.POW10, -1.0, 1.0, (0.1, 1.0, 10.0), ["0.1", "1.0", "10.0"]),
        (ParamNotation.NEG_POW2, 0.0, 2.0, (-1.0, -2.0, -4.0), ["-1.0", "-2.0", "-4.0"]),
        (ParamNotation.NEG_POW10, -1.0, 1.0, (-0.1, -1.0, -10.0), ["-0.1", "-1.0", "-10.0"]),
    ],
)
def test_axis_power_values(notation, start, stop, values, spellings):
    """A power axis sweeps the exponent; its values are powers of the base, or their negatives, spelled
    canonically."""
    # --- arrange ----------------------
    axis = ParamAxis("p1", start, stop, step=1.0, notation=notation)

    # --- act / assert -----------------
    assert axis.values() == values
    assert [ParamNotation.spell_value_canonically(v) for v in axis.values()] == spellings


@pytest.mark.parametrize("value", [3.0, 1e-05, -1e-05, 1e16, -3.5, 0.0])
def test_axis_single_point_preserves_value_exactly(value):
    """Values whose repr uses exponent notation must survive materialization intact."""
    assert ParamAxis("p1", value, value, step=1.0).values() == (value,)


@pytest.mark.parametrize(
    "start, stop, step",
    [(-1e-05, -1e-05, 1.0), (1e-09, 1e-09, 1.0), (0.0, 0.0, 1.0), (-1.0, -1.0, 0.25)],
)
def test_axis_never_yields_an_empty_grid(start, stop, step):
    """An empty grid would make coupled sweeps index out of range."""
    assert len(ParamAxis("p1", start, stop, step).values()) >= 1


@pytest.mark.parametrize(
    "rounding, values",
    [
        (
            ParamRounding.NEAREST_ODD_INTEGER,
            (
                1,
                3,
                5,
                7,
                11,
                13,
                15,
                19,
                25,
                31,
                39,
                51,
                63,
                79,
                101,
                125,
                159,
                199,
                251,
                317,
                399,
                501,
                631,
                795,
                1001,
            ),
        ),
        (
            ParamRounding.NEAREST_EVEN_INTEGER,
            (
                2,
                4,
                6,
                8,
                10,
                12,
                16,
                20,
                26,
                32,
                40,
                50,
                64,
                80,
                100,
                126,
                158,
                200,
                252,
                316,
                398,
                502,
                630,
                794,
                1000,
            ),
        ),
    ],
)
def test_rounded_axis_yields_each_value_once(rounding, values):
    """A rounded power axis yields each integer once, in grid order, though several grid points round to it."""
    # --- arrange ----------------------
    axis = ParamAxis("n", 0.0, 3.0, 0.1, ParamNotation.POW10, rounding)

    # --- act / assert -----------------
    assert axis.values() == tuple(float(value) for value in values)


@pytest.mark.parametrize(
    "axis, expected",
    [
        (
            ParamAxis("p1", 0.0, 2.0, 1.0),
            [(0.0, 0, Fraction(1, 4)), (1.0, Fraction(1, 4), Fraction(3, 4)), (2.0, Fraction(3, 4), 1)],
        ),
        (ParamAxis("p1", 5.0, 5.0, 1.0), [(5.0, 0, 1)]),
        (
            # the 5 grid values 1, 1.26, 1.58, 2.0, 2.51 round to 1, 1, 2, 2, 3
            ParamAxis("p1", 0.0, 0.4, 0.1, ParamNotation.POW10, ParamRounding.NEAREST_INTEGER),
            [(1.0, 0, Fraction(3, 8)), (2.0, Fraction(3, 8), Fraction(7, 8)), (3.0, Fraction(7, 8), 1)],
        ),
    ],
)
def test_axis_value_position_ranges(axis, expected):
    """Each value applies from the midpoint below its first grid point to the midpoint above its last one."""
    # --- act --------------------------
    value_position_ranges = axis.value_position_ranges()

    # --- assert -----------------------
    assert value_position_ranges == tuple(expected)


def test_coupled_sweep_with_tiny_magnitude_axis():
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(ParamAxis("p1", 0.0, 2.0, 1.0), ParamAxis("p2", -1e-05, -1e-05, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert list(grid.tuples()) == [
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


@pytest.mark.parametrize("noise", [1e-13, -1e-13, 2.5e-13])
def test_axis_alignment_forgives_snap_erasable_noise(noise):
    """The invariant behind the derived tolerance: noise the canonical snap erases cannot fail alignment."""
    # --- act --------------------------
    axis = ParamAxis("p1", 0.0, 1.0 + noise, step=0.25)

    # --- assert -----------------------
    assert axis.values() == (0.0, 0.25, 0.5, 0.75, 1.0)


def test_axis_alignment_rejects_misalignment_beyond_snap_noise():
    """A genuinely off-grid stop (integer endpoints, so the places check cannot mask it) is rejected."""
    with pytest.raises(ValueError, match="integer multiple"):
        ParamAxis("p1", 0.0, 1000000001.0, step=4.0)  # ratio 250000000.25: off by 1e-9 relative


def test_axis_forgives_float_noise_in_endpoints():
    """Decimal places are counted on the canonical form, so noise the snap erases can't fail the check."""
    # --- arrange ----------------------
    noisy_stop = 0.1 + 0.2  # 0.30000000000000004: 17 raw decimal places, 1 canonical

    # --- act --------------------------
    axis = ParamAxis("p1", 0.0, noisy_stop, step=0.1)

    # --- assert -----------------------
    assert axis.values() == (0.0, 0.1, 0.2, 0.3)


def test_axis_accepts_offset_but_clean_grid():
    """An offset lattice (1,3,5,7 on step 2) is valid: the endpoints are no finer than the step."""
    # --- act --------------------------
    values = ParamAxis("p1", 1.0, 7.0, 2.0).values()

    # --- assert -----------------------
    assert values == (1.0, 3.0, 5.0, 7.0)


# ==================================================================================================
#  ParamGrid
# ==================================================================================================
def test_grid_product():
    # --- arrange ----------------------
    grid = ParamGrid(axes=(ParamAxis("p1", 0.0, 1.0, 1.0), ParamAxis("p2", 5.0, 6.0, 1.0)))

    # --- act / assert -----------------
    assert list(grid.tuples()) == [(0.0, 5.0), (0.0, 6.0), (1.0, 5.0), (1.0, 6.0)]


def test_grid_coupled_sweep_same_lengths():
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(ParamAxis("p1", 0.0, 1.0, 1.0), ParamAxis("p2", 5.0, 6.0, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert list(grid.tuples()) == [(0.0, 5.0), (1.0, 6.0)]


def test_grid_coupled_sweep_unequal_lengths():
    """Axes advance one coordinate at a time along a shared axis; lengths need not match."""
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(ParamAxis("p1", 0.0, 4.0, 1.0), ParamAxis("p2", 0.0, 2.0, 1.0)),  # 5 values, 3 values
        product=False,
    )

    # --- act --------------------------
    tuples = list(grid.tuples())

    # --- assert -----------------------
    assert tuples == [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (2.0, 1.0), (3.0, 1.0), (3.0, 2.0), (4.0, 2.0)]


@pytest.mark.parametrize("n_p1, n_p2", [(5, 3), (32, 50), (101, 11), (7, 7), (2, 9)])
def test_grid_coupled_sweep_covers_every_value(n_p1, n_p2):
    """No axis ever loses a value, and consecutive tuples differ in exactly the stepping axes."""
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(ParamAxis("p1", 0.0, float(n_p1 - 1), 1.0), ParamAxis("p2", 0.0, float(n_p2 - 1), 1.0)),
        product=False,
    )

    # --- act --------------------------
    tuples = list(grid.tuples())

    # --- assert -----------------------
    assert {t[0] for t in tuples} == {float(i) for i in range(n_p1)}  # every p1 value appears
    assert {t[1] for t in tuples} == {float(i) for i in range(n_p2)}  # every p2 value appears
    assert max(n_p1, n_p2) <= len(tuples) <= (n_p1 - 1) + (n_p2 - 1) + 1
    assert all(a != b for a, b in itertools.pairwise(tuples))  # no repeats
    assert all(a <= b for a, b in itertools.pairwise(tuples))  # monotone in both axes


def test_grid_coupled_sweep_equal_lengths_is_a_zip():
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(ParamAxis("p1", 0.0, 3.0, 1.0), ParamAxis("p2", 10.0, 13.0, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert list(grid.tuples()) == [
        (0.0, 10.0),
        (1.0, 11.0),
        (2.0, 12.0),
        (3.0, 13.0),
    ]


def test_grid_coupled_sweep_all_single_value_axes():
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(ParamAxis("p1", 3.0, 3.0, 1.0), ParamAxis("p2", 7.0, 7.0, 1.0)),
        product=False,
    )

    # --- act / assert -----------------
    assert list(grid.tuples()) == [(3.0, 7.0)]


def test_grid_coupled_sweep_coinciding_boundaries_step_together():
    """Axes whose position ranges share a boundary advance in the same step (2- and 4-value axes share 1/2)."""
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(ParamAxis("p1", 0.0, 1.0, 1.0), ParamAxis("p2", 0.0, 3.0, 1.0)),  # 2 values, 4 values
        product=False,
    )

    # --- act / assert -----------------
    assert list(grid.tuples()) == [
        (0.0, 0.0),
        (0.0, 1.0),
        (1.0, 2.0),  # both axes crossed the shared boundary 1/2 in one step
        (1.0, 3.0),
    ]


def test_grid_coupled_sweep_with_a_rounded_axis_follows_the_grid_argument():
    """A rounded axis advances only at the boundary where its value changes, and no tuple repeats."""
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(
            ParamAxis("p1", 0.0, 0.4, 0.1, ParamNotation.POW10, ParamRounding.NEAREST_INTEGER),  # 1, 1, 2, 2, 3
            ParamAxis("p2", 0.0, 4.0, 1.0),  # 5 values, at the same positions as p1's grid points
        ),
        product=False,
    )

    # --- act / assert -----------------
    assert list(grid.tuples()) == [(1.0, 0.0), (1.0, 1.0), (2.0, 2.0), (2.0, 3.0), (3.0, 4.0)]


def test_grid_mixed_notations_survive_combining_into_tuples():
    """Each axis's notation determines its values in the assembled tuples: the POW2 axis gives powers of 2."""
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(ParamAxis("p1", 0.0, 1.0, 1.0), ParamAxis("p2", 0.0, 1.0, 1.0, ParamNotation.POW2)),
    )

    # --- act --------------------------
    tuples = list(grid.tuples())

    # --- assert -----------------------
    assert tuples == [(0.0, 1.0), (0.0, 2.0), (1.0, 1.0), (1.0, 2.0)]


def test_grid_coupled_sweep_three_axes():
    # --- arrange ----------------------
    grid = ParamGrid(
        axes=(
            ParamAxis("p1", 0.0, 2.0, 1.0),
            ParamAxis("p2", 0.0, 1.0, 1.0),
            ParamAxis("p3", 0.0, 3.0, 1.0),
        ),
        product=False,
    )

    # --- act --------------------------
    tuples = list(grid.tuples())

    # --- assert -----------------------
    assert {t[0] for t in tuples} == {0.0, 1.0, 2.0}
    assert {t[1] for t in tuples} == {0.0, 1.0}
    assert {t[2] for t in tuples} == {0.0, 1.0, 2.0, 3.0}
    assert tuples[0] == (0.0, 0.0, 0.0)
    assert tuples[-1] == (2.0, 1.0, 3.0)


def test_axis_grid_with_large_magnitude_values():
    assert ParamAxis("p1", 1e16, 3e16, step=1e16).values() == (1e16, 2e16, 3e16)


def test_grid_pow10_convenience():
    # --- arrange / act ----------------
    grid = ParamGrid.pow10("p1", -1.0, 1.0, step=1.0)

    # --- assert -----------------------
    assert list(grid.tuples()) == [(0.1,), (1.0,), (10.0,)]


def test_grid_single_axis_convenience():
    # --- arrange / act ----------------
    grid = ParamGrid.pow2("p1", 0.0, 1.0, step=0.5)
    tuples = list(grid.tuples())

    # --- assert -----------------------
    assert grid.param_names() == ("p1",)
    # arguments are rounded to 12 significant digits, so compare at that resolution
    assert [p[0] for p in tuples] == pytest.approx([1.0, 2**0.5, 2.0], rel=1e-9)
    assert [ParamNotation.spell_value_canonically(p[0]) for p in tuples] == ["1.0", "2^0.5", "2.0"]


# ==================================================================================================
#  ParamTable
# ==================================================================================================
def test_table_yields_its_rows_in_order_as_floats():
    """A table yields its rows in the order listed, with every value as a float."""
    # --- arrange ----------------------
    table = ParamTable(names=("n", "a"), rows=((5, 0.5), (1, 0.25), (20, 1e-05)))

    # --- act --------------------------
    tuples = list(table.tuples())

    # --- assert -----------------------
    assert table.param_names() == ("n", "a")
    assert tuples == [(5.0, 0.5), (1.0, 0.25), (20.0, 1e-05)]
    assert all(isinstance(value, float) for row in tuples for value in row)


@pytest.mark.parametrize(
    "names, rows, message",
    [
        (("n",), (), "at least 1 row"),
        (("n", "a"), ((1.0, 2.0), (3.0,)), "1 value for each"),
        (("n",), ((3.141592653589793,),), "not a valid parameter value"),
    ],
)
def test_table_rejects_a_malformed_table(names, rows, message):
    """A table without rows, with a row of the wrong length, or with an invalid value raises `ValueError`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message):
        ParamTable(names=names, rows=rows)


# ==================================================================================================
#  Summaries
# ==================================================================================================
@pytest.mark.parametrize(
    "recipe, expected",
    [
        (ParamGrid.decimal("b", 0.0, 1.0, 0.5, summary=r"The sweep of $\param{b}$."), r"The sweep of $\param{b}$."),
        (ParamGrid.pow2("b", 0.0, 1.0, 0.5, summary="A sweep in powers of 2."), "A sweep in powers of 2."),
        (ParamGrid.pow10("b", 0.0, 1.0, 0.5), None),
        (ParamTable(names=("n",), rows=((1.0,),), summary="The published values."), "The published values."),
        (ParamTable(names=("n",), rows=((1.0,),)), None),
    ],
)
def test_recipe_holds_its_summary(recipe, expected):
    """A grid or a table holds the summary that it is given, and None by default."""
    assert recipe.summary == expected
