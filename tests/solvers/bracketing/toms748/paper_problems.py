"""This module holds the test problems of Algorithm 748, from the authors' test driver, and the roots that the
authors' code computes for them.

The driver numbers its problems 1 to 28, and runs most of them for several values of an integer parameter ``n``. The
functions and intervals below follow the driver's subroutines ``FUNC`` and ``INIT``; they are the test problems of the
paper's Table I, with the paper's problem 2 split into 10 problems, 1 per interval.
"""

import math
from dataclasses import dataclass

# The driver sets pi to this rounded value for the intervals of problems 1 and 27.
_PI_ROUNDED = 3.1416


@dataclass(frozen=True)
class PaperProblem:
    """A `PaperProblem` is 1 of the test problems: the driver's problem number, its parameter ``n``, and the root that
    the authors' code computes for it with the tolerance ``tol = 0``."""

    number: int
    n: int
    root: float

    def __str__(self) -> str:
        """Return a short label for the test id, e.g. ``15[n=4]``."""
        return f"{self.number}[n={self.n}]"

    @property
    def interval(self) -> tuple[float, float]:  # noqa: C901 — 1 branch per interval of the driver
        """Return the initial interval ``(a, b)`` of the problem."""
        if self.number == 1:
            return _PI_ROUNDED / 2.0, _PI_ROUNDED
        elif 2 <= self.number <= 11:
            # Problems 2 to 11 share 1 function, which has a pole at each square i^2; each problem takes the
            # interval between 2 consecutive squares.
            i = float(self.number - 1)
            return i * i + 1e-9, (i + 1.0) * (i + 1.0) - 1e-9
        elif 12 <= self.number <= 14:
            return -9.0, 31.0
        elif self.number in (15, 16):
            return 0.0, 5.0
        elif self.number == 17:
            return -0.95, 4.05
        elif self.number == 18:
            return 0.0, 1.5
        elif 19 <= self.number <= 23:
            return 0.0, 1.0
        elif self.number == 24:
            return 1e-2, 1.0
        elif self.number == 25:
            return 1.0, 100.0
        elif self.number == 26:
            return -1.0, 4.0
        elif self.number == 27:
            return -10000.0, _PI_ROUNDED / 2.0
        else:
            return -10000.0, 1e-4

    def f(self, x: float) -> float:  # noqa: C901 — 1 branch per function of the driver
        """Return the problem's function at ``x``, computed as the driver computes it."""
        n = float(self.n)
        if self.number == 1:
            return math.sin(x) - x / 2.0
        elif 2 <= self.number <= 11:
            fx = 0.0
            for i in range(1, 21):
                fx = fx + (2.0 * i - 5.0) ** 2 / (x - float(i * i)) ** 3
            return -2.0 * fx
        elif self.number == 12:
            return -40.0 * x * math.exp(-1.0 * x)
        elif self.number == 13:
            return -100.0 * x * math.exp(-2.0 * x)
        elif self.number == 14:
            return -200.0 * x * math.exp(-3.0 * x)
        elif self.number == 15:
            return x**self.n - 0.2
        elif self.number in (16, 17):
            return x**self.n - 1.0
        elif self.number == 18:
            return math.sin(x) - 0.5
        elif self.number == 19:
            return 2.0 * x * math.exp(-n) - 2.0 * math.exp(-n * x) + 1.0
        elif self.number == 20:
            return (1.0 + (1.0 - n) ** 2) * x - (1.0 - n * x) ** 2
        elif self.number == 21:
            return x**2 - (1.0 - x) ** self.n
        elif self.number == 22:
            return (1.0 + (1.0 - n) ** 4) * x - (1.0 - n * x) ** 4
        elif self.number == 23:
            return (x - 1.0) * math.exp(-n * x) + x**self.n
        elif self.number == 24:
            return (n * x - 1.0) / ((n - 1.0) * x)
        elif self.number == 25:
            return x ** (1.0 / n) - n ** (1.0 / n)
        elif self.number == 26:
            return self._flat_near_0(x)
        elif self.number == 27:
            if x >= 0.0:
                return (x / 1.5 + math.sin(x) - 1.0) * n / 20.0
            else:
                return -n / 20.0
        elif x >= 1e-3 * 2.0 / (n + 1.0):
            return math.exp(1.0) - 1.859
        elif x >= 0.0:
            return math.exp((n + 1.0) * 0.5 * x * 1e3) - 1.859
        else:
            return -0.859

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _flat_near_0(x: float) -> float:
        """Return ``x / exp(1 / x^2)``, problem 26, and 0 where the exponential overflows, which is the value that the
        Fortran code computes there.

        Python raises where Fortran returns infinity: ``exp`` overflows for ``|x|`` below about 0.0375, and ``1 / x^2``
        for ``|x|`` below about 1e-154. The function is 0 there in both cases.
        """
        if x == 0.0:
            return 0.0
        else:
            try:
                return x / math.exp(1.0 / (x * x))
            except (OverflowError, ZeroDivisionError):
                return 0.0


# The authors' test output lists, in the order of their test data, the problem number, n, and the root that their
# code prints to 14 significant digits.
PAPER_PROBLEMS = [
    PaperProblem(number, n, root)
    for number, n, root in [
        (1, 1, 1.8954942670340),
        (2, 1, 3.0229153472731),
        (3, 1, 6.6837535608081),
        (4, 1, 11.238701655002),
        (5, 1, 19.676000080623),
        (6, 1, 29.828227326505),
        (7, 1, 41.906116195289),
        (8, 1, 55.953595800143),
        (9, 1, 71.985665586588),
        (10, 1, 90.008868539167),
        (11, 1, 110.02653274833),
        (12, 1, 0.0),
        (13, 1, 0.0),
        (14, 1, 0.0),
        (15, 4, 0.66874030497642),
        (15, 6, 0.76472449133173),
        (15, 8, 0.81776543395794),
        (15, 10, 0.85133992252078),
        (15, 12, 0.87448527222117),
        (16, 4, 1.0000000000000),
        (16, 6, 1.0000000000000),
        (16, 8, 1.0000000000000),
        (16, 10, 1.0000000000000),
        (16, 12, 1.0000000000000),
        (17, 8, 1.0000000000000),
        (17, 10, 1.0000000000000),
        (17, 12, 1.0000000000000),
        (17, 14, 1.0000000000000),
        (18, 1, 0.52359877559830),
        (19, 1, 0.42247770964124),
        (19, 2, 0.30669941048320),
        (19, 3, 0.22370545765466),
        (19, 4, 0.17171914751951),
        (19, 5, 0.13825715505682),
        (19, 20, 3.4657359020854e-02),
        (19, 40, 1.7328679513999e-02),
        (19, 60, 1.1552453009332e-02),
        (19, 80, 8.6643397569993e-03),
        (19, 100, 6.9314718055995e-03),
        (20, 5, 3.8402551840622e-02),
        (20, 10, 9.9000099980005e-03),
        (20, 20, 2.4937500390620e-03),
        (21, 2, 0.50000000000000),
        (21, 5, 0.34595481584824),
        (21, 10, 0.24512233375331),
        (21, 15, 0.19554762353657),
        (21, 20, 0.16492095727644),
        (22, 1, 0.27550804099948),
        (22, 2, 0.13775402049974),
        (22, 4, 1.0305283778156e-02),
        (22, 5, 3.6171081789041e-03),
        (22, 8, 4.1087291849640e-04),
        (22, 15, 2.5989575892908e-05),
        (22, 20, 7.6685951221853e-06),
        (23, 1, 0.40105813754155),
        (23, 5, 0.51615351875793),
        (23, 10, 0.53952222690842),
        (23, 15, 0.54818229434066),
        (23, 20, 0.55270466667849),
        (24, 2, 0.50000000000000),
        (24, 5, 0.20000000000000),
        (24, 15, 6.6666666666667e-02),
        (24, 20, 5.0000000000000e-02),
        (25, 2, 2.0000000000000),
        (25, 3, 3.0000000000000),
        (25, 4, 4.0000000000000),
        (25, 5, 5.0000000000000),
        (25, 6, 6.0000000000000),
        (25, 7, 7.0000000000000),
        (25, 9, 9.0000000000000),
        (25, 11, 11.000000000000),
        (25, 13, 13.000000000000),
        (25, 15, 15.000000000000),
        (25, 17, 17.000000000000),
        (25, 19, 19.000000000000),
        (25, 21, 21.000000000000),
        (25, 23, 23.000000000000),
        (25, 25, 25.000000000000),
        (25, 27, 27.000000000000),
        (25, 29, 29.000000000000),
        (25, 31, 31.000000000000),
        (25, 33, 33.000000000000),
        (26, 1, 2.2317679157465e-02),
        (27, 1, 0.62380651896161),
        (27, 2, 0.62380651896161),
        (27, 3, 0.62380651896161),
        (27, 4, 0.62380651896161),
        (27, 5, 0.62380651896161),
        (27, 6, 0.62380651896161),
        (27, 7, 0.62380651896161),
        (27, 8, 0.62380651896161),
        (27, 9, 0.62380651896161),
        (27, 10, 0.62380651896161),
        (27, 11, 0.62380651896161),
        (27, 12, 0.62380651896161),
        (27, 13, 0.62380651896161),
        (27, 14, 0.62380651896161),
        (27, 15, 0.62380651896161),
        (27, 16, 0.62380651896161),
        (27, 17, 0.62380651896161),
        (27, 18, 0.62380651896161),
        (27, 19, 0.62380651896161),
        (27, 20, 0.62380651896161),
        (27, 21, 0.62380651896161),
        (27, 22, 0.62380651896161),
        (27, 23, 0.62380651896161),
        (27, 24, 0.62380651896161),
        (27, 25, 0.62380651896161),
        (27, 26, 0.62380651896161),
        (27, 27, 0.62380651896161),
        (27, 28, 0.62380651896161),
        (27, 29, 0.62380651896161),
        (27, 30, 0.62380651896161),
        (27, 31, 0.62380651896161),
        (27, 32, 0.62380651896161),
        (27, 33, 0.62380651896161),
        (27, 34, 0.62380651896161),
        (27, 35, 0.62380651896161),
        (27, 36, 0.62380651896161),
        (27, 37, 0.62380651896161),
        (27, 38, 0.62380651896161),
        (27, 39, 0.62380651896161),
        (27, 40, 0.62380651896161),
        (28, 20, 5.9051305594220e-05),
        (28, 21, 5.6367155339937e-05),
        (28, 22, 5.3916409455592e-05),
        (28, 23, 5.1669892394942e-05),
        (28, 24, 4.9603096699145e-05),
        (28, 25, 4.7695285287639e-05),
        (28, 26, 4.5928793239949e-05),
        (28, 27, 4.4288479195665e-05),
        (28, 28, 4.2761290257883e-05),
        (28, 29, 4.1335913915954e-05),
        (28, 30, 4.0002497338020e-05),
        (28, 31, 3.8752419296207e-05),
        (28, 32, 3.7578103559958e-05),
        (28, 33, 3.6472865219959e-05),
        (28, 34, 3.5430783356532e-05),
        (28, 35, 3.4446594929961e-05),
        (28, 36, 3.3515605877800e-05),
        (28, 37, 3.2633616249437e-05),
        (28, 38, 3.1796856858426e-05),
        (28, 39, 3.1001935436965e-05),
        (28, 40, 3.0245790670210e-05),
        (28, 100, 1.2277994232462e-05),
        (28, 200, 6.1695393904409e-06),
        (28, 300, 4.1198585298293e-06),
        (28, 400, 3.0924623877272e-06),
        (28, 500, 2.4752044261050e-06),
        (28, 600, 2.0633567678513e-06),
        (28, 700, 1.7690120078154e-06),
        (28, 800, 1.5481615698859e-06),
        (28, 900, 1.3763345366022e-06),
        (28, 1000, 1.2388385788997e-06),
    ]
]
