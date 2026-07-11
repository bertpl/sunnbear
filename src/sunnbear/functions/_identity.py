"""Stable identity of a test function: formula number plus its bound parameter tuple.

Identity is the parameter tuple itself (not a materialization-order counter),
so it is stable under recipe edits, reordering, and deduplication. The
canonical string form renders each parameter in its shortest exactly
round-tripping notation — plain decimal, ``2^e``, or ``10^e`` — keeping
storage keys human-readable even for log-spaced parameter grids.
"""

import math
from dataclasses import dataclass


# ==================================================================================================
#  Parameter value formatting
# ==================================================================================================
def format_param(value: float) -> str:
    """Render a parameter value in its shortest exactly round-tripping notation.

    Candidates are the plain decimal `repr`, ``2^e``, and ``10^e`` (with `e`
    itself in decimal `repr`); only notations that reproduce the exact float
    are considered, and ties prefer plain decimal.
    """
    candidates = [repr(value)]
    if value > 0.0:
        for log_fn, base, prefix in ((math.log2, 2.0, "2^"), (math.log10, 10.0, "10^")):
            exponent = _shortest_exact_exponent(value, base, log_fn(value))
            if exponent is not None:
                candidates.append(f"{prefix}{exponent!r}")
    return min(candidates, key=lambda s: (len(s), s != candidates[0]))


def _shortest_exact_exponent(value: float, base: float, exponent_raw: float) -> float | None:
    """Find the fewest-decimals exponent with ``base ** exponent == value`` exactly, if any.

    The raw logarithm can be off by an ulp from the short exponent that
    generated the value (e.g. ``10 ** -3.4``), so nearby rounded exponents are
    tried from coarse to fine before falling back to the raw one.
    """
    for decimals in range(13):
        exponent = round(exponent_raw, decimals)
        if base**exponent == value:
            return exponent
    return exponent_raw if base**exponent_raw == value else None


def parse_param(token: str) -> float:
    """Parse a single `format_param` token back to its float value."""
    for prefix, base in (("2^", 2.0), ("10^", 10.0)):
        if token.startswith(prefix):
            return base ** float(token.removeprefix(prefix))
    return float(token)


# ==================================================================================================
#  FunctionId
# ==================================================================================================
@dataclass(frozen=True, order=True)
class FunctionId:
    """Identity of one test function: formula number + the bound parameter tuple."""

    formula: int
    params: tuple[float, ...]

    # --------------------------------------------------------------------------
    #  Canonical string form
    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """Render the canonical string form, e.g. ``f101-0.2`` or ``f105-2^1.2_0.4``."""
        if not self.params:
            return f"f{self.formula:03d}"
        return f"f{self.formula:03d}-" + "_".join(format_param(p) for p in self.params)

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
            params = tuple(parse_param(token) for token in params_part.split("_")) if params_part else ()
        except ValueError as exc:
            raise ValueError(f"Invalid FunctionId string: {text!r}") from exc
        return cls(formula=formula, params=params)
