"""This module holds `EXAMPLES_1_TO_7`, the problems of Examples 1 to 7 of Anderson and Björck (1973), each with the
paper's iteration count for `AndersonBjorck`, from the column "Alg. A"."""

from tests.solvers.paper_problems import UNSTATED_RUN_DETAILS
from tests.solvers.paper_problems.anderson_bjorck import AndersonBjorckExampleProblem

# The paper prints an iteration pattern for Example 1 and for the largest n of Examples 2 to 7; where a solve takes 1
# iteration more, its steps follow that pattern, and a step of delta follows them.
_ONE_MORE_STEP_OF_DELTA = "the solve takes 1 iteration more: a step of delta after the paper's last step"

# On Example 7, the solve takes 3 iterations for every n.
_EXAMPLE_7_ENDING = (
    "its 2nd iterate lies within 2e-15 of the root, and its 3rd, a step of delta, crosses the root and ends the solve"
)

EXAMPLES_1_TO_7 = [
    AndersonBjorckExampleProblem.EX1.with_n_iterations(
        5, deviation=1, reason=UNSTATED_RUN_DETAILS, observation=_ONE_MORE_STEP_OF_DELTA
    ),
    AndersonBjorckExampleProblem.EX2_N1.with_n_iterations(
        4,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation="the solve takes 1 iteration more, and its last iteration is a step of delta",
    ),
    AndersonBjorckExampleProblem.EX2_N5.with_n_iterations(8),
    AndersonBjorckExampleProblem.EX2_N15.with_n_iterations(10),
    AndersonBjorckExampleProblem.EX2_N20.with_n_iterations(
        10, deviation=1, reason=UNSTATED_RUN_DETAILS, observation=_ONE_MORE_STEP_OF_DELTA
    ),
    AndersonBjorckExampleProblem.EX3_N2.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX3_N5.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX3_N15.with_n_iterations(5),
    AndersonBjorckExampleProblem.EX3_N20.with_n_iterations(
        4, deviation=1, reason=UNSTATED_RUN_DETAILS, observation=_ONE_MORE_STEP_OF_DELTA
    ),
    AndersonBjorckExampleProblem.EX4_N2.with_n_iterations(1),
    AndersonBjorckExampleProblem.EX4_N5.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX4_N15.with_n_iterations(9),
    AndersonBjorckExampleProblem.EX4_N20.with_n_iterations(9),
    AndersonBjorckExampleProblem.EX5_N2.with_n_iterations(7),
    AndersonBjorckExampleProblem.EX5_N5.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX5_N15.with_n_iterations(5),
    AndersonBjorckExampleProblem.EX5_N20.with_n_iterations(
        4, deviation=1, reason=UNSTATED_RUN_DETAILS, observation=_ONE_MORE_STEP_OF_DELTA
    ),
    AndersonBjorckExampleProblem.EX6_N1.with_n_iterations(5),
    AndersonBjorckExampleProblem.EX6_N5.with_n_iterations(6),
    AndersonBjorckExampleProblem.EX6_N10.with_n_iterations(7),
    AndersonBjorckExampleProblem.EX6_N15.with_n_iterations(7),
    AndersonBjorckExampleProblem.EX6_N20.with_n_iterations(8),
    AndersonBjorckExampleProblem.EX7_N2.with_n_iterations(
        4,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=f"the solve takes 1 iteration fewer: {_EXAMPLE_7_ENDING}",
    ),
    AndersonBjorckExampleProblem.EX7_N5.with_n_iterations(
        5,
        deviation=2,
        reason=(
            "the count deviates for 2 causes that add up: the paper ran its examples in 27-bit arithmetic, and a port "
            "of `AndersonBjorck` that rounds every arithmetic result to 27 bits, to nearest or by truncation, takes 4 "
            f"iterations; and {UNSTATED_RUN_DETAILS}"
        ),
        observation=f"the solve takes 2 iterations fewer: {_EXAMPLE_7_ENDING}",
    ),
    AndersonBjorckExampleProblem.EX7_N15.with_n_iterations(
        4,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=f"the solve takes 1 iteration fewer: {_EXAMPLE_7_ENDING}",
    ),
    AndersonBjorckExampleProblem.EX7_N20.with_n_iterations(
        4,
        deviation=1,
        reason=UNSTATED_RUN_DETAILS,
        observation=f"the solve takes 1 iteration fewer: {_EXAMPLE_7_ENDING}",
    ),
]
