"""This package holds the shared code of the tests that reproduce published results: `PaperProblem`, and the problem
sets that the papers of several solvers use.

Each solver's tests define their own list of `PaperProblem`s, with that solver's published results, and check a solve
with `PaperProblem.assert_reproduced_by`. Results that are not per problem, such as a table's total evaluation count,
or the iterates of 1 worked example, are asserted by the solver's own tests.
"""

from .problem import PaperProblem
