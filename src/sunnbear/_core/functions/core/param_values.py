"""This module defines parameter notations and the operations on parameter values.

A parameter value is a plain float.

**A notation maps a continuous argument to a value.** The argument is the value itself for
`DECIMAL` and the exponent for `POW2`/`POW10`. A grid sweeps the argument, and building a value
rounds the argument to `CANONICAL_DIGITS` significant digits.

A power notation's value then follows from its rounded exponent by plain exponentiation and is not
rounded itself, so a value authored as ``2^1.23`` is exactly ``2 ** 1.23``, and a reader who
computes ``2 ** 1.23`` from a paper or a suite file gets the same float.

**The notation matters only while a value is built.** Afterwards a value is written in its
canonical spelling (see `ParamNotation`), which depends on the float alone: ``2^2.0`` and
``4.0`` are one value with one spelling.

Collapsing values that agree to `DEDUP_DIGITS` significant digits but are different floats is
a separate pass, `deduplicate_param_tuples`, not part of equality: a tolerance in equality would
make 2 values equal even though their canonical spellings differ, so equal ids could render as
different strings.
"""

from collections.abc import Iterable
from enum import StrEnum
from math import isfinite, log2, log10
from typing import assert_never

# The root precision constant: significant digits an argument is snapped to, absorbing the
# float error of grid arithmetic (`start + i * step`). Chosen as 3/4 of float64's ~16
# significant digits — far enough above ulp noise to be robust with healthy margin, small
# enough to still clearly be noise cleanup rather than value engineering. Every other
# precision constant in this module derives from this one.
CANONICAL_DIGITS = 12

# Significant digits at which two parameter values count as the same exact-math number seen
# through different notations. Why 2 decades below CANONICAL_DIGITS suffices (first-order
# error propagation): the canonical snap at C digits has relative resolution ~10^-(C-1). A
# decimal stores its value directly, so that is its whole error. An exponential stores its
# *exponent* snapped at C digits, and the derivation value = b^e amplifies a relative
# exponent error eps to a relative value error ~ln(b)*|e|*eps. The worst cross-notation
# discrepancy between two spellings of one exact value is therefore
# delta ~ ln(10)*|e|*10^-(C-1). Deduplication collapses reliably when its key resolution
# 10^-(D-1) comfortably exceeds delta; with D = C - 2 the margin is
# 10^(C-D) / (ln(10)*|e|) ~ 43/|e| — a >=4x margin for exponents up to ~10 and still >=1 up
# to |e| ~ 43, where a single decade would already fail around |e| ~ 4.
DEDUP_DIGITS = CANONICAL_DIGITS - 2


# ==================================================================================================
#  ParamNotation
# ==================================================================================================
class ParamNotation(StrEnum):
    """Each supported notation maps a continuous argument to a parameter value.

    **Validity rule.** A float is a valid parameter value only if at least one notation spells it
    with an argument of `CANONICAL_DIGITS` significant digits or fewer. A notation spells a float
    when it writes it as text, such as ``0.3`` or ``2^1.23``, that parses back to exactly that float.

    Every value that sunnbear builds meets the rule, because both of its ways to build a value —
    `build_value_from_argument` for a recipe grid and `parse_value` for a spelling — round the
    argument to `CANONICAL_DIGITS` significant digits.

    A float passed directly to `FunctionId`, such as ``0.1 + 0.2``, is not checked until the id is
    rendered; `is_valid_value` checks it up front.

    **Canonical spelling.** `spell_value_canonically` spells a valid value in every notation that
    can spell it under the validity rule and returns the shortest spelling, so the spelling depends
    on the float alone, not on how it was authored: ``2^2.0`` and ``4.0`` both spell as ``4.0``.

    A tie in length goes to the notation declared first below.

    Power spellings depend on the platform's ``pow``, which is not guaranteed to be correctly
    rounded: ``2^1.23`` can parse to a float that differs in the last bit on another platform, so one
    id string can stand for slightly different floats on 2 platforms.

    The test functions' own results already differ in the last bit across platforms, so the
    platform's ``pow`` adds no new source of difference.
    """

    DECIMAL = "decimal"  # value = argument
    POW2 = "pow2"  # value = 2 ** argument
    POW10 = "pow10"  # value = 10 ** argument

    # --------------------------------------------------------------------------
    #  Building and parsing a value
    # --------------------------------------------------------------------------
    def build_value_from_argument(self, argument: float) -> float:
        """Return the value of `argument` in this notation, after rounding `argument` to `CANONICAL_DIGITS` digits.

        The rounding is to significant digits. A non-finite argument is rejected, because a NaN would
        quietly break equality, hashing and deduplication.

        Raises:
            ValueError: If `argument` is not finite, or ``base ** argument`` overflows to a non-finite value.
        """
        if not isfinite(argument):
            raise ValueError(f"A parameter value's argument must be finite (got {argument!r}).")
        return self._build_value_from_rounded_argument(_round_argument(argument))

    @classmethod
    def parse_value(cls, token: str) -> float:
        """Parse one spelling (``0.4``, ``1e-05``, ``2^1.2``, ``10^-3.4``) back into its value.

        The number after ``^``, or the whole token for a decimal, is rounded as
        `build_value_from_argument` rounds its argument, so a spelling of a valid value parses back to
        exactly that value.

        Raises:
            ValueError: If the token uses an exponent base other than 2 or 10, is malformed, or gives a
                non-finite value; for an unsupported base or a malformed token, the message names the
                token.
        """
        if "^" in token:
            base_text, _, argument_text = token.partition("^")
            notation = {"2": cls.POW2, "10": cls.POW10}.get(base_text)
            if notation is None:
                raise ValueError(f"Unsupported exponent base {base_text!r} in token {token!r} (supported: 2, 10).")
        else:
            notation, argument_text = cls.DECIMAL, token
        try:
            argument = float(argument_text)
        except ValueError as exc:
            raise ValueError(f"Malformed parameter token {token!r}.") from exc
        return notation.build_value_from_argument(argument)

    # --------------------------------------------------------------------------
    #  Canonical spelling
    # --------------------------------------------------------------------------
    @classmethod
    def spell_value_canonically(cls, value: float) -> str:
        """Return the canonical spelling of `value`: its shortest valid spelling.

        A tie in length goes to the notation declared first. ``-0.0`` spells as ``0.0``, since the two
        are equal floats.

        Raises:
            ValueError: If no notation spells `value` exactly with an argument of `CANONICAL_DIGITS`
                significant digits or fewer.
        """
        spellings = [spelling for notation in cls if (spelling := notation.spell_value(value)) is not None]
        if not spellings:
            raise ValueError(
                f"{value!r} is not a valid parameter value: no notation spells it exactly with an argument "
                f"of {CANONICAL_DIGITS} significant digits or fewer."
            )
        # min returns the first of several equal-length spellings, and the list follows declaration order
        return min(spellings, key=len)

    @classmethod
    def is_valid_value(cls, value: float) -> bool:
        """Return whether `value` is a valid parameter value.

        A value is valid if some notation spells it exactly with an argument of `CANONICAL_DIGITS`
        significant digits or fewer.
        """
        return any(notation.spell_value(value) is not None for notation in cls)

    def spell_value(self, value: float) -> str | None:
        """Return this notation's spelling of `value`, or None if it cannot spell `value` under the validity rule."""
        # --- validation ---------------------------
        value = value + 0.0  # adding 0.0 turns -0.0 into 0.0, so the two equal floats spell alike
        if not isfinite(value) or (self is not ParamNotation.DECIMAL and value <= 0.0):
            return None  # a power of 2 or 10 is finite and positive

        # --- spell value --------------------------
        # for a power, recover the exponent of a valid value; the comparison below rejects the value
        # if the recovered exponent, once rounded, does not reproduce the value
        match self:
            case ParamNotation.DECIMAL:
                argument = value
            case ParamNotation.POW2:
                argument = log2(value)
            case ParamNotation.POW10:
                argument = log10(value)
            case _:
                assert_never(self)
        argument = _round_argument(argument)
        if self._build_value_from_rounded_argument(argument) == value:
            return self._spell_rounded_argument(argument)
        else:
            return None

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    def _build_value_from_rounded_argument(self, argument: float) -> float:
        """Return the value of an already rounded `argument`: the argument itself, or a power of the base.

        Raises:
            ValueError: If the power overflows to a non-finite value.
        """
        match self:
            case ParamNotation.DECIMAL:
                return argument
            case ParamNotation.POW2 | ParamNotation.POW10:
                try:
                    return float(self._power_base) ** argument
                except OverflowError as exc:
                    raise ValueError(f"{self._power_base}^{argument!r} overflows to a non-finite value.") from exc
            case _:
                assert_never(self)

    def _spell_rounded_argument(self, argument: float) -> str:
        """Write an already rounded `argument` in this notation, e.g. ``0.4`` or ``2^1.2``."""
        match self:
            case ParamNotation.DECIMAL:
                return repr(argument)
            case ParamNotation.POW2 | ParamNotation.POW10:
                return f"{self._power_base}^{argument!r}"
            case _:
                assert_never(self)

    @property
    def _power_base(self) -> int:
        """Return the base of a power notation: 2 or 10."""
        return 2 if self is ParamNotation.POW2 else 10


# ==================================================================================================
#  Near-duplicate removal
# ==================================================================================================
def deduplicate_param_tuples(
    tuples: Iterable[tuple[float, ...]], digits: int = DEDUP_DIGITS
) -> tuple[tuple[float, ...], ...]:
    """Keep the first tuple of each group whose values agree to `digits` significant digits.

    The one collapse this level performs: two tuples count as duplicates iff
    they could plausibly be the same exact-math values seen through different
    notations, showing up as different floats only because of float rounding
    error — ``10^0.5`` from a POW10 axis and ``3.16227766017`` from a DECIMAL
    axis, which exact float equality leaves as two.

    Tuples whose floats are exactly equal, such as ``4.0`` and ``2^2.0``, are
    already one value; they collapse here too. The default `digits` is 2 less
    than `CANONICAL_DIGITS`; the comment at `DEDUP_DIGITS` explains why that
    margin suffices.

    Deduplication is a filter, not an equality, because the granularity is a
    parameter; which tuple of a group is kept follows the input order.

    Grouping is by rounded key, not pairwise distance, so the partition is
    deterministic and the pass is linear. The cost is that a pair of *noisy*
    values straddling a bucket boundary survives as two tuples — buckets are
    centered on round values (see `_round_significant`), so this cannot hit a
    canonical value — and it is immaterial here anyway, since the corpus's
    diversity selection is free to drop one later.

    Args:
        tuples: Candidate parameter tuples, in materialization order.
        digits: Significant digits at which two parameter tuples count as one.

    Returns:
        The kept tuples, in first-seen order.
    """
    seen: set[tuple[float, ...]] = set()
    kept: list[tuple[float, ...]] = []
    for param_values in tuples:
        key = tuple(_round_significant(value, digits) for value in param_values)
        if key in seen:
            continue
        seen.add(key)
        kept.append(param_values)
    return tuple(kept)


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _round_significant(x: float, digits: int) -> float:
    """Round a float to `digits` significant digits.

    Rounds to *nearest* (``format`` half-even semantics), so when used as a
    bucketing key the buckets are **centered on** round values, with boundaries
    at the midpoints between representable `digits`-digit numbers — ``4.0``'s
    bucket spans roughly ``4.0 ± 0.5`` units in the last kept digit. Round
    numbers are therefore bucket centers, never boundaries: a canonical value
    like ``2^2.0 == 4.0`` and anything within half a bucket of it share a key.
    Two *noisy* values can still straddle a midpoint boundary and land in
    different buckets — that is the residual straddle case documented at
    `deduplicate_param_tuples`.
    """
    return float(f"{x:.{digits}g}")


def _round_argument(x: float) -> float:
    """Round an argument to `CANONICAL_DIGITS` significant digits."""
    return _round_significant(x, CANONICAL_DIGITS)
