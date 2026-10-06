"""This module holds `RiddersVariant`, the variants of `Ridders`."""

from enum import StrEnum


class RiddersVariant(StrEnum):
    """`RiddersVariant` names the 3 variants of `Ridders`, 1 per reference implementation; `Ridders` describes each."""

    COMMONS_MATH = "commons_math"
    SCIPY = "scipy"
    BRACKETING_SOLVER = "bracketing_solver"
