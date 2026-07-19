"""Stable identity of a test function: formula number plus its bound parameter tuple.

A `FunctionId` is the pair *(formula number, parameter tuple)* — nothing else.
In particular there is no materialization-order counter: which recipe produced
a parameter tuple, or in which order, never affects identity, so identities
are stable under recipe edits, reordering, and deduplication.

Parameter values are `ParamValue` objects that *carry* the notation they were
authored in (plain decimal, or an exponent on base 2/10 for log-spaced grids),
so a notation-carrying rendering needs no reverse-engineering of notation from
bare floats — and `from_string` parses either rendering back.

**Two renderings, and which is the default matters.** ``str()`` and ``repr()``
both produce the *canonical* form: plain decimals, independent of notation, so
that equal identities always produce equal strings. `display` produces the
notation-carrying form (``f105-2^1.2_0.4``) for human-facing output — suite
files, gallery labels, error messages. The safe form is the default because
the unsafe one fails silently: keying storage on a notation-carrying string
would give one candidate two keys the moment an author switched a linear axis
to a log2 one — never a wrong answer, just unbounded recomputation that
nothing reports.

Identity semantics live on `FunctionId`, and are **by parameter value, not
notation**: two recipes can legitimately generate the same value in different
notations (a linear axis hitting ``4.0``, a log2 axis hitting ``2^2.0``), and
those must be *one* test function — so `FunctionId` compares, hashes, and
orders on the float values, making "throw all candidates' ids in a set" the
complete deduplication story. `ParamValue` itself is a plain value object
(notation included in its own equality), modelled as one subclass per
notation so that no value carries fields belonging to a notation it does not
use.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ==================================================================================================
#  ParamValue
# ==================================================================================================
def _canonical(x: float) -> float:
    """Round a float to 10 significant digits — the framework's identity granularity."""
    return float(f"{x:.10g}")


@dataclass(frozen=True)
class ParamValue(ABC):
    """A parameter value, in the notation it was authored in.

    One subclass per notation, so a value cannot carry fields belonging to a
    notation it does not use. Construct through the factories on this class
    (`decimal`, `exponential`, `parse`) rather than the subclasses directly.

    **The canonical-value invariant lives here**, in `__post_init__`: `value`
    is rounded to 10 significant digits on *every* construction path, whatever
    the notation. That is what makes the canonical rendering re-parse to the
    same value, and it is deliberately not left to the subclasses — a variant
    that forgot the step would produce identities that silently fail to
    round-trip through storage. Consequence, by design: two parameters
    differing only beyond the 10th significant digit are one parameter.

    Equality is plain field equality, so it *is* notation-sensitive; identity
    comparisons, where notation must be invisible, happen at the `FunctionId`
    level (see the module docstring).
    """

    value: float

    def __post_init__(self) -> None:
        """Enforce the canonical-value invariant for every notation."""
        object.__setattr__(self, "value", _canonical(self.value))

    # --------------------------------------------------------------------------
    #  Construction
    # --------------------------------------------------------------------------
    @classmethod
    def decimal(cls, value: float) -> "ParamValue":
        """Build a plain-decimal parameter value."""
        return DecimalParamValue(value=value)

    @classmethod
    def exponential(cls, base: int, exponent: float) -> "ParamValue":
        """Build a ``base^exponent`` parameter value (base 2 or 10)."""
        if base not in (2, 10):
            raise ValueError(f"ParamValue supports exponent notation on base 2 or 10 (got {base}).")
        canonical_exponent = _canonical(exponent)
        return ExponentialParamValue(
            value=float(base) ** canonical_exponent,
            base=base,
            exponent=canonical_exponent,
        )

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
    def __repr__(self) -> str:
        """Render the canonical token: a plain decimal, independent of notation."""
        return repr(self.value)

    def __str__(self) -> str:
        """Same as `__repr__` — so equal values look equal wherever they are printed."""
        return repr(self)

    @abstractmethod
    def display(self) -> str:
        """Render with the authored notation — for humans, never for keys."""


@dataclass(frozen=True, repr=False)  # repr=False: inherit the canonical __repr__ from the base
class DecimalParamValue(ParamValue):
    """A parameter value authored as a plain decimal."""

    def display(self) -> str:
        """Render the value as a plain decimal — identical to the canonical form."""
        return repr(self.value)


@dataclass(frozen=True, repr=False)  # repr=False: inherit the canonical __repr__ from the base
class ExponentialParamValue(ParamValue):
    """A parameter value authored as ``base^exponent``, as log-spaced grids produce.

    The exponent is canonicalized alongside the value (which the base class
    handles), so both the authored and the canonical renderings are stable.

    Attributes:
        base: 2 or 10.
        exponent: The canonicalized exponent.
    """

    base: int
    exponent: float

    def display(self) -> str:
        """Render as ``base^exponent``, e.g. ``2^1.2``."""
        return f"{self.base}^{self.exponent!r}"


# ==================================================================================================
#  FunctionId
# ==================================================================================================
@dataclass(frozen=True, eq=False)
class FunctionId:
    """Identity of one test function: formula number + the bound parameter tuple.

    Equality, hashing, and ordering are by ``(formula, parameter float
    values)`` — notation-blind, so a set of `FunctionId`s deduplicates test
    functions regardless of how their parameters were spelled. ``str()`` and
    ``repr()` render the matching canonical form; `display` renders the
    authored notation (see the module docstring).
    """

    formula: int
    params: tuple[ParamValue, ...]

    @property
    def param_values(self) -> tuple[float, ...]:
        """Return the plain float values, e.g. for handing to formula code."""
        return tuple(p.value for p in self.params)

    # --------------------------------------------------------------------------
    #  Identity: by (formula, float values), notation-blind
    # --------------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        """Compare by formula number and parameter float values."""
        if isinstance(other, FunctionId):
            return (self.formula, self.param_values) == (other.formula, other.param_values)
        return NotImplemented

    def __hash__(self) -> int:
        """Hash consistently with the notation-blind equality."""
        return hash((self.formula, self.param_values))

    def __lt__(self, other: "FunctionId") -> bool:
        """Order by formula number, then parameter float values."""
        return (self.formula, self.param_values) < (other.formula, other.param_values)

    # --------------------------------------------------------------------------
    #  Rendering
    # --------------------------------------------------------------------------
    def __repr__(self) -> str:
        """Render the canonical form, e.g. ``f101-0.2`` — what storage and cache keys use."""
        if not self.params:
            return f"f{self.formula:03d}"
        return f"f{self.formula:03d}-" + "_".join(repr(p) for p in self.params)

    def __str__(self) -> str:
        """Same as `__repr__` — identity-consistent, so equal ids look equal when printed."""
        return repr(self)

    def display(self) -> str:
        """Render with each parameter's authored notation, e.g. ``f105-2^1.2_0.4``.

        For human-facing output only; `from_string` parses it back, but keying
        storage on it would split one identity across two keys.
        """
        if not self.params:
            return f"f{self.formula:03d}"
        return f"f{self.formula:03d}-" + "_".join(p.display() for p in self.params)

    @classmethod
    def from_string(cls, text: str) -> "FunctionId":
        """Parse a canonical string form back into a `FunctionId`.

        Raises:
            ValueError: If `text` does not follow the canonical form.
        """
        if not text.startswith("f"):
            raise ValueError(f"Invalid FunctionId string: {text!r}")
        number_part, _, params_part = text[1:].partition("-")
        try:
            formula = int(number_part)
            params = tuple(ParamValue.parse(token) for token in params_part.split("_")) if params_part else ()
        except ValueError as exc:
            raise ValueError(f"Invalid FunctionId string: {text!r}") from exc
        return cls(formula=formula, params=params)
