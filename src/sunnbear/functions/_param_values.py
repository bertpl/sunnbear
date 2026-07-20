"""Parameter values and their notations: faithful construction, canonicalization, dedup.

**A notation maps a continuous argument to a value.** The argument is the
quantity a grid sweeps and the quantity that gets canonicalized — the value
itself for `DECIMAL`, the exponent for `POW2`/`POW10`; an exponential's value
then follows from its canonical argument by plain exponentiation, itself
untouched.

**Values are faithful.** A parameter authored as ``2^1.23`` is stored as that
exponent and evaluated as ``2 ** 1.23``, not as a rounded stand-in — so the
number sunnbear computes with is exactly the one its notation advertises, and a
reader reproducing it from a paper or a suite file arrives at the same float.
There is a single rendering, notation-carrying and parsed back losslessly by
`ParamValue.parse`.

Equality and hashing are therefore **exact and notation-sensitive**: ``2^2.0``
and ``4.0`` are distinct values that happen to coincide numerically. Collapsing
two values that could plausibly be the same exact-math number seen through
different notations is a separate, deliberate pass — `deduplicate_param_tuples`
— because a tolerance folded into ``__eq__`` would force the rendering to be
lossy to match it, which is precisely the faithfulness this module exists to
keep.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

# The root precision constant: significant digits an argument is snapped to, absorbing the
# float error of grid arithmetic (`start + i * step`). Chosen as 3/4 of float64's ~16
# significant digits — far enough above ulp noise to be robust with healthy margin, small
# enough to still clearly be noise cleanup rather than value engineering. Every other
# precision constant in the package derives from this one.
CANONICAL_DIGITS = 12

# Significant digits at which two parameter values count as the same exact-math number seen
# through different notations. See `deduplicate_param_tuples` for the derivation of the
# 2-decade margin below CANONICAL_DIGITS.
DEDUP_DIGITS = CANONICAL_DIGITS - 2


def _round_significant(x: float, digits: int) -> float:
    """Round a float to `digits` significant digits."""
    return float(f"{x:.{digits}g}")


def _canonical(x: float) -> float:
    """Snap an argument to the framework's canonical precision."""
    return _round_significant(x, CANONICAL_DIGITS)


# ==================================================================================================
#  ParamNotation
# ==================================================================================================
class ParamNotation(StrEnum):
    """The supported notations; each maps a continuous argument to a parameter value."""

    DECIMAL = "decimal"  # value = argument
    POW2 = "pow2"  # value = 2 ** argument
    POW10 = "pow10"  # value = 10 ** argument

    def make(self, argument: float) -> "ParamValue":
        """Build the `ParamValue` whose (canonicalized) argument is `argument`."""
        if self is ParamNotation.DECIMAL:
            return ParamValue.decimal(argument)
        return ParamValue.exponential(2 if self is ParamNotation.POW2 else 10, argument)


# ==================================================================================================
#  ParamValue
# ==================================================================================================
@dataclass(frozen=True)
class ParamValue(ABC):
    """A parameter value, in the notation it was authored in.

    One subclass per notation shape, so a value cannot carry fields belonging
    to a notation it does not use. Construct through the factories on this
    class (`decimal`, `exponential`, `parse`) or through `ParamNotation.make`
    rather than the subclasses directly.

    **Each notation canonicalizes its own argument**, in its `__post_init__` —
    the value for a plain decimal, the exponent for an exponential. That is
    where the sweep's float error lands, and confining the snap to it is what
    keeps the value a notation reports identical to the value it evaluates to.

    Equality is plain field equality, so it *is* notation-sensitive: `2^2.0`
    and `4.0` are distinct values that happen to coincide numerically.
    Collapsing them is `deduplicate_param_tuples`'s job, not equality's.
    """

    value: float

    # --------------------------------------------------------------------------
    #  Construction
    # --------------------------------------------------------------------------
    @classmethod
    def decimal(cls, value: float) -> "ParamValue":
        """Build a plain-decimal parameter value."""
        return DecimalParamValue(value=value)

    @classmethod
    def exponential(cls, base: float, exponent: float) -> "ParamValue":
        """Build a ``base^exponent`` parameter value (base 2 or 10; ``2.0``/``10.0`` also accepted)."""
        if base not in (2, 10):
            raise ValueError(f"ParamValue supports exponent notation on base 2 or 10 (got {base!r}).")
        # value=0.0 is a placeholder: __post_init__ derives the real value from base and exponent
        return ExponentialParamValue(value=0.0, base=int(base), exponent=exponent)

    @classmethod
    def parse(cls, token: str) -> "ParamValue":
        """Parse one string token (``0.4``, ``2^1.2``, ``10^-3.4``).

        Raises:
            ValueError: On an unsupported exponent base or a malformed token,
                with the offending token named.
        """
        if "^" in token:
            base_text, _, exponent_text = token.partition("^")
            if base_text not in ("2", "10"):
                raise ValueError(f"Unsupported exponent base {base_text!r} in token {token!r} (supported: 2, 10).")
            try:
                return cls.exponential(int(base_text), float(exponent_text))
            except ValueError as exc:
                raise ValueError(f"Malformed exponent in token {token!r}.") from exc
        try:
            return cls.decimal(float(token))
        except ValueError as exc:
            raise ValueError(f"Malformed parameter token {token!r}.") from exc

    # --------------------------------------------------------------------------
    #  Rendering
    # --------------------------------------------------------------------------
    @abstractmethod
    def display(self) -> str:
        """Render this value in its authored notation — the one faithful form."""

    def __repr__(self) -> str:
        """Render the authored notation; `parse` reads it back to this value."""
        return self.display()

    def __str__(self) -> str:
        """Same as `__repr__` — there is one rendering, so both agree."""
        return repr(self)


@dataclass(frozen=True, repr=False)  # repr=False: inherit the notation-carrying __repr__ from the base
class DecimalParamValue(ParamValue):
    """A parameter value authored as a plain decimal."""

    def __post_init__(self) -> None:
        """Reject non-finite values, then canonicalize — for this notation, the value *is* the argument.

        Finiteness is an identity invariant: a NaN would quietly break equality,
        hashing and near-duplicate grouping, so it is rejected on every
        construction path rather than allowed to propagate.
        """
        if not isfinite(self.value):
            raise ValueError(f"ParamValue must be finite (got {self.value!r}).")
        object.__setattr__(self, "value", _canonical(self.value))

    def display(self) -> str:
        """Render the value as a plain decimal."""
        return repr(self.value)


@dataclass(frozen=True, repr=False)  # repr=False: inherit the notation-carrying __repr__ from the base
class ExponentialParamValue(ParamValue):
    """A parameter value authored as ``base^exponent``, as POW2/POW10 grids produce.

    `__post_init__` enforces this notation's invariants on every construction
    path: the base is validated and normalized to `int` (``2.0``/``10.0`` are
    accepted), the exponent — this notation's argument — is canonicalized, and
    the value is *derived* from the two — so `value` never drifts from what the
    notation says, and any `value` handed to the constructor is replaced.

    Attributes:
        base: 2 or 10 (stored as `int`).
        exponent: The canonicalized exponent.
    """

    base: int
    exponent: float

    def __post_init__(self) -> None:
        """Validate the base and exponent, canonicalize the exponent, then derive the value.

        Both the exponent and the derived value must be finite (see
        `DecimalParamValue.__post_init__` for why): a finite exponent can still
        overflow the derivation (e.g. ``10^400``), so that is rejected too.
        """
        if self.base not in (2, 10):
            raise ValueError(f"ParamValue supports exponent notation on base 2 or 10 (got {self.base!r}).")
        if not isfinite(self.exponent):
            raise ValueError(f"ParamValue exponent must be finite (got {self.exponent!r}).")
        object.__setattr__(self, "base", int(self.base))
        object.__setattr__(self, "exponent", _canonical(self.exponent))
        try:
            derived = float(self.base) ** self.exponent
        except OverflowError as exc:
            raise ValueError(f"ParamValue {self.base}^{self.exponent!r} overflows to a non-finite value.") from exc
        object.__setattr__(self, "value", derived)

    def display(self) -> str:
        """Render as ``base^exponent``, e.g. ``2^1.2``."""
        return f"{self.base}^{self.exponent!r}"


# ==================================================================================================
#  Near-duplicate removal
# ==================================================================================================
def deduplicate_param_tuples(
    tuples: Iterable[tuple[ParamValue, ...]], digits: int = DEDUP_DIGITS
) -> tuple[tuple[ParamValue, ...], ...]:
    """Keep the first tuple of each group whose values agree to `digits` significant digits.

    The one collapse this level performs: two tuples count as duplicates iff
    they could plausibly be the same exact-math values seen through different
    notations, showing up as different floats only through float arithmetic —
    a DECIMAL axis hitting ``4.0`` and a POW2 axis hitting ``2^2.0``, which
    exact notation-sensitive equality leaves as two.

    **Why 2 decades below `CANONICAL_DIGITS` suffices** (first-order error
    propagation): the canonical snap at ``C`` digits has relative resolution
    ``~10^-(C-1)``. A decimal stores its value directly, so that is its whole
    error. An exponential stores its *exponent* snapped at ``C`` digits, and
    the derivation ``value = b^e`` amplifies a relative exponent error ``eps``
    to a relative value error ``~ln(b) * |e| * eps``. The worst cross-notation
    discrepancy between two spellings of one exact value is therefore
    ``delta ~ ln(10) * |e| * 10^-(C-1)``. Deduplication collapses reliably when
    its key resolution ``10^-(D-1)`` comfortably exceeds ``delta``; with
    ``D = C - 2`` the margin is ``10^(C-D) / (ln(10) * |e|) ~ 43/|e|`` — a >=4x
    margin for exponents up to ~10 and still >=1 up to ``|e| ~ 43``, where a
    single decade would already fail around ``|e| ~ 4``.

    A filter rather than an equality, and deliberately so: the granularity is a
    parameter, and which member of a group survives follows the input order.
    Grouping is by rounded key, not pairwise distance, so the partition is
    deterministic and the pass is linear. The cost is that a pair straddling a
    rounding boundary survives as two tuples — immaterial here, since the
    corpus's diversity selection is free to drop one later.

    Args:
        tuples: Candidate parameter tuples, in materialization order.
        digits: Significant digits at which two parameter tuples count as one.

    Returns:
        The kept tuples, in first-seen order.
    """
    seen: set[tuple[float, ...]] = set()
    kept: list[tuple[ParamValue, ...]] = []
    for params in tuples:
        key = tuple(_round_significant(p.value, digits) for p in params)
        if key in seen:
            continue
        seen.add(key)
        kept.append(params)
    return tuple(kept)
