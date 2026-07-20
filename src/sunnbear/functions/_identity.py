"""Stable identity of a test function: formula number plus its bound parameter tuple.

A `FunctionId` is the pair *(formula number, parameter tuple)* — nothing else.
In particular there is no materialization-order counter: which recipe produced a
parameter tuple, or in which order, never affects identity, so identities are
stable under recipe edits and reordering.

**Identities are faithful.** A parameter authored as ``2^1.23`` is stored as that
exponent and evaluated as ``2 ** 1.23``, not as a rounded stand-in — so the
number sunnbear computes with is exactly the one its notation advertises, and a
reader reproducing it from a paper or a suite file arrives at the same float.
There is a single rendering, notation-carrying and parsed back losslessly by
`from_string`.

Canonicalization applies to whatever the grid arithmetic produced, since that is
where float noise enters: the *value* of a linear axis (``start + i * step``),
and the *exponent* of a log-spaced one. An exponential's value then follows from
its canonical exponent by plain exponentiation, itself untouched.

Equality, hashing, and ordering are therefore **exact**: two ids match when they
carry the same formula and the same parameter values in the same notation.
Collapsing test functions that are merely *close* is a separate, deliberate
pass — `deduplicate_ids` — because a tolerance folded into ``__eq__`` would force
the rendering to be lossy to match it, which is precisely the faithfulness this
module exists to keep.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite

# Significant digits a grid quantity is snapped to, absorbing the float error accumulated
# by `start + i * step`. Deliberately finer than DEDUP_DIGITS: this cleans up arithmetic
# noise, it does not decide which test functions count as distinct.
CANONICAL_DIGITS = 10

# Significant digits at which two parameter tuples are treated as the same test function.
# Coarser than CANONICAL_DIGITS on purpose, so near-duplicates collapse with margin — the
# corpus wants diverse functions, not neighbours separated in the tenth digit.
DEDUP_DIGITS = 8


def _round_significant(x: float, digits: int) -> float:
    """Round a float to `digits` significant digits."""
    return float(f"{x:.{digits}g}")


def _canonical(x: float) -> float:
    """Snap a grid quantity to the framework's canonical precision."""
    return _round_significant(x, CANONICAL_DIGITS)


# ==================================================================================================
#  ParamValue
# ==================================================================================================
@dataclass(frozen=True)
class ParamValue(ABC):
    """A parameter value, in the notation it was authored in.

    One subclass per notation, so a value cannot carry fields belonging to a
    notation it does not use. Construct through the factories on this class
    (`decimal`, `exponential`, `parse`) rather than the subclasses directly.

    **Each notation canonicalizes its own grid quantity**, in its
    `__post_init__` — the value for a plain decimal, the exponent for an
    exponential. That is where the sweep's float error lands, and confining the
    snap to it is what keeps the value a notation reports identical to the value
    it evaluates to.

    Equality is plain field equality, so it *is* notation-sensitive: `2^2.0` and
    `4.0` are distinct values that happen to coincide numerically. Collapsing
    them is `deduplicate_ids`'s job, not equality's.
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
        """Render the authored notation; `from_string` parses it back to this value."""
        return self.display()

    def __str__(self) -> str:
        """Same as `__repr__` — there is one rendering, so both agree."""
        return repr(self)


@dataclass(frozen=True, repr=False)  # repr=False: inherit the notation-carrying __repr__ from the base
class DecimalParamValue(ParamValue):
    """A parameter value authored as a plain decimal."""

    def __post_init__(self) -> None:
        """Reject non-finite values, then canonicalize — for this notation, the value *is* the grid quantity.

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
    """A parameter value authored as ``base^exponent``, as log-spaced grids produce.

    `__post_init__` enforces this notation's invariants on every construction
    path: the base is validated and normalized to `int` (``2.0``/``10.0`` are
    accepted), the exponent is canonicalized as the grid quantity, and the value
    is *derived* from the two — so `value` never drifts from what the notation
    says, and any `value` handed to the constructor is replaced.

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
#  FunctionId
# ==================================================================================================
@dataclass(frozen=True)
class FunctionId:
    """Identity of one test function: formula number + the bound parameter tuple.

    Equality and hashing are the dataclass defaults — exact, and notation-aware,
    since the parameter values carry their notation. Rendering is faithful and
    re-parseable (see the module docstring); collapsing near-identical functions
    belongs to `deduplicate_ids`.
    """

    formula: int
    params: tuple[ParamValue, ...]

    @property
    def param_values(self) -> tuple[float, ...]:
        """Return the plain float values, e.g. for handing to formula code."""
        return tuple(p.value for p in self.params)

    def __lt__(self, other: "FunctionId") -> bool:
        """Order by formula number, then parameter values."""
        return (self.formula, self.param_values) < (other.formula, other.param_values)

    # --------------------------------------------------------------------------
    #  Rendering
    # --------------------------------------------------------------------------
    def display(self) -> str:
        """Render with each parameter's authored notation, e.g. ``f105-2^1.2_0.4``."""
        if not self.params:
            return f"f{self.formula:03d}"
        return f"f{self.formula:03d}-" + "_".join(p.display() for p in self.params)

    def __repr__(self) -> str:
        """Render the faithful form; `from_string` parses it back to this identity."""
        return self.display()

    def __str__(self) -> str:
        """Same as `__repr__` — there is one rendering, so both agree."""
        return repr(self)

    @classmethod
    def from_string(cls, text: str) -> "FunctionId":
        """Parse a rendered identity back into a `FunctionId`.

        Raises:
            ValueError: If `text` does not follow the rendered form.
        """
        if not text.startswith("f"):
            raise ValueError(f"Invalid FunctionId string: {text!r}")
        number_part, dash, params_part = text[1:].partition("-")
        if dash and not params_part:  # trailing dash: "f101-" is not the rendering of any identity
            raise ValueError(f"Invalid FunctionId string: {text!r}")
        try:
            formula = int(number_part)
            params = tuple(ParamValue.parse(token) for token in params_part.split("_")) if params_part else ()
        except ValueError as exc:
            raise ValueError(f"Invalid FunctionId string: {text!r}") from exc
        return cls(formula=formula, params=params)


# ==================================================================================================
#  Near-duplicate removal
# ==================================================================================================
def deduplicate_ids(ids: Iterable[FunctionId], digits: int = DEDUP_DIGITS) -> tuple[FunctionId, ...]:
    """Keep the first id of each group whose parameter values agree to `digits` significant digits.

    A filter rather than an equality, and deliberately so: the granularity is a
    parameter, and which member of a group survives follows the input order. It
    is what collapses the same value reached through different notations (a
    linear axis hitting ``4.0``, a log2 axis hitting ``2^2.0``), which exact
    identity equality leaves as two.

    Grouping is by rounded key, not pairwise distance, so the partition is
    deterministic and the pass is linear. The cost is that a pair straddling a
    rounding boundary survives as two ids — immaterial here, since the corpus's
    diversity selection is free to drop one later.

    Args:
        ids: Candidate identities, in materialization order.
        digits: Significant digits at which two parameter tuples count as one.

    Returns:
        The kept identities, in first-seen order.
    """
    seen: set[tuple[int, tuple[float, ...]]] = set()
    kept: list[FunctionId] = []
    for function_id in ids:
        key = (function_id.formula, tuple(_round_significant(v, digits) for v in function_id.param_values))
        if key in seen:
            continue
        seen.add(key)
        kept.append(function_id)
    return tuple(kept)
