"""This module holds `BrentVariant`, the variants of `Brent`."""

from enum import StrEnum


class BrentVariant(StrEnum):
    """`BrentVariant` names the variants of `Brent`, 1 per formula of its interpolation through 3 x-values."""

    HYPERBOLIC = "hyperbolic"
    INVERSE_QUADRATIC = "inverse_quadratic"
