"""This module holds `ModABVariant`, the variants of `ModAB`."""

from enum import StrEnum


class ModABVariant(StrEnum):
    """`ModABVariant` names the variants of `ModAB`, 1 per published version of the method; `ModAB` describes each."""

    ALGORITHMS_2026 = "algorithms_2026"
    SAFEGUARDED_2026 = "safeguarded_2026"
