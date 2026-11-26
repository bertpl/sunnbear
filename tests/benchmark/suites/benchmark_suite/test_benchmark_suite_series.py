"""`BenchmarkSuiteSeries` builds each suite of a size that it declares, with the suite's name, aliases and series id,
and refuses a declaration that could give 2 suites the same name or that declares a size that no suite can have.

The tests use an example series, so that a change to the built-in series leaves them as they are.
"""

import dataclasses

import pytest

from sunnbear._core.benchmark.suites.benchmark_suite import BenchmarkSuite, BenchmarkSuiteSeries
from sunnbear._core.problems.core import ProblemId

_EXAMPLE_SERIES = BenchmarkSuiteSeries(
    series_id="ex",
    readable_name="example series",
    summary="The example series serves the tests of the series model.",
    name_format="ex-{size}",
    sizes=(4, 2, 1),
    aliases_by_size={4: ("ex-large",)},
)


@pytest.mark.parametrize(
    "size, name_expected, aliases_expected",
    [
        pytest.param(4, "ex-4", ("ex-large",), id="with_aliases"),
        pytest.param(1, "ex-1", (), id="without_aliases"),
    ],
)
def test_the_series_builds_its_suite_of_each_size(size, name_expected, aliases_expected):
    """The suite of a declared size carries the series' id, the name of its size and that size's aliases."""
    # --- arrange ----------------------
    problem_ids = [ProblemId.from_string(f"f99.1[p={idx + 1}]") for idx in range(size)]

    # --- act --------------------------
    suite = _EXAMPLE_SERIES.build_suite(problem_ids)

    # --- assert -----------------------
    assert suite == BenchmarkSuite(
        series_id="ex", name=name_expected, aliases=aliases_expected, problem_ids=tuple(problem_ids)
    )


def test_the_series_refuses_a_suite_of_a_size_that_it_does_not_declare():
    """A suite of 3 test problems does not fit a series of the sizes 4, 2 and 1."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=r"^Series ex has no suite of 3 test problems; its sizes are \(4, 2, 1\)\.$"):
        _EXAMPLE_SERIES.build_suite([ProblemId.from_string(f"f99.1[p={idx + 1}]") for idx in range(3)])


@pytest.mark.parametrize(
    "changes, message_expected",
    [
        pytest.param({"name_format": "ex"}, r"The name format 'ex' of series ex has no field \{size\}\.", id="no_size"),
        pytest.param({"sizes": (4, 3)}, r"Every size of series ex must be a power of 2", id="not_a_power_of_2"),
        pytest.param({"sizes": (4, 0)}, r"Every size of series ex must be a power of 2", id="zero"),
        pytest.param({"sizes": (4, 2, 4)}, r"Series ex declares a size twice: \(4, 2, 4\)\.", id="size_twice"),
        pytest.param(
            {"aliases_by_size": {8: ("ex-huge",)}},
            r"Series ex gives aliases to sizes that it does not declare: \[8\]\.",
            id="alias_of_undeclared_size",
        ),
    ],
)
def test_the_series_refuses_an_invalid_declaration(changes, message_expected):
    """A name format without ``{size}``, a size that is not a power of 2 or is declared twice, and aliases of an
    undeclared size are refused."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match=message_expected):
        dataclasses.replace(_EXAMPLE_SERIES, **changes)
