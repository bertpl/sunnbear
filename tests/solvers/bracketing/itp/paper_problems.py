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
# table, which excludes the 2 evaluations at the interval bounds; the row whose count `ITP` does not reproduce also
# holds a count tolerance and the reason.
TABLE_1 = [
    PaperProblem(
        name=row["name"],
        f=row["f"],
        a=-1.0,
        b=1.0,
        n_fevals=row["n_iterations"] + 2,
        n_fevals_tol=row.get("n_fevals_tol", 0),
        deviation_reason=row.get("deviation_reason"),
    )
    for row in [
        {"name": "lambert", "f": lambda x: x * math.exp(x) - 1.0, "n_iterations": 8},
        {"name": "trigonometric_1", "f": lambda x: math.tan(x - 0.1), "n_iterations": 8},
        {"name": "trigonometric_2", "f": lambda x: math.sin(x) + 0.5, "n_iterations": 8},
        {"name": "polynomial_1", "f": lambda x: 4.0 * x**5 + x**2 + 1.0, "n_iterations": 18},
        {"name": "polynomial_2", "f": lambda x: x + x**10 - 1.0, "n_iterations": 16},
        {"name": "exponential", "f": lambda x: math.pi**x - math.e, "n_iterations": 8},
        {"name": "logarithmic", "f": lambda x: -math.log(abs(x - 10.0 / 9.0)), "n_iterations": 7},
        {
            "name": "posynomial",
            "f": lambda x: 1.0 / 3.0 + math.copysign(abs(x) ** (1.0 / 3.0), x) + x**3,
            "n_iterations": 32,
        },
        {
            "name": "weierstrass",
            "f": lambda x: 0.001 + sum(math.sin(math.pi * i**3 * x / 2.0) / (math.pi * i**3) for i in range(1, 11)),
            "n_iterations": 9,
        },
        {"name": "polynomial_fraction", "f": lambda x: (x + 2.0 / 3.0) / (x + 101.0 / 100.0), "n_iterations": 21},
        {
            "name": "normal_cdf",
            "f": lambda x: 0.5 * (1.0 + math.erf((x - 1.0) / math.sqrt(2.0))) - math.sqrt(2.0) / 4.0,
            "n_iterations": 8,
        },
        {
            "name": "normal_pdf",
            "f": lambda x: math.exp(-0.5 * (x - 1.0) ** 2) / math.sqrt(2.0 * math.pi) - math.sqrt(2.0) / 4.0,
            "n_iterations": 8,
        },
        {"name": "polynomial_3", "f": lambda x: (x * 1e6 - 1.0) ** 3, "n_iterations": 34},
        {"name": "exponential_polynomial", "f": lambda x: math.exp(x) * (x * 1e6 - 1.0) ** 3, "n_iterations": 34},
        {
            "name": "tangent_polynomial",
            "f": lambda x: (x - 1.0 / 3.0) ** 2 * math.atan(x - 1.0 / 3.0),
            "n_iterations": 34,
        },
        {"name": "circles", "f": _circles, "n_iterations": 23},
        {
            "name": "step_function",
            "f": lambda x: float(x > (1.0 - 1e6) / 1e6) * (1.0 + 1e6) / 1e6 - 1.0,
            "n_iterations": 34,
            "n_fevals_tol": 1,
            "deviation_reason": _STEP_FUNCTION_DEVIATION_REASON,
        },
        {"name": "geometric", "f": _geometric, "n_iterations": 34},
        {"name": "truncated_polynomial", "f": lambda x: (x / 2.0) ** 2 + math.ceil(x / 2.0) - 0.5, "n_iterations": 34},
        {"name": "staircase", "f": lambda x: math.ceil(10.0 * x - 1.0) + 0.5, "n_iterations": 31},
        {"name": "noisy_line", "f": lambda x: x + math.sin(x * 1e6) / 10.0 + 1e-3, "n_iterations": 19},
        {"name": "warsaw", "f": _warsaw, "n_iterations": 12},
        {"name": "sawtooth", "f": _sawtooth, "n_iterations": 10},
        {"name": "sawtooth_cube", "f": lambda x: _sawtooth(x) ** 3, "n_iterations": 34},
    ]
]
