"""`BenchmarkRunSettings` holds the settings that every task of a benchmark run shares."""

from dataclasses import dataclass

from .mc_tuples import MCTuplesSize
from .tolerances import validate_n_bisection_fevals


@dataclass(frozen=True, kw_only=True)
class BenchmarkRunSettings:
    """`BenchmarkRunSettings` holds the settings that every task of a benchmark run shares.

    The settings travel together, into every task and into the record of the run, so a run's results can
    only be combined with results of the same settings.

    Attributes:
        mc_size: The size of the Monte Carlo tuple set, 1 of `MCTuplesSize`: the number of samples per
            (solver, test function) pair.
        n_bisection_fevals: Bisection's evaluation count, from which the `xtol` range and the evaluation
            budget follow.
        root_seed: The run's root seed, from which every seed of the run is derived.
    """

    mc_size: int
    n_bisection_fevals: int
    root_seed: int

    def __post_init__(self) -> None:
        """Check the settings, so an invalid `BenchmarkRunSettings` cannot be constructed.

        Raises:
            ValueError: If `mc_size` is not 1 of `MCTuplesSize`, or `n_bisection_fevals` is below 2.
        """
        MCTuplesSize(self.mc_size)
        validate_n_bisection_fevals(self.n_bisection_fevals)
