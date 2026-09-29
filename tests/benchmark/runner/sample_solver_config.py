"""`SampleBisectionConfig` is a solver config that only a test registers, by importing this module.

A module-level import would register the config for every later test, so tests import this module by name,
inside `isolated_solver_config_registry`.
"""

from sunnbear.solvers import Bisection, SolverConfig, SolverRole


class SampleBisection(Bisection):
    """`SampleBisection` is `Bisection` under the name ``sample_bisection``, which no shipped config uses."""

    name = "sample_bisection"


class SampleBisectionConfig(SolverConfig):
    """`SampleBisectionConfig` configures `SampleBisection`."""

    solver_cls = SampleBisection
    role = SolverRole.USER_OTHER
