"""This module holds `RiddersVariant`, the variants of `Ridders`."""

from enum import StrEnum


class RiddersVariant(StrEnum):
    """`RiddersVariant` names the variants of `Ridders`, 1 per stopping criterion; `Ridders` describes each."""

    COMMONS_MATH = "commons_math"
    SCIPY = "scipy"
    STANDARD_STOPPING_CRITERION = "standard_stopping_criterion"
