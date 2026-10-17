"""This module holds `TABLE_1`, the test problems of Table 1 of the ITP paper, with the paper's iteration counts for
`ITP`."""

from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.oliveira_takahashi import OliveiraTakahashiTable1Problem

TABLE_1 = [
    OliveiraTakahashiTable1Problem.LAMBERT.with_n_iterations(8),
    OliveiraTakahashiTable1Problem.TRIGONOMETRIC_1.with_n_iterations(8),
    OliveiraTakahashiTable1Problem.TRIGONOMETRIC_2.with_n_iterations(8),
    OliveiraTakahashiTable1Problem.POLYNOMIAL_1.with_n_iterations(18),
    OliveiraTakahashiTable1Problem.POLYNOMIAL_2.with_n_iterations(16),
    OliveiraTakahashiTable1Problem.EXPONENTIAL.with_n_iterations(8),
    OliveiraTakahashiTable1Problem.LOGARITHMIC.with_n_iterations(7),
    OliveiraTakahashiTable1Problem.POSYNOMIAL.with_n_iterations(32),
    OliveiraTakahashiTable1Problem.WEIERSTRASS.with_n_iterations(9),
    OliveiraTakahashiTable1Problem.POLYNOMIAL_FRACTION.with_n_iterations(21),
    OliveiraTakahashiTable1Problem.NORMAL_CDF.with_n_iterations(8),
    OliveiraTakahashiTable1Problem.NORMAL_PDF.with_n_iterations(8),
    OliveiraTakahashiTable1Problem.POLYNOMIAL_3.with_n_iterations(34),
    OliveiraTakahashiTable1Problem.EXPONENTIAL_POLYNOMIAL.with_n_iterations(34),
    OliveiraTakahashiTable1Problem.TANGENT_POLYNOMIAL.with_n_iterations(34),
    OliveiraTakahashiTable1Problem.CIRCLES.with_n_iterations(23),
    OliveiraTakahashiTable1Problem.STEP_FUNCTION.with_n_iterations(
        34, deviation=1, reason=UNSTATED_RUN_DETAILS, observation="the solve takes 1 iteration more"
    ),
    OliveiraTakahashiTable1Problem.GEOMETRIC.with_n_iterations(34),
    OliveiraTakahashiTable1Problem.TRUNCATED_POLYNOMIAL.with_n_iterations(34),
    OliveiraTakahashiTable1Problem.STAIRCASE.with_n_iterations(31),
    OliveiraTakahashiTable1Problem.NOISY_LINE.with_n_iterations(19),
    OliveiraTakahashiTable1Problem.WARSAW.with_n_iterations(12),
    OliveiraTakahashiTable1Problem.SAWTOOTH.with_n_iterations(10),
    OliveiraTakahashiTable1Problem.SAWTOOTH_CUBE.with_n_iterations(34),
]
