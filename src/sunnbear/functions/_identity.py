"""Stable identity of a test function: formula number plus its bound parameter tuple.

A `FunctionId` is the pair *(formula number, parameter tuple)* — nothing else.
In particular there is no materialization-order counter: which recipe produced
a parameter tuple, or in which order, never affects identity, so identities
are stable under recipe edits, reordering, and deduplication.

Parameter values are `ParamValue` objects that *carry* the notation they were
authored in (plain decimal, or an exponent on base 2/10 for log-spaced grids),
so canonical strings like ``f105-2^1.2_0.4`` are rendered and parsed directly —
no reverse-engineering of notation from bare floats anywhere.

Identity semantics live on `FunctionId`, and are **by parameter value, not
notation**: two recipes can legitimately generate the same value in different
notations (a linear axis hitting ``4.0``, a log2 axis hitting ``2^2.0``), and
those must be *one* test function — so `FunctionId` compares, hashes, and
orders on the float values, making "throw all candidates' ids in a set" the
complete deduplication story. `ParamValue` itself is a plain value object
(notation included in its own equality).
"""

from dataclasses import dataclass


# ==================================================================================================
#  ParamValue
# ==================================================================================================
def _snap(x: float) -> float:
    """Canonicalize a float to 10 significant digits (shortest-repr friendly)."""
    return float(f"{x:.10g}")


@dataclass(frozen=True)
class ParamValue:
    """A parameter value carrying the notation it was authored in.

    The construction classmethods canonicalize their input (the decimal value,
    or the exponent for exponential notation) to **10 significant digits**, so
    ulp-level float noise can neither lengthen the rendered notation nor split
    identities. Warning: this also means two parameters differing only beyond
    the 10th significant digit are merged — identity granularity is 10
    significant digits by design.

    Equality of `ParamValue` itself is plain field equality (notation
    included); *identity* comparisons — where notation must be invisible —
    happen at the `FunctionId` level on the float values (see the module
    docstring).

    Attributes:
        value: The actual float handed to formula code; the identity datum.
        base: None for decimal notation; 2 or 10 for ``base^exponent`` notation.
        exponent: The (canonicalized) exponent for exponential notation.
    """

    value: float
    base: int | None = None
    exponent: float | None = None

    # --------------------------------------------------------------------------
    #  Construction
    # --------------------------------------------------------------------------
    @classmethod
    def decimal(cls, value: float) -> "ParamValue":
        """Build a plain-decimal parameter value."""
        return cls(value=_snap(value))

    @classmethod
    def exponential(cls, base: int, exponent: float) -> "ParamValue":
        """Build a ``base^exponent`` parameter value (base 2 or 10)."""
        if base not in (2, 10):
            raise ValueError(f"ParamValue supports exponent notation on base 2 or 10 (got {base}).")
        snapped = _snap(exponent)
        return cls(value=float(base) ** snapped, base=base, exponent=snapped)

    @classmethod
    def parse(cls, token: str) -> "ParamValue":
        """Parse one canonical-string token (``0.4``, ``2^1.2``, ``10^-3.4``).

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
    def __str__(self) -> str:
        """Render the canonical token: shortest repr, or ``base^exponent``."""
        if self.base is None:
            return repr(self.value)
        return f"{self.base}^{self.exponent!r}"


# ==================================================================================================
#  FunctionId
# ==================================================================================================
@dataclass(frozen=True, eq=False)
class FunctionId:
    """Identity of one test function: formula number + the bound parameter tuple.

    Equality, hashing, and ordering are by ``(formula, parameter float
    values)`` — notation-blind, so a set of `FunctionId`s deduplicates test
    functions regardless of how their parameters were spelled.
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
    #  Canonical string form
    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """Render the canonical string form, e.g. ``f101-0.2`` or ``f105-2^1.2_0.4``."""
        if not self.params:
            return f"f{self.formula:03d}"
        return f"f{self.formula:03d}-" + "_".join(str(p) for p in self.params)

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
