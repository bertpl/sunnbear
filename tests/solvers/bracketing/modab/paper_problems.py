"""This module holds the 92 test problems of Table 2 of the 2026 modAB paper. Each problem holds:

- a function and its interval;
- modAB's evaluation count in the table;
- modAB's root in the paper's supplementary results.

The functions follow the C# benchmark of the paper's supplementary code, which produced Table 2; where the table
prints a function differently, the C# code holds.

Each power and each library function other than ``sqrt``, ``ceil`` and ``floor``, such as ``exp`` or ``sin``, is
evaluated correctly rounded, through mpmath; IEEE 754 already rounds ``sqrt`` correctly, and ``ceil`` and ``floor`` are
exact.

The C library rounds the last bit of powers and library functions differently per platform, and on several of the 92
functions that last bit changes the evaluation count; correctly rounded values make the counts the same on every
platform.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass

import mpmath


@dataclass(frozen=True)
class PaperProblem:
    """A `PaperProblem` is 1 row of the paper's Table 2: a function, its interval, and modAB's root and evaluation
    count.

    Attributes:
        name: The function's name in Table 2, ``f01`` to ``f92``.
        reported_root: modAB's root in the paper's supplementary results, which modAB returns without evaluating it.
        reported_n_fevals: modAB's evaluation count in Table 2.
        n_clamped: The number of iterations whose chord's zero is clamped onto a bound. The C# code counts every
            iteration as an evaluation, but a clamped iteration evaluates nothing, so `ModAB` evaluates
            ``reported_n_fevals - n_clamped`` times.
    """

    name: str
    f: Callable[[float], float]
    a: float
    b: float
    reported_root: float
    reported_n_fevals: int
    n_clamped: int


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _correctly_rounded(mpmath_function: Callable[..., mpmath.mpf]) -> Callable[..., float]:
    """Return a float version of ``mpmath_function`` that rounds its exact result to the nearest float.

    With 160 bits of working precision, the result is rounded correctly unless the exact value lies within a relative
    distance of 2^-107 of the midpoint between 2 adjacent floats.
    """

    def evaluate(*args: float) -> float:
        with mpmath.workprec(160):
            return float(mpmath_function(*[mpmath.mpf(arg) for arg in args]))

    return evaluate


_atan = _correctly_rounded(mpmath.atan)
_cbrt = _correctly_rounded(mpmath.cbrt)
_cos = _correctly_rounded(mpmath.cos)
_exp = _correctly_rounded(mpmath.exp)
_log = _correctly_rounded(mpmath.log)
_pow = _correctly_rounded(mpmath.power)
_sin = _correctly_rounded(mpmath.sin)
_tan = _correctly_rounded(mpmath.tan)


def _f27(x: float) -> float:
    """Return ``f27``, a quartic in ``s = x + 1.11111`` whose sign flips where ``s = 3``."""
    s = x + 1.11111
    return (81 - s * (108 - s * (54 - s * (12 - s)))) * float(mpmath.sign(s - 3))


# ==================================================================================================
#  The problems
# ==================================================================================================
PAPER_PROBLEMS = [
    PaperProblem("f01", lambda x: _pow(x, 3) - 1, 0.5, 1.5, 1.0, 3, 0),
    PaperProblem(
        "f02",
        lambda x: _pow(x, 2) * (_pow(x, 2) / 3 + math.sqrt(2) * _sin(x)) - math.sqrt(3) / 18,
        0.1,
        1.0,
        0.399422291710968,
        12,
        0,
    ),
    PaperProblem("f03", lambda x: 11 * _pow(x, 11) - 1, 0.1, 1.0, 0.804133097503664, 15, 2),
    PaperProblem("f04", lambda x: _pow(x, 3) + 1, -1.8, 0.0, -1.0, 10, 0),
    PaperProblem("f05", lambda x: _pow(x, 3) - 2 * x - 5, 2.0, 3.0, 2.09455148154232, 12, 2),
    PaperProblem("f06", lambda x: 2 * x * _exp(-5) + 1 - 2 * _exp(-5 * x), 0.0, 1.0, 0.138257155056824, 10, 0),
    PaperProblem("f07", lambda x: 2 * x * _exp(-10) + 1 - 2 * _exp(-10 * x), 0.0, 1.0, 0.0693140886870234, 11, 0),
    PaperProblem("f08", lambda x: 2 * x * _exp(-20) + 1 - 2 * _exp(-20 * x), 0.0, 1.0, 0.0346573590208538, 12, 0),
    PaperProblem(
        "f09", lambda x: (1 + _pow(1 - 5, 2)) * _pow(x, 2) - _pow(1 - 5 * x, 2), 0.0, 1.0, 0.109611796797792, 11, 1
    ),
    PaperProblem(
        "f10", lambda x: (1 + _pow(1 - 10, 2)) * _pow(x, 2) - _pow(1 - 10 * x, 2), 0.0, 1.0, 0.0524786034368101, 9, 0
    ),
    PaperProblem(
        "f11", lambda x: (1 + _pow(1 - 20, 2)) * _pow(x, 2) - _pow(1 - 20 * x, 2), 0.0, 1.0, 0.0256237476199882, 9, 0
    ),
    PaperProblem("f12", lambda x: _pow(x, 2) - _pow(1 - x, 5), 0.0, 1.0, 0.345954815848242, 11, 0),
    PaperProblem("f13", lambda x: _pow(x, 2) - _pow(1 - x, 10), 0.0, 1.0, 0.245122333753307, 12, 0),
    PaperProblem("f14", lambda x: _pow(x, 2) - _pow(1 - x, 20), 0.0, 1.0, 0.16492095727644, 12, 0),
    PaperProblem("f15", lambda x: (1 + _pow(1 - 5, 4)) * x - _pow(1 - 5 * x, 4), 0.0, 1.0, 0.00361710817890406, 9, 0),
    PaperProblem(
        "f16", lambda x: (1 + _pow(1 - 10, 4)) * x - _pow(1 - 10 * x, 4), 0.0, 1.0, 0.000151471334783891, 8, 0
    ),
    PaperProblem(
        "f17", lambda x: (1 + _pow(1 - 20, 4)) * x - _pow(1 - 20 * x, 4), 0.0, 1.0, 7.66859512218533e-06, 8, 0
    ),
    PaperProblem("f18", lambda x: _exp(-5 * x) * (x - 1) + _pow(x, 5), 0.0, 1.0, 0.516153518757933, 11, 0),
    PaperProblem("f19", lambda x: _exp(-10 * x) * (x - 1) + _pow(x, 10), 0.0, 1.0, 0.539522226908415, 12, 0),
    PaperProblem("f20", lambda x: _exp(-20 * x) * (x - 1) + _pow(x, 20), 0.0, 1.0, 0.552704666678487, 14, 1),
    PaperProblem("f21", lambda x: _pow(x, 2) + _sin(x / 5) - 1 / 4, 0.0, 1.0, 0.409992017989137, 9, 0),
    PaperProblem("f22", lambda x: _pow(x, 2) + _sin(x / 10) - 1 / 4, 0.0, 1.0, 0.452509145577641, 9, 0),
    PaperProblem("f23", lambda x: _pow(x, 2) + _sin(x / 20) - 1 / 4, 0.0, 1.0, 0.475626848596062, 9, 0),
    PaperProblem("f24", lambda x: (x + 2) * (x + 1) * _pow(x - 3, 3), 2.6, 4.6, 2.99999999999999, 48, 0),
    PaperProblem("f25", lambda x: _pow(x - 4, 5) * _log(x), 3.6, 5.6, 3.99999999999999, 48, 0),
    PaperProblem("f26", lambda x: _pow(_sin(x) - x / 4, 3), 2.0, 4.0, 2.47457678736982, 48, 0),
    PaperProblem("f27", _f27, 1.0, 3.0, 1.88916015625, 14, 0),
    PaperProblem("f28", lambda x: _sin(_pow(x - 7.143, 3)), 7.0, 8.0, 7.143, 46, 0),
    PaperProblem("f29", lambda x: _exp(_pow(x - 3, 5)) - 1, 2.6, 4.6, 3.00039062499999, 12, 0),
    PaperProblem("f30", lambda x: _exp(_pow(x - 3, 5)) - _exp(x - 1), 4.0, 5.0, 4.26716830454212, 13, 0),
    PaperProblem("f31", lambda x: math.pi - 1 / x, 0.05, 5.0, 0.31830988618379, 12, 0),
    PaperProblem("f32", lambda x: 4 - _tan(x), 0.0, 1.5, 1.32581766366803, 14, 1),
    PaperProblem("f33", lambda x: _cos(x) - _pow(x, 3), 0.0, 4.0, 0.865474033101614, 12, 0),
    PaperProblem("f34", lambda x: _cos(x) - x, -11.0, 9.0, 0.73908513321516, 11, 0),
    PaperProblem(
        "f35",
        lambda x: math.sqrt(abs(x - 2 / 3)) * (1 if x <= 2 / 3 else -1) - 0.1,
        -11.0,
        9.0,
        0.656666666666666,
        17,
        1,
    ),
    PaperProblem(
        "f36", lambda x: _pow(abs(x - 2 / 3), 0.2) * (1 if x <= 2 / 3 else -1), -11.0, 9.0, 0.666666666666665, 55, 0
    ),
    PaperProblem("f37", lambda x: _pow(x - 7 / 9, 3) + (x - 7 / 9) * 1e-3, -11.0, 9.0, 0.777777777777777, 16, 0),
    PaperProblem("f38", lambda x: -0.5 if x <= 1 / 3 else 0.5, -11.0, 9.0, 0.333333333333333, 53, 0),
    PaperProblem("f39", lambda x: -1e-3 if x <= 1 / 3 else 1 - 1e-3, -11.0, 9.0, 0.333333333333333, 53, 0),
    PaperProblem("f40", lambda x: 0.0 if x == 0 else 1 / (x - 2 / 3), -11.0, 9.0, 0.666666666666665, 53, 0),
    PaperProblem("f41", lambda x: 2 * x * _exp(-5) - 2 * _exp(-5 * x) + 1, 0.0, 10.0, 0.138257155056824, 13, 0),
    PaperProblem("f42", lambda x: (_pow(x, 2) - x - 6) * (_pow(x, 2) - 3 * x + 2), 0.0, math.pi, 1.0, 12, 0),
    PaperProblem("f43", lambda x: _pow(x, 3), -1.0, 1.5, 8.88178419700125e-16, 50, 0),
    PaperProblem("f44", lambda x: _pow(x, 5), -1.0, 1.5, 8.88178419700125e-16, 50, 0),
    PaperProblem("f45", lambda x: _pow(x, 7), -1.0, 1.5, 8.88178419700125e-16, 50, 0),
    PaperProblem("f46", lambda x: (_exp(-5 * x) - x - 0.5) / _pow(x, 5), 0.09, 0.7, 0.101624392293549, 14, 0),
    PaperProblem(
        "f47", lambda x: 1 / math.sqrt(x) - 2 * _log(5e3 * math.sqrt(x)) + 0.8, 0.0005, 0.5, 0.00773252320061279, 16, 0
    ),
    PaperProblem(
        "f48", lambda x: 1 / math.sqrt(x) - 2 * _log(5e7 * math.sqrt(x)) + 0.8, 0.0005, 0.5, 0.00127630494573556, 14, 0
    ),
    # The C# expression Math.Pow(x, 1/3) uses integer division, so its exponent is 0; Table 2 counts the evaluations
    # of the function with that exponent, so the exponent here stays 0.
    PaperProblem(
        "f49", lambda x: -_pow(x, 3) - x - 1 if x <= 0 else _pow(x, 0) - x - 1, -1.0, 1.0, -0.682327803828019, 12, 1
    ),
    PaperProblem("f50", lambda x: _pow(x, 3) - 2 * x - x + 3, -3.0, 2.0, -2.10380340273553, 11, 0),
    PaperProblem("f51", _log, 0.5, 5.0, 1.0, 10, 0),
    PaperProblem("f52", lambda x: (10 - x) * _exp(-10 * x) - _pow(x, 10) + 1, 0.5, 8.0, 1.00004083556472, 15, 0),
    PaperProblem("f53", lambda x: _exp(_sin(x)) - x - 1, 1.0, 4.0, 1.69681238680975, 13, 0),
    PaperProblem("f54", lambda x: 2 * _sin(x) - 1, 0.1, math.pi / 3, 0.523598775598298, 11, 1),
    PaperProblem("f55", lambda x: (x - 1) * _exp(-x), 0.0, 1.5, 1.0, 10, 0),
    PaperProblem("f56", lambda x: _pow(x - 1, 3) - 1, 1.5, 3.0, 2.0, 11, 0),
    PaperProblem("f57", lambda x: _exp(_pow(x, 2) + 7 * x - 30) - 1, 2.6, 3.5, 3.0, 11, 0),
    PaperProblem("f58", lambda x: _atan(x) - 1, 1.0, 8.0, 1.5574077246549, 10, 0),
    PaperProblem("f59", lambda x: _exp(x) - 2 * x - 1, 0.2, 3.0, 1.25643120862616, 12, 0),
    PaperProblem("f60", lambda x: _exp(-x) - x - _sin(x), 0.0, 2.0, 0.354463104375025, 9, 0),
    PaperProblem("f61", lambda x: _pow(x, 2) - _pow(_sin(x), 2) - 1, -1.0, 2.0, 1.40449164821534, 13, 1),
    PaperProblem("f62", lambda x: _sin(x) - x / 2, math.pi / 2, math.pi, 1.89549426703398, 10, 0),
    PaperProblem("f63", lambda x: x * _exp(x) - 1, -1.0, 1.0, 0.567143290409783, 11, 0),
    PaperProblem("f64", lambda x: _tan(x - 1 / 10), -1.0, 1.0, 0.1, 8, 0),
    PaperProblem("f65", lambda x: _sin(x) + 0.5, -1.0, 1.0, -0.523598775598298, 9, 0),
    PaperProblem("f66", lambda x: 4 * _pow(x, 5) + x * x + 1, -1.0, 1.0, -0.843914568649266, 13, 0),
    PaperProblem("f67", lambda x: x + _pow(x, 10) - 1, -1.0, 1.0, 0.835079042723559, 12, 0),
    PaperProblem("f68", lambda x: _pow(math.pi, x) - math.e, -1.0, 1.0, 0.873568526830231, 9, 0),
    PaperProblem("f69", lambda x: _log(abs(x - 10 / 9)), -1.0, 1.0, 0.111111111111111, 10, 0),
    PaperProblem(
        "f70",
        lambda x: 1 / 3 + float(mpmath.sign(x)) * _cbrt(abs(x)) + _pow(x, 3),
        -1.0,
        1.0,
        -0.0370201277078609,
        17,
        1,
    ),
    PaperProblem("f71", lambda x: (x + 2 / 3) / (x + 101 / 100), -1.0, 1.0, -0.666666666666666, 8, 0),
    PaperProblem("f72", lambda x: _pow(x * 1e6 - 1, 3), -1.0, 1.0, 1.00000000102795e-06, 50, 0),
    PaperProblem("f73", lambda x: _exp(x) * _pow(x * 1e6 - 1, 3), -1.0, 1.0, 1.00000000102795e-06, 50, 0),
    PaperProblem("f74", lambda x: _pow(x - 1 / 3, 2) * _atan(x - 1 / 3), -1.0, 1.0, 0.333333333333332, 50, 0),
    PaperProblem(
        "f75",
        lambda x: float(mpmath.sign(3 * x - 1)) * (1 - math.sqrt(1 - _pow(3 * x - 1, 2) / 81)),
        -1.0,
        1.0,
        0.333333313465118,
        27,
        0,
    ),
    PaperProblem(
        "f76", lambda x: (1 + 1e6) / 1e6 if x > (1 - 1e6) / 1e6 else -1.0, -1.0, 1.0, -0.999999000000003, 39, 0
    ),
    PaperProblem("f77", lambda x: 1 / (21 * x - 1) if x != 1 / 21 else 0.0, -1.0, 1.0, 0.0476190476190474, 50, 0),
    PaperProblem("f78", lambda x: x * x / 4 + math.ceil(x / 2) - 0.5, -1.0, 1.0, 9.65733148895921e-43, 9, 0),
    PaperProblem("f79", lambda x: math.ceil(10 * x - 1) + 0.5, -1.0, 1.0, 2.91317086684747e-19, 14, 0),
    PaperProblem("f80", lambda x: x + _sin(x * 1e6) / 10 + 1e-3, -1.0, 1.0, -0.0414560401586836, 25, 0),
    PaperProblem("f81", lambda x: 1 + _sin(1 / (x + 1)) if x > -1 else -1.0, -1.0, 1.0, -1.0, 14, 0),
    PaperProblem(
        "f82", lambda x: 202 * x - 2 * math.floor((2 * x + 1e-2) / 2e-2) - 0.1, -1.0, 1.0, 0.0499999999999999, 5, 0
    ),
    PaperProblem(
        "f83",
        lambda x: _pow(202 * x - 2 * math.floor((2 * x + 1e-2) / 2e-2) - 0.1, 3),
        -1.0,
        1.0,
        0.198514851485146,
        50,
        0,
    ),
    PaperProblem(
        "f84", lambda x: (x - 1) * (x - 2) * (x - 3) * (x - 4) * (x - 5) - 0.05, 0.5, 5.5, 3.01250244276146, 8, 0
    ),
    PaperProblem("f85", lambda x: _sin(x) - 0.5 * x - 0.3, -10.0, 10.0, -2.20778314488693, 11, 0),
    PaperProblem("f86", lambda x: _exp(x) - 1 - x - x * x / 2 - 0.005, -2.0, 2.0, 0.302804157270697, 15, 0),
    PaperProblem("f87", lambda x: 1 / (x - 0.5) - 2 - 0.05, 0.6, 2.0, 0.98780487804878, 9, 1),
    PaperProblem("f88", lambda x: _log(x) - x + 2 - 0.05, 0.1, 3.0, 0.168362173262536, 14, 1),
    PaperProblem("f89", lambda x: _sin(20 * x) + 0.1 * x - 0.1, -4.0, 5.0, -1.74176261121641, 13, 0),
    PaperProblem("f90", lambda x: x * x * x - 2 * x * x + x - 0.025, -1.0, 2.0, 0.02637269541443, 13, 0),
    PaperProblem("f91", lambda x: x * _sin(1 / x) - 0.1 - 0.01, 0.01, 1.0, 0.120778011811926, 13, 0),
    PaperProblem("f92", lambda x: x * x * x - 0.001, -10.0, 10.0, 0.1, 25, 0),
]
