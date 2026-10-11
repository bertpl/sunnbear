"""This package holds the shared code of the tests that reproduce published results: `PaperProblem`, the problem sets
that the papers of several solvers use, and `UNSTATED_RUN_DETAILS`.

Each solver's tests define their own list of `PaperProblem`s, with that solver's published results, and check a solve
with `PaperProblem.assert_reproduced_by`. A published table that several solvers reproduce is a `PaperProblemEnum`,
whose members return the table's problems with 1 solver's results. Results that are not per problem, such as a
table's total evaluation count, or the iterates of 1 worked example, are asserted by the solver's own tests.

A count that deviates by 1 from the published one is accepted with the reason `UNSTATED_RUN_DETAILS`: details of the
published run that the paper does not state can each shift a count by 1. A larger deviation needs a cause of its own.
"""

from .problem import UNSTATED_RUN_DETAILS, PaperProblem, PaperProblemEnum
