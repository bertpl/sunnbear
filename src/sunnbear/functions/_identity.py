"""Stable identity of a test function: formula number plus its bound parameter tuple.

A `FunctionId` is the pair *(formula number, parameter tuple)* — nothing else.
In particular there is no materialization-order counter: which recipe produced
a parameter tuple, or in which order, never affects identity, so identities
are stable under recipe edits, reordering, and deduplication.

Parameter values are `ParamValue` objects that *carry* the notation they were
authored in (plain decimal, or an exponent on base 2/10 for log-spaced grids),
so canonical strings like ``f105-2^1.2_0.4`` are rendered and parsed directly —
no reverse-engineering of notation from bare floats anywhere.
"""

from dataclasses import dataclass


# ==================================================================================================
#  ParamValue
# ==================================================================================================
def _snap(x: float) -> float:
    """Canonicalize a float to 10 significant digits (shortest-repr friendly)."""
    return float(f"{x:.10g}")


@dataclass(frozen=True, eq=False)
class ParamValue:
    """A parameter value carrying the notation it was authored in.

    Identity (equality, hashing, ordering) is by `value` only — notation is
    presentation. The construction classmethods canonicalize their input (the
    decimal value, or the exponent for exponential notation) to **10
    significant digits**, so ulp-level float noise can neither lengthen the
    rendered notation nor split identities. Warning: this also means two
    parameters differing only beyond the 10th significant digit are merged —
    identity granularity is 10 significant digits by design.

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
    def coerce(cls, value: "ParamValue | float") -> "ParamValue":
        """Return `value` unchanged if already a `ParamValue`, else wrap it as decimal."""
        return value if isinstance(value, ParamValue) else cls.decimal(value)

    @classmethod
    def parse(cls, token: str) -> "ParamValue":
        """Parse one canonical-string token (``0.4``, ``2^1.2``, ``10^-3.4``)."""
        for prefix, base in (("2^", 2), ("10^", 10)):
            if token.startswith(prefix):
                return cls.exponential(base, float(token.removeprefix(prefix)))
        return cls.decimal(float(token))

    # --------------------------------------------------------------------------
    #  Identity: by value only
    # --------------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        """Compare by float value; notation is presentation, and bare floats compare too."""
        if isinstance(other, ParamValue):
            return self.value == other.value
        if isinstance(other, int | float):
            return self.value == float(other)
        return NotImplemented

    def __hash__(self) -> int:
        """Hash by float value, consistent with float-comparing equality."""
        return hash(self.value)

    def __lt__(self, other: "ParamValue | float") -> bool:
        """Order by float value."""
        other_value = other.value if isinstance(other, ParamValue) else float(other)
        return self.value < other_value

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
@dataclass(frozen=True, order=True)
class FunctionId:
    """Identity of one test function: formula number + the bound parameter tuple.

    `params` accepts bare floats for convenience; they are coerced to
    decimal-notation `ParamValue`s on construction.
    """

    formula: int
    params: tuple[ParamValue | float, ...]  # normalized to all-ParamValue in __post_init__

    def __post_init__(self) -> None:
        """Coerce any bare-float parameters to `ParamValue`."""
        object.__setattr__(self, "params", tuple(ParamValue.coerce(p) for p in self.params))

    @property
    def param_values(self) -> tuple[float, ...]:
        """Return the plain float values, e.g. for handing to formula code."""
        # coerce is an idempotent no-op at runtime (post-init normalized); it narrows for typing
        return tuple(ParamValue.coerce(p).value for p in self.params)

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
