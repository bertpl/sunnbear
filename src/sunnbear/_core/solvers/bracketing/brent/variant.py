"""This module holds `BrentVariant`, the variants of `Brent`."""

from enum import StrEnum


class BrentVariant(StrEnum):
    """`BrentVariant` names the variants of `Brent`, 1 per form of its 3-point step; `Brent` describes each variant."""

    HYPERBOLIC = "hyperbolic"
    INVERSE_QUADRATIC = "inverse_quadratic"
