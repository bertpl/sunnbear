"""This module holds `GanchovskiEtAlTable2Problem`, the 92 test problems of Table 2 of Ganchovski et al. (2026),
without any method's evaluation counts or roots.

Table 2 gives several methods' evaluation counts on 92 functions, each on 1 interval; a problem's name is the
function's name in the table, f01 to f92. The paper's supplementary results add each method's root.

The functions follow the C# benchmark of the paper's supplementary code, which produced Table 2; where the table
prints a function differently, the C# code holds.

Each power and each library function, such as ``exp`` or ``sin``, is evaluated correctly rounded, through mpmath. The
exceptions are ``sqrt``, which IEEE 754 already rounds correctly, and ``ceil`` and ``floor``, which are exact.

The C library rounds the last bit of powers and library functions differently per platform, and on several of the 92
functions that last bit changes the evaluation count; correctly rounded values make the counts the same on every
platform.

References:
    - Ganchovski, N., Smith, O., Rackauckas, C., Tomov, L. and Traykov, A. (2026). Improvements to the modified
      Anderson-Björck (modAB) root-finding algorithm. Algorithms 19(5), 332. https://doi.org/10.3390/a19050332
    - The paper's supplementary materials, which hold the C# benchmark and the results per function and method:
      https://www.mdpi.com/article/10.3390/a19050332/s1
"""

import math
from collections.abc import Callable
from dataclasses import replace

import mpmath

from .problem import PaperProblem, PaperProblemEnum

# The supplementary results print each root to 15 significant digits, so a root is checked within a relative 1e-13 by
# default.
GANCHOVSKI_ET_AL_ROOT_REL_TOL = 1e-13


# ==================================================================================================
#  The problems' functions
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


def _f40(x: float) -> float:
    """Return ``f40``, which is 0 at ``x = 0`` and has a pole at ``x = 2/3``."""
    if x == 0:
        return 0.0
    else:
        return 1 / (x - 2 / 3)


def _f49(x: float) -> float:
    """Return ``f49``: ``-x^3 - x - 1`` for ``x <= 0``, and ``x^0 - x - 1`` above, because the C# code writes the
    exponent ``1/3`` as an integer division, which is 0."""
    if x <= 0:
        return -_pow(x, 3) - x - 1
    else:
        return _pow(x, 0) - x - 1


def _f77(x: float) -> float:
    """Return ``f77``, which has a pole at ``x = 1/21``, where it is set to 0."""
    if x != 1 / 21:
        return 1 / (21 * x - 1)
    else:
        return 0.0


def _f81(x: float) -> float:
    """Return ``f81``, which is -1 at ``x <= -1``."""
    if x > -1:
        return 1 + _sin(1 / (x + 1))
    else:
        return -1.0


# ==================================================================================================
#  The problems
# ==================================================================================================
class GanchovskiEtAlTable2Problem(PaperProblemEnum):
    """`GanchovskiEtAlTable2Problem` holds the 92 problems of Table 2 of Ganchovski et al. (2026), in the table's
    order; a member's name is the function's name in the table, with an upper-case ``F``, e.g. ``F01``."""

    F01 = PaperProblem(name="f01", f=lambda x: _pow(x, 3) - 1, a=0.5, b=1.5)
    F02 = PaperProblem(
        name="f02", f=lambda x: _pow(x, 2) * (_pow(x, 2) / 3 + math.sqrt(2) * _sin(x)) - math.sqrt(3) / 18, a=0.1, b=1.0
    )
    F03 = PaperProblem(name="f03", f=lambda x: 11 * _pow(x, 11) - 1, a=0.1, b=1.0)
    F04 = PaperProblem(name="f04", f=lambda x: _pow(x, 3) + 1, a=-1.8, b=0.0)
    F05 = PaperProblem(name="f05", f=lambda x: _pow(x, 3) - 2 * x - 5, a=2.0, b=3.0)
    F06 = PaperProblem(name="f06", f=lambda x: 2 * x * _exp(-5) + 1 - 2 * _exp(-5 * x), a=0.0, b=1.0)
    F07 = PaperProblem(name="f07", f=lambda x: 2 * x * _exp(-10) + 1 - 2 * _exp(-10 * x), a=0.0, b=1.0)
    F08 = PaperProblem(name="f08", f=lambda x: 2 * x * _exp(-20) + 1 - 2 * _exp(-20 * x), a=0.0, b=1.0)
    F09 = PaperProblem(name="f09", f=lambda x: (1 + _pow(1 - 5, 2)) * _pow(x, 2) - _pow(1 - 5 * x, 2), a=0.0, b=1.0)
    F10 = PaperProblem(name="f10", f=lambda x: (1 + _pow(1 - 10, 2)) * _pow(x, 2) - _pow(1 - 10 * x, 2), a=0.0, b=1.0)
    F11 = PaperProblem(name="f11", f=lambda x: (1 + _pow(1 - 20, 2)) * _pow(x, 2) - _pow(1 - 20 * x, 2), a=0.0, b=1.0)
    F12 = PaperProblem(name="f12", f=lambda x: _pow(x, 2) - _pow(1 - x, 5), a=0.0, b=1.0)
    F13 = PaperProblem(name="f13", f=lambda x: _pow(x, 2) - _pow(1 - x, 10), a=0.0, b=1.0)
    F14 = PaperProblem(name="f14", f=lambda x: _pow(x, 2) - _pow(1 - x, 20), a=0.0, b=1.0)
    F15 = PaperProblem(name="f15", f=lambda x: (1 + _pow(1 - 5, 4)) * x - _pow(1 - 5 * x, 4), a=0.0, b=1.0)
    F16 = PaperProblem(name="f16", f=lambda x: (1 + _pow(1 - 10, 4)) * x - _pow(1 - 10 * x, 4), a=0.0, b=1.0)
    F17 = PaperProblem(name="f17", f=lambda x: (1 + _pow(1 - 20, 4)) * x - _pow(1 - 20 * x, 4), a=0.0, b=1.0)
    F18 = PaperProblem(name="f18", f=lambda x: _exp(-5 * x) * (x - 1) + _pow(x, 5), a=0.0, b=1.0)
    F19 = PaperProblem(name="f19", f=lambda x: _exp(-10 * x) * (x - 1) + _pow(x, 10), a=0.0, b=1.0)
    F20 = PaperProblem(name="f20", f=lambda x: _exp(-20 * x) * (x - 1) + _pow(x, 20), a=0.0, b=1.0)
    F21 = PaperProblem(name="f21", f=lambda x: _pow(x, 2) + _sin(x / 5) - 1 / 4, a=0.0, b=1.0)
    F22 = PaperProblem(name="f22", f=lambda x: _pow(x, 2) + _sin(x / 10) - 1 / 4, a=0.0, b=1.0)
    F23 = PaperProblem(name="f23", f=lambda x: _pow(x, 2) + _sin(x / 20) - 1 / 4, a=0.0, b=1.0)
    F24 = PaperProblem(name="f24", f=lambda x: (x + 2) * (x + 1) * _pow(x - 3, 3), a=2.6, b=4.6)
    F25 = PaperProblem(name="f25", f=lambda x: _pow(x - 4, 5) * _log(x), a=3.6, b=5.6)
    F26 = PaperProblem(name="f26", f=lambda x: _pow(_sin(x) - x / 4, 3), a=2.0, b=4.0)
    F27 = PaperProblem(name="f27", f=_f27, a=1.0, b=3.0)
    F28 = PaperProblem(name="f28", f=lambda x: _sin(_pow(x - 7.143, 3)), a=7.0, b=8.0)
    F29 = PaperProblem(name="f29", f=lambda x: _exp(_pow(x - 3, 5)) - 1, a=2.6, b=4.6)
    F30 = PaperProblem(name="f30", f=lambda x: _exp(_pow(x - 3, 5)) - _exp(x - 1), a=4.0, b=5.0)
    F31 = PaperProblem(name="f31", f=lambda x: math.pi - 1 / x, a=0.05, b=5.0)
    F32 = PaperProblem(name="f32", f=lambda x: 4 - _tan(x), a=0.0, b=1.5)
    F33 = PaperProblem(name="f33", f=lambda x: _cos(x) - _pow(x, 3), a=0.0, b=4.0)
    F34 = PaperProblem(name="f34", f=lambda x: _cos(x) - x, a=-11.0, b=9.0)
    F35 = PaperProblem(
        name="f35", f=lambda x: math.sqrt(abs(x - 2 / 3)) * (1 if x <= 2 / 3 else -1) - 0.1, a=-11.0, b=9.0
    )
    F36 = PaperProblem(name="f36", f=lambda x: _pow(abs(x - 2 / 3), 0.2) * (1 if x <= 2 / 3 else -1), a=-11.0, b=9.0)
    F37 = PaperProblem(name="f37", f=lambda x: _pow(x - 7 / 9, 3) + (x - 7 / 9) * 1e-3, a=-11.0, b=9.0)
    F38 = PaperProblem(name="f38", f=lambda x: -0.5 if x <= 1 / 3 else 0.5, a=-11.0, b=9.0)
    F39 = PaperProblem(name="f39", f=lambda x: -1e-3 if x <= 1 / 3 else 1 - 1e-3, a=-11.0, b=9.0)
    F40 = PaperProblem(name="f40", f=_f40, a=-11.0, b=9.0)
    F41 = PaperProblem(name="f41", f=lambda x: 2 * x * _exp(-5) - 2 * _exp(-5 * x) + 1, a=0.0, b=10.0)
    F42 = PaperProblem(name="f42", f=lambda x: (_pow(x, 2) - x - 6) * (_pow(x, 2) - 3 * x + 2), a=0.0, b=math.pi)
    F43 = PaperProblem(name="f43", f=lambda x: _pow(x, 3), a=-1.0, b=1.5)
    F44 = PaperProblem(name="f44", f=lambda x: _pow(x, 5), a=-1.0, b=1.5)
    F45 = PaperProblem(name="f45", f=lambda x: _pow(x, 7), a=-1.0, b=1.5)
    F46 = PaperProblem(name="f46", f=lambda x: (_exp(-5 * x) - x - 0.5) / _pow(x, 5), a=0.09, b=0.7)
    F47 = PaperProblem(name="f47", f=lambda x: 1 / math.sqrt(x) - 2 * _log(5e3 * math.sqrt(x)) + 0.8, a=0.0005, b=0.5)
    F48 = PaperProblem(name="f48", f=lambda x: 1 / math.sqrt(x) - 2 * _log(5e7 * math.sqrt(x)) + 0.8, a=0.0005, b=0.5)
    F49 = PaperProblem(name="f49", f=_f49, a=-1.0, b=1.0)
    F50 = PaperProblem(name="f50", f=lambda x: _pow(x, 3) - 2 * x - x + 3, a=-3.0, b=2.0)
    F51 = PaperProblem(name="f51", f=_log, a=0.5, b=5.0)
    F52 = PaperProblem(name="f52", f=lambda x: (10 - x) * _exp(-10 * x) - _pow(x, 10) + 1, a=0.5, b=8.0)
    F53 = PaperProblem(name="f53", f=lambda x: _exp(_sin(x)) - x - 1, a=1.0, b=4.0)
    F54 = PaperProblem(name="f54", f=lambda x: 2 * _sin(x) - 1, a=0.1, b=math.pi / 3)
    F55 = PaperProblem(name="f55", f=lambda x: (x - 1) * _exp(-x), a=0.0, b=1.5)
    F56 = PaperProblem(name="f56", f=lambda x: _pow(x - 1, 3) - 1, a=1.5, b=3.0)
    F57 = PaperProblem(name="f57", f=lambda x: _exp(_pow(x, 2) + 7 * x - 30) - 1, a=2.6, b=3.5)
    F58 = PaperProblem(name="f58", f=lambda x: _atan(x) - 1, a=1.0, b=8.0)
    F59 = PaperProblem(name="f59", f=lambda x: _exp(x) - 2 * x - 1, a=0.2, b=3.0)
    F60 = PaperProblem(name="f60", f=lambda x: _exp(-x) - x - _sin(x), a=0.0, b=2.0)
    F61 = PaperProblem(name="f61", f=lambda x: _pow(x, 2) - _pow(_sin(x), 2) - 1, a=-1.0, b=2.0)
    F62 = PaperProblem(name="f62", f=lambda x: _sin(x) - x / 2, a=math.pi / 2, b=math.pi)
    F63 = PaperProblem(name="f63", f=lambda x: x * _exp(x) - 1, a=-1.0, b=1.0)
    F64 = PaperProblem(name="f64", f=lambda x: _tan(x - 1 / 10), a=-1.0, b=1.0)
    F65 = PaperProblem(name="f65", f=lambda x: _sin(x) + 0.5, a=-1.0, b=1.0)
    F66 = PaperProblem(name="f66", f=lambda x: 4 * _pow(x, 5) + x * x + 1, a=-1.0, b=1.0)
    F67 = PaperProblem(name="f67", f=lambda x: x + _pow(x, 10) - 1, a=-1.0, b=1.0)
    F68 = PaperProblem(name="f68", f=lambda x: _pow(math.pi, x) - math.e, a=-1.0, b=1.0)
    F69 = PaperProblem(name="f69", f=lambda x: _log(abs(x - 10 / 9)), a=-1.0, b=1.0)
    F70 = PaperProblem(
        name="f70", f=lambda x: 1 / 3 + float(mpmath.sign(x)) * _cbrt(abs(x)) + _pow(x, 3), a=-1.0, b=1.0
    )
    F71 = PaperProblem(name="f71", f=lambda x: (x + 2 / 3) / (x + 101 / 100), a=-1.0, b=1.0)
    F72 = PaperProblem(name="f72", f=lambda x: _pow(x * 1e6 - 1, 3), a=-1.0, b=1.0)
    F73 = PaperProblem(name="f73", f=lambda x: _exp(x) * _pow(x * 1e6 - 1, 3), a=-1.0, b=1.0)
    F74 = PaperProblem(name="f74", f=lambda x: _pow(x - 1 / 3, 2) * _atan(x - 1 / 3), a=-1.0, b=1.0)
    F75 = PaperProblem(
        name="f75",
        f=lambda x: float(mpmath.sign(3 * x - 1)) * (1 - math.sqrt(1 - _pow(3 * x - 1, 2) / 81)),
        a=-1.0,
        b=1.0,
    )
    F76 = PaperProblem(name="f76", f=lambda x: (1 + 1e6) / 1e6 if x > (1 - 1e6) / 1e6 else -1.0, a=-1.0, b=1.0)
    F77 = PaperProblem(name="f77", f=_f77, a=-1.0, b=1.0)
    F78 = PaperProblem(name="f78", f=lambda x: x * x / 4 + math.ceil(x / 2) - 0.5, a=-1.0, b=1.0)
    F79 = PaperProblem(name="f79", f=lambda x: math.ceil(10 * x - 1) + 0.5, a=-1.0, b=1.0)
    F80 = PaperProblem(name="f80", f=lambda x: x + _sin(x * 1e6) / 10 + 1e-3, a=-1.0, b=1.0)
    F81 = PaperProblem(name="f81", f=_f81, a=-1.0, b=1.0)
    F82 = PaperProblem(name="f82", f=lambda x: 202 * x - 2 * math.floor((2 * x + 1e-2) / 2e-2) - 0.1, a=-1.0, b=1.0)
    F83 = PaperProblem(
        name="f83", f=lambda x: _pow(202 * x - 2 * math.floor((2 * x + 1e-2) / 2e-2) - 0.1, 3), a=-1.0, b=1.0
    )
    F84 = PaperProblem(name="f84", f=lambda x: (x - 1) * (x - 2) * (x - 3) * (x - 4) * (x - 5) - 0.05, a=0.5, b=5.5)
    F85 = PaperProblem(name="f85", f=lambda x: _sin(x) - 0.5 * x - 0.3, a=-10.0, b=10.0)
    F86 = PaperProblem(name="f86", f=lambda x: _exp(x) - 1 - x - x * x / 2 - 0.005, a=-2.0, b=2.0)
    F87 = PaperProblem(name="f87", f=lambda x: 1 / (x - 0.5) - 2 - 0.05, a=0.6, b=2.0)
    F88 = PaperProblem(name="f88", f=lambda x: _log(x) - x + 2 - 0.05, a=0.1, b=3.0)
    F89 = PaperProblem(name="f89", f=lambda x: _sin(20 * x) + 0.1 * x - 0.1, a=-4.0, b=5.0)
    F90 = PaperProblem(name="f90", f=lambda x: x * x * x - 2 * x * x + x - 0.025, a=-1.0, b=2.0)
    F91 = PaperProblem(name="f91", f=lambda x: x * _sin(1 / x) - 0.1 - 0.01, a=0.01, b=1.0)
    F92 = PaperProblem(name="f92", f=lambda x: x * x * x - 0.001, a=-10.0, b=10.0)

    def with_n_fevals_and_root(
        self,
        n_fevals: int,
        root: float,
        *,
        root_rel_tol: float = GANCHOVSKI_ET_AL_ROOT_REL_TOL,
        root_abs_tol: float = 0.0,
        deviation: int | None = 0,
        reason: str | None = None,
        observation: str | None = None,
    ) -> PaperProblem:
        """Return the member's problem with a method's evaluation count in Table 2 and the method's root in the paper's
        supplementary results; the count includes the 2 evaluations at the interval bounds.

        ``deviation`` is how far the solve's count may lie from ``n_fevals``: 0 when it must match exactly, and None
        when the count is not checked; ``reason``, required when ``deviation`` is not 0, says why. ``observation`` is
        that of `PaperProblemEnum.with_n_fevals`, and ``root_rel_tol`` and ``root_abs_tol`` are those of
        `PaperProblem`.
        """
        return replace(
            self.with_n_fevals(n_fevals, deviation=deviation, reason=reason, observation=observation),
            root=root,
            root_rel_tol=root_rel_tol,
            root_abs_tol=root_abs_tol,
        )


# ==================================================================================================
#  Stopping rule
# ==================================================================================================
def ganchovski_et_al_stop_width(x: float) -> float:
    """Return ``aTol + rTol * |x|``, with ``aTol = rTol = 1e-14``, the tolerance that the paper's C# code applies at
    ``x``.

    The C# modAB stops once the interval is at most this wide; the C# methods of Ridders and Brent use half of this
    width as their tolerance.
    """
    return 1e-14 + 1e-14 * abs(x)
