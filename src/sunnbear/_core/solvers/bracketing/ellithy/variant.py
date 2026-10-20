"""This module holds `EllithyVariant`, the variants of `Ellithy`."""

from enum import StrEnum


class EllithyVariant(StrEnum):
    """`EllithyVariant` names the variants of `Ellithy`, 1 per method of Ellithy (2026); `Ellithy` describes each."""

    BF = "bf"
    BFMS = "bfms"
    TF = "tf"
    TFMS = "tfms"
