"""These tests assert that every built-in solver's module docstring holds the record that
``IMPLEMENTATION_PRINCIPLES.md`` defines, and that the class docstring cites every source that the record names."""

import inspect
import re
import sys

import pytest

from sunnbear._core.utils.class_origin import is_defined_in_sunnbear
from sunnbear.solvers import (
    CARF,
    ITP,
    TOMS748,
    Brent,
    RegulaFalsi,
    Ridders,
    SolverConfigRegistry,
)

# Defining a SolverConfig subclass registers it, so the registry also holds the configs that test modules define;
# the built-in solvers are those of the configs defined inside the sunnbear package.
_BUILT_IN_SOLVER_CLASSES = list(
    dict.fromkeys(
        config.solver_cls for config in SolverConfigRegistry.configs() if is_defined_in_sunnbear(type(config))
    )
)

# The tests of these solvers are expected to fail; a solver whose record is added must leave this list, or its
# tests pass unexpectedly and fail the suite.
_SOLVER_CLASSES_WITHOUT_RECORD = {
    Brent,
    CARF,
    ITP,
    RegulaFalsi,
    Ridders,
    TOMS748,
}

_RECORD_HEADINGS = ("Sources:", "Source per aspect:", "Validation:", "Variants:")

# This pattern matches an author-year citation, such as "Atkinson (1989)" or "Ganchovski et al. (2026)"; its first
# group holds the surname, and its second the year.
_AUTHOR_YEAR_PATTERN = re.compile(r"(\w[\w'-]*)(?: et al\.)? \((\d{4})\)")


def _built_in_solver_cls_params():
    """Return 1 parameter per built-in solver class, marked as an expected failure while it has no record."""
    params = []
    for solver_cls in _BUILT_IN_SOLVER_CLASSES:
        if solver_cls in _SOLVER_CLASSES_WITHOUT_RECORD:
            marks = pytest.mark.xfail(strict=True, reason="the solver has no record yet")
        else:
            marks = ()
        params.append(pytest.param(solver_cls, marks=marks, id=solver_cls.__name__))
    return params


def _parse_record_sections(solver_cls) -> dict[str, str]:
    """Return the text under each record heading of the solver's module docstring, by heading."""
    lines = (sys.modules[solver_cls.__module__].__doc__ or "").splitlines()
    sections: dict[str, str] = {}
    heading = None
    for line in lines:
        if line in _RECORD_HEADINGS:
            heading = line
            sections[heading] = ""
        elif heading is not None:
            sections[heading] += line + "\n"
    return sections


@pytest.mark.parametrize("solver_cls", _built_in_solver_cls_params())
def test_the_module_docstring_holds_the_record_headings_in_order(solver_cls):
    """The solver's module docstring holds each record heading once, in the order of
    ``IMPLEMENTATION_PRINCIPLES.md``."""
    # --- arrange ----------------------
    lines = (sys.modules[solver_cls.__module__].__doc__ or "").splitlines()

    # --- act --------------------------
    headings = [line for line in lines if line in _RECORD_HEADINGS]

    # --- assert -----------------------
    assert headings == list(_RECORD_HEADINGS)


@pytest.mark.parametrize("solver_cls", _built_in_solver_cls_params())
def test_the_class_docstring_cites_every_source_of_the_record(solver_cls):
    """Every author and year that the record's ``Sources:`` names appears in 1 entry of the class's ``References:``."""
    # --- arrange ----------------------
    sources_text = _parse_record_sections(solver_cls)["Sources:"]
    references_text = inspect.cleandoc(solver_cls.__doc__ or "").partition("References:")[2]
    reference_entries = re.split(r"\n\s*- ", references_text)

    # --- act --------------------------
    uncited = []
    for surname, year in _AUTHOR_YEAR_PATTERN.findall(sources_text):
        is_cited = False
        for entry in reference_entries:
            if surname in entry and f"({year})" in entry:
                is_cited = True
        if not is_cited:
            uncited.append(f"{surname} ({year})")

    # --- assert -----------------------
    assert uncited == []
