"""This module holds `EllithyVariant`, the variants of `Ellithy`."""

from enum import StrEnum


class EllithyVariant(StrEnum):
    """`EllithyVariant` names the variants of `Ellithy`, 1 per method of Ellithy (2026); `Ellithy` describes each."""

    BF = "bf"
    BFMS = "bfms"
    TF = "tf"
    TFMS = "tfms"

    @property
    def is_bisection(self) -> bool:
        """Return whether phase 1 of the variant's method is bisection; otherwise it is trisection."""
        return self in (EllithyVariant.BF, EllithyVariant.BFMS)

    @property
    def has_secant_step(self) -> bool:
        """Return whether the variant's method ends each iteration with the modified-secant step."""
        return self in (EllithyVariant.BFMS, EllithyVariant.TFMS)
