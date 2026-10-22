"""This module holds the Bessel functions of the first and second kind of orders 0 and 1, for real arguments.

Each function evaluates rational approximations on 2 or 3 ranges of `|x|`: a rational function of `x^2` up to 5, and
the Hankel asymptotic expansion, with 2 rational functions of `25/x^2`, above. Their absolute error is about 1E-15 on
`[0, 30]`, as the original code states. The Bessel functions of the second kind are real only for `x > 0`: they return
minus infinity at 0 and NaN for a negative `x`.
"""

# These functions are ported from C++ code under the BSD 3-Clause license, © 2024 SciPy, itself translated from the
# Cephes Math Library, © Stephen L. Moshier; THIRD_PARTY_NOTICES.md holds that code's copyright and license notice.

import math

import numba

_SQRT1OPI = 5.641895835477562869480794515607725858441e-1  # sqrt(1/pi)
_SQRT2OPI = 7.978845608028653558798921198687637369517e-1  # sqrt(2/pi)
_PIO4 = 7.853981633974483096156608458198757210493e-1  # pi/4
_THPIO4 = 2.356194490192344928846982537459627163148  # 3*pi/4
_TWOOPI = 6.366197723675813430755350534900574481378e-1  # 2/pi
_SQRT1_2 = 7.071067811865475244008443621048490392848e-1  # sqrt(1/2)
# _SQRT_EPS is the square root of float64's machine epsilon, below which J1(x) is x/2 in float64
_SQRT_EPS = 1.490116119384765625e-8

# fmt: off
# The coefficient tuples hold each polynomial's coefficients from the highest power down; a tuple named for `p1evl`
# omits the leading coefficient, which is 1.
_J0_PP = (
    7.96936729297347051624e-4, 8.28352392107440799803e-2, 1.23953371646414299388e0, 5.44725003058768775090e0,
    8.74716500199817011941e0, 5.30324038235394892183e0, 9.99999999999999997821e-1,
)
_J0_PQ = (
    9.24408810558863637013e-4, 8.56288474354474431428e-2, 1.25352743901058953537e0, 5.47097740330417105182e0,
    8.76190883237069594232e0, 5.30605288235394617618e0, 1.00000000000000000218e0,
)
_J0_QP = (
    -1.13663838898469149931e-2, -1.28252718670509318512e0, -1.95539544257735972385e1, -9.32060152123768231369e1,
    -1.77681167980488050595e2, -1.47077505154951170175e2, -5.14105326766599330220e1, -6.05014350600728481186e0,
)
_J0_QQ = (  # for p1evl
    6.43178256118178023184e1, 8.56430025976980587198e2, 3.88240183605401609683e3, 7.24046774195652478189e3,
    5.93072701187316984827e3, 2.06209331660327847417e3, 2.42005740240291393179e2,
)
_J0_YP = (
    1.55924367855235737965e4, -1.46639295903971606143e7, 5.43526477051876500413e9, -9.82136065717911466409e11,
    8.75906394395366999549e13, -3.46628303384729719441e15, 4.42733268572569800351e16, -1.84950800436986690637e16,
)
_J0_YQ = (  # for p1evl
    1.04128353664259848412e3, 6.26107330137134956842e5, 2.68919633393814121987e8, 8.64002487103935000337e10,
    2.02979612750105546709e13, 3.17157752842975028269e15, 2.50596256172653059228e17,
)
_J0_DR1 = 5.78318596294678452118e0  # the square of the first zero of J0
_J0_DR2 = 3.04712623436620863991e1  # the square of the second zero of J0
_J0_RP = (
    -4.79443220978201773821e9, 1.95617491946556577543e12, -2.49248344360967716204e14, 9.70862251047306323952e15,
)
_J0_RQ = (  # for p1evl
    4.99563147152651017219e2, 1.73785401676374683123e5, 4.84409658339962045305e7, 1.11855537045356834862e10,
    2.11277520115489217587e12, 3.10518229857422583814e14, 3.18121955943204943306e16, 1.71086294081043136091e18,
)
_J1_RP = (
    -8.99971225705559398224e8, 4.52228297998194034323e11, -7.27494245221818276015e13, 3.68295732863852883286e15,
)
_J1_RQ = (  # for p1evl
    6.20836478118054335476e2, 2.56987256757748830383e5, 8.35146791431949253037e7, 2.21511595479792499675e10,
    4.74914122079991414898e12, 7.84369607876235854894e14, 8.95222336184627338078e16, 5.32278620332680085395e18,
)
_J1_PP = (
    7.62125616208173112003e-4, 7.31397056940917570436e-2, 1.12719608129684925192e0, 5.11207951146807644818e0,
    8.42404590141772420927e0, 5.21451598682361504063e0, 1.00000000000000000254e0,
)
_J1_PQ = (
    5.71323128072548699714e-4, 6.88455908754495404082e-2, 1.10514232634061696926e0, 5.07386386128601488557e0,
    8.39985554327604159757e0, 5.20982848682361821619e0, 9.99999999999999997461e-1,
)
_J1_QP = (
    5.10862594750176621635e-2, 4.98213872951233449420e0, 7.58238284132545283818e1, 3.66779609360150777800e2,
    7.10856304998926107277e2, 5.97489612400613639965e2, 2.11688757100572135698e2, 2.52070205858023719784e1,
)
_J1_QQ = (  # for p1evl
    7.42373277035675149943e1, 1.05644886038262816351e3, 4.98641058337653607651e3, 9.56231892404756170795e3,
    7.99704160447350683650e3, 2.82619278517639096600e3, 3.36093607810698293419e2,
)
_J1_YP = (
    1.26320474790178026440e9, -6.47355876379160291031e11, 1.14509511541823727583e14, -8.12770255501325109621e15,
    2.02439475713594898196e17, -7.78877196265950026825e17,
)
_J1_YQ = (  # for p1evl
    5.94301592346128195359e2, 2.35564092943068577943e5, 7.34811944459721705660e7, 1.87601316108706159478e10,
    3.88231277496238566008e12, 6.20557727146953693363e14, 6.87141087355300489866e16, 3.97270608116560655612e18,
)
_J1_Z1 = 1.46819706421238932572e1  # the square of the first positive zero of J1
_J1_Z2 = 4.92184563216946036703e1  # the square of the second positive zero of J1
# fmt: on


# ==================================================================================================
#  Bessel functions
# ==================================================================================================
@numba.njit
def bessel_j0(x: float) -> float:
    """Return J0(x), the Bessel function of the first kind of order 0."""
    x = abs(x)
    if x <= 5.0:
        if x < 3e-8:
            # x^2/4 is below float64's machine epsilon, so 1 - x^2/4 rounds to 1
            return 1.0
        elif x < 1e-5:
            return 1.0 - x * x / 4.0
        else:
            z = x * x
            p = (z - _J0_DR1) * (z - _J0_DR2)
            return p * _polevl(z, _J0_RP) / _p1evl(z, _J0_RQ)
    else:
        p, q = _j0_hankel_terms(x)
        w = 5.0 / x
        if x < 10.0:
            xn = x - _PIO4
            return (p * math.cos(xn) - w * q * math.sin(xn)) * _SQRT2OPI / math.sqrt(x)
        else:
            return ((p + w * q) * math.cos(x) + (p - w * q) * math.sin(x)) * _SQRT1OPI / math.sqrt(x)


@numba.njit
def bessel_y0(x: float) -> float:
    """Return Y0(x), the Bessel function of the second kind of order 0: minus infinity at 0, NaN for x < 0."""
    if x <= 5.0:
        if x == 0.0:
            return -math.inf
        elif x < 0.0:
            return math.nan
        elif x < 3e-8:
            # x^2/4 is below float64's machine epsilon, so the rational function takes its value at 0
            return _J0_YP[7] / _J0_YQ[6] + _TWOOPI * math.log(x)
        else:
            z = x * x
            return _polevl(z, _J0_YP) / _p1evl(z, _J0_YQ) + _TWOOPI * math.log(x) * bessel_j0(x)
    else:
        p, q = _j0_hankel_terms(x)
        w = 5.0 / x
        if x < 10.0:
            xn = x - _PIO4
            return (p * math.sin(xn) + w * q * math.cos(xn)) * _SQRT2OPI / math.sqrt(x)
        else:
            return ((w * q - p) * math.cos(x) + (p + w * q) * math.sin(x)) * _SQRT1OPI / math.sqrt(x)


@numba.njit
def bessel_j1(x: float) -> float:
    """Return J1(x), the Bessel function of the first kind of order 1."""
    if x < 0.0:
        return -_bessel_j1_of_nonnegative(-x)
    else:
        return _bessel_j1_of_nonnegative(x)


@numba.njit
def bessel_y1(x: float) -> float:
    """Return Y1(x), the Bessel function of the second kind of order 1: minus infinity at 0, NaN for x < 0."""
    if x <= 5.0:
        if x == 0.0:
            return -math.inf
        elif x < 0.0:
            return math.nan
        else:
            z = x * x
            w = x * (_polevl(z, _J1_YP) / _p1evl(z, _J1_YQ))
            return w + _TWOOPI * (bessel_j1(x) * math.log(x) - 1.0 / x)
    else:
        p, q = _j1_hankel_terms(x)
        w = 5.0 / x
        if x < 10.0:
            xn = x - _THPIO4
            return (p * math.sin(xn) + w * q * math.cos(xn)) * _SQRT2OPI / math.sqrt(x)
        else:
            return ((w * q - p) * math.sin(x) - (p + w * q) * math.cos(x)) * _SQRT1OPI / math.sqrt(x)


# ==================================================================================================
#  Helpers
# ==================================================================================================
@numba.njit
def _bessel_j1_of_nonnegative(x: float) -> float:
    """Return J1(x) for x >= 0."""
    if x < _SQRT_EPS:
        return 0.5 * x
    elif x <= 5.0:
        z = x * x
        w = _polevl(z, _J1_RP) / _p1evl(z, _J1_RQ)
        return w * x * (z - _J1_Z1) * (z - _J1_Z2)
    else:
        p, q = _j1_hankel_terms(x)
        w = 5.0 / x
        if x < 10.0:
            xn = x - _THPIO4
            return (p * math.cos(xn) - w * q * math.sin(xn)) * _SQRT2OPI / math.sqrt(x)
        else:
            a = _SQRT1_2 * (w * q - p)
            b = _SQRT1_2 * (p + w * q)
            return (a * math.cos(x) + b * math.sin(x)) * _SQRT2OPI / math.sqrt(x)


@numba.njit
def _j0_hankel_terms(x: float) -> tuple[float, float]:
    """Return the 2 rational functions P and Q of the Hankel expansion of J0 and Y0, for x > 5."""
    z = 25.0 / (x * x)
    p = _polevl(z, _J0_PP) / _polevl(z, _J0_PQ)
    q = _polevl(z, _J0_QP) / _p1evl(z, _J0_QQ)
    return p, q


@numba.njit
def _j1_hankel_terms(x: float) -> tuple[float, float]:
    """Return the 2 rational functions P and Q of the Hankel expansion of J1 and Y1, for x > 5."""
    w = 5.0 / x
    z = w * w
    p = _polevl(z, _J1_PP) / _polevl(z, _J1_PQ)
    q = _polevl(z, _J1_QP) / _p1evl(z, _J1_QQ)
    return p, q


@numba.njit
def _polevl(x: float, coefficients: tuple) -> float:
    """Return the polynomial with `coefficients`, from the highest power down, at `x`, by Horner's rule."""
    result = coefficients[0]
    for coefficient in coefficients[1:]:
        result = result * x + coefficient
    return result


@numba.njit
def _p1evl(x: float, coefficients: tuple) -> float:
    """Return the polynomial with leading coefficient 1 and the other `coefficients`, from the highest power down."""
    result = x + coefficients[0]
    for coefficient in coefficients[1:]:
        result = result * x + coefficient
    return result
