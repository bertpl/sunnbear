"""`textbook_secant_zero` computes the secant's zero in the textbook form that several papers' code uses."""


def textbook_secant_zero(a: float, fa: float, b: float, fb: float) -> float:
    """Return the zero of the secant through ``(a, fa)`` and ``(b, fb)``, as ``(a*fb - b*fa) / (fb - fa)``.

    A test-only solver subclass sets its ``_secant_zero`` to this function where a published table depends on the
    rounding of this form; the shipped solvers compute the secant's zero in SciPy's form, `secant_zero`.
    """
    return (a * fb - b * fa) / (fb - fa)
