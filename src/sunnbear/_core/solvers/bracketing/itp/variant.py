"""This module holds `ITPVariant`, the variants of `ITP`."""

from enum import StrEnum


class ITPVariant(StrEnum):
    """`ITPVariant` names the 2 variants of `ITP`, 1 per source in its paper; `ITP` describes each."""

    PAPER_PSEUDOCODE = "paper_pseudocode"
    PAPER_EXPERIMENTS = "paper_experiments"
