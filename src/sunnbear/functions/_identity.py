"""Stable identity of a test function: formula number plus its bound parameter tuple.

A `FunctionId` is the pair *(formula number, parameter tuple)* — nothing else.
In particular there is no materialization-order counter: which recipe produced a
parameter tuple, or in which order, never affects identity, so identities are
stable under recipe edits and reordering.

Identities inherit the faithfulness of their parameter values (see
`_param_values`): there is a single rendering, notation-carrying and parsed
back losslessly by `from_string`. Equality, hashing, and ordering are exact —
two ids match when they carry the same formula and the same parameter values
in the same notation; collapsing near-duplicate parameter tuples happens
*before* identities are built (`deduplicate_param_tuples`).
"""

from dataclasses import dataclass

from ._param_values import ParamValue


# ==================================================================================================
#  FunctionId
# ==================================================================================================
@dataclass(frozen=True)
class FunctionId:
    """Identity of one test function: formula number + the bound parameter tuple.

    Equality and hashing are the dataclass defaults — exact, and notation-aware,
    since the parameter values carry their notation. Rendering is faithful and
    re-parseable (see the module docstring).
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
