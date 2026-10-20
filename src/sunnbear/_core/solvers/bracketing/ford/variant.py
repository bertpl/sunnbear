"""This module holds `FordVariant`, the variants of `Ford`."""

from enum import StrEnum


class FordVariant(StrEnum):
    """`FordVariant` names the variants of `Ford`, 1 per method of Ford (1997); `Ford` describes each variant."""

    METHOD_1 = "method_1"
    METHOD_3 = "method_3"
    METHOD_4 = "method_4"
