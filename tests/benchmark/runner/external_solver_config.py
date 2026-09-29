"""`ExternalBisectionConfig` is a solver config, registered only when a test imports this module.

A test file that imported this module at its top would register the config for every test that runs after the import,
so a test imports this module by its module name at run time, inside the `isolated_solver_config_registry`
fixture.
"""

from sunnbear.solvers import Bisection, SolverConfig, SolverRole


class ExternalBisection(Bisection):
    """`ExternalBisection` is `Bisection` under a name that no shipped config uses."""

    name = "external_bisection"


class ExternalBisectionConfig(SolverConfig):
    """`ExternalBisectionConfig` configures `ExternalBisection`."""

    solver_cls = ExternalBisection
    role = SolverRole.USER_OTHER
