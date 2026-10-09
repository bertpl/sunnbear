"""This module holds `TABLE_1`, the test functions of Table 1 of the ITP paper, with the paper's iteration counts for
`ITP`."""

import math

from tests.solvers.paper_problems import PaperProblem

# The paper's experiments solve every function on [-1, 1] with this xtol, where bisection needs `N_BISECTION`
# iterations.
XTOL = 1e-10
N_BISECTION = 34


def _sawtooth(x: float) -> float:
    """Return the paper's sawtooth function, which crosses 0 on many teeth."""
    return 202.0 * x - 2.0 * math.floor((2.0 * x + 1e-2) / (2.0 * 1e-2)) - 0.1


def _geometric(x: float) -> float:
    """Return the paper's geometric function ``1 / (21x - 1)``, set to 0 at its pole."""
    if x == 1.0 / 21.0:
        return 0.0
    else:
        return 1.0 / (21.0 * x - 1.0)


def _warsaw(x: float) -> float:
    """Return the paper's Warsaw function, ``sin(1 / (x + 1))`` right of -1 and -1 elsewhere."""
    if x > -1.0:
        return math.sin(1.0 / (x + 1.0))
    else:
        return -1.0


def _circles(x: float) -> float:
    """Return the paper's circles function, which takes the sign of ``3x + 1`` and is 0 where ``3x + 1`` is 0."""
    sign = (3.0 * x + 1.0 > 0.0) - (3.0 * x + 1.0 < 0.0)
    return sign * (1.0 - math.sqrt(1.0 - (3.0 * x + 1.0) ** 2 / 81.0))


_STEP_FUNCTION_DEVIATION_REASON = "MATLAB's arithmetic produced the table's 34 iterations, and `ITP` takes 35"

# Each row holds a test function of the paper's Table 1, by its name there, and the iteration count of ITP in that
# table, which excludes the 2 evaluations at the interval bounds.
TABLE_1 = [
    PaperProblem(
        name,
        f,
        -1.0,
        1.0,
        n_fevals=n_iterations + 2,
        n_fevals_tol=1 if name == "step_function" else 0,
        deviation_reason=_STEP_FUNCTION_DEVIATION_REASON if name == "step_function" else None,
    )
    for name, f, n_iterations in [
        ("lambert", lambda x: x * math.exp(x) - 1.0, 8),
        ("trigonometric_1", lambda x: math.tan(x - 0.1), 8),
        ("trigonometric_2", lambda x: math.sin(x) + 0.5, 8),
        ("polynomial_1", lambda x: 4.0 * x**5 + x**2 + 1.0, 18),
        ("polynomial_2", lambda x: x + x**10 - 1.0, 16),
        ("exponential", lambda x: math.pi**x - math.e, 8),
        ("logarithmic", lambda x: -math.log(abs(x - 10.0 / 9.0)), 7),
        ("posynomial", lambda x: 1.0 / 3.0 + math.copysign(abs(x) ** (1.0 / 3.0), x) + x**3, 32),
        (
            "weierstrass",
            lambda x: 0.001 + sum(math.sin(math.pi * i**3 * x / 2.0) / (math.pi * i**3) for i in range(1, 11)),
            9,
        ),
        ("polynomial_fraction", lambda x: (x + 2.0 / 3.0) / (x + 101.0 / 100.0), 21),
        ("normal_cdf", lambda x: 0.5 * (1.0 + math.erf((x - 1.0) / math.sqrt(2.0))) - math.sqrt(2.0) / 4.0, 8),
        ("normal_pdf", lambda x: math.exp(-0.5 * (x - 1.0) ** 2) / math.sqrt(2.0 * math.pi) - math.sqrt(2.0) / 4.0, 8),
        ("polynomial_3", lambda x: (x * 1e6 - 1.0) ** 3, 34),
        ("exponential_polynomial", lambda x: math.exp(x) * (x * 1e6 - 1.0) ** 3, 34),
        ("tangent_polynomial", lambda x: (x - 1.0 / 3.0) ** 2 * math.atan(x - 1.0 / 3.0), 34),
        ("circles", _circles, 23),
        ("step_function", lambda x: float(x > (1.0 - 1e6) / 1e6) * (1.0 + 1e6) / 1e6 - 1.0, 34),
        ("geometric", _geometric, 34),
        ("truncated_polynomial", lambda x: (x / 2.0) ** 2 + math.ceil(x / 2.0) - 0.5, 34),
        ("staircase", lambda x: math.ceil(10.0 * x - 1.0) + 0.5, 31),
        ("noisy_line", lambda x: x + math.sin(x * 1e6) / 10.0 + 1e-3, 19),
        ("warsaw", _warsaw, 12),
        ("sawtooth", _sawtooth, 10),
        ("sawtooth_cube", lambda x: _sawtooth(x) ** 3, 34),
    ]
]
