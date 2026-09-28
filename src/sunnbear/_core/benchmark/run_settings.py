"""`BenchmarkRunSettings` holds the settings that every task of a benchmark run shares."""

from dataclasses import dataclass

from .mc_tuples import MC_TUPLES_SIZES
from .tolerances import validate_n_bisection_fevals


@dataclass(frozen=True, kw_only=True)
class BenchmarkRunSettings:
    """`BenchmarkRunSettings` holds the settings that every task of a benchmark run shares.

    The settings travel together, into every task and into the record of the run, so a run's results can
    only be combined with results of the same settings.

    Attributes:
        mc_size: The size of the Monte Carlo tuple set, 1 of `MC_TUPLES_SIZES`: the number of samples per
            (solver, test function) pair.
        n_bisection_fevals: Bisection's evaluation count, from which the `xtol` range and the evaluation
            budget follow.
        root_seed: The run's root seed, from which every seed of the run is derived.
    """

    mc_size: int
    n_bisection_fevals: int
    root_seed: int

    def __post_init__(self) -> None:
        """Check the settings, so a run with invalid settings fails before its first task.

        Raises:
            ValueError: If `mc_size` is not 1 of `MC_TUPLES_SIZES`, or `n_bisection_fevals` is below 2.
        """
        if self.mc_size not in MC_TUPLES_SIZES:
            raise ValueError(f"mc_size must be one of {list(MC_TUPLES_SIZES)} (got {self.mc_size}).")
        validate_n_bisection_fevals(self.n_bisection_fevals)
