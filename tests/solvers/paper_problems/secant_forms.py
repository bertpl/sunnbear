"""`textbook_secant_zero` computes the secant's zero in the textbook form that several papers print and their code uses.

The shipped solvers compute the secant's zero in SciPy's form, `secant_zero`. A published table that depends on the
rounding of a paper's own form is checked against a test-only subclass whose ``_secant_zero`` takes that form;
`with_textbook_secant_zero` builds such a subclass for the textbook form.
"""

from sunnbear.solvers import Solver


def textbook_secant_zero(a: float, fa: float, b: float, fb: float) -> float:
    """Return the zero of the secant through ``(a, fa)`` and ``(b, fb)``, as ``(a*fb - b*fa) / (fb - fa)``."""
    return (a * fb - b * fa) / (fb - fa)


def with_textbook_secant_zero[SolverT: Solver](solver_cls: type[SolverT]) -> type[SolverT]:
    """Return a subclass of `solver_cls` whose secant steps take the textbook form of `textbook_secant_zero`."""
    return type(
        f"{solver_cls.__name__}WithTextbookSecantZero",
        (solver_cls,),
        {"_secant_zero": staticmethod(textbook_secant_zero)},
    )
