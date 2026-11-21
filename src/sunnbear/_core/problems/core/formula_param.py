"""`FormulaParam` declares 1 parameter of a formula: its name, and what a reader sees of it."""

from dataclasses import dataclass


# ==================================================================================================
#  FormulaParam
# ==================================================================================================
@dataclass(frozen=True)
class FormulaParam:
    r"""`FormulaParam` declares 1 parameter of a formula, as a `Formula` lists it in `params`.

    Attributes:
        name: The parameter's name in ids, recipes and the signatures of the formula's hooks, such as ``"alpha"``.
        latex_symbol: The parameter's symbol in LaTeX, such as ``r"\alpha"``, which replaces the parameter's
            placeholder when a formula renders its LaTeX with symbols. Optional here; the catalog's tests require it of
            every parameter of a shipped formula.
        meaning: Optional: what the parameter does, in a sentence for a reader, written only where the formula's
            expression does not make it obvious. The sentence writes its math in LaTeX, as `LatexTemplate` describes.
    """

    name: str
    latex_symbol: str | None = None
    meaning: str | None = None

    def __post_init__(self) -> None:
        """Check that `name` is a Python identifier, as the signatures of the formula's hooks need.

        Raises:
            ValueError: If `name` is not a Python identifier.
        """
        if not self.name.isidentifier():
            raise ValueError(f"A formula parameter's name must be a Python identifier (got {self.name!r}).")
