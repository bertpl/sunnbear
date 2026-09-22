"""`SolverRole` decides how the benchmark treats a configured solver."""

from enum import Enum


# ==================================================================================================
#  SolverRole
# ==================================================================================================
class SolverRole(Enum):
    """`SolverRole` classifies a `SolverConfig`: is it reported, does it characterize, is it built-in only.

    Code that treats configs differently reads the properties below, never the member itself: several
    roles share the same treatment, so the properties derive from the role and cannot define it.

    Members:
        BUILTIN_BASELINE: The single reference solver. It sets the tolerance and normalizes the
            other solvers' costs; its evaluation count is fixed by construction, so it says nothing
            about a function.
        BUILTIN_CORE: A built-in solver whose results characterize the test functions.
        BUILTIN_SECONDARY: A built-in solver reported for information only: redundant with a core
            solver, or too unreliable to characterize but informative to show.
        USER_ACTIVE: A user's solver, benchmarked and reported beside the built-in ones.
        USER_OTHER: A user's solver that is registered but never run.
    """

    BUILTIN_BASELINE = "builtin_baseline"
    BUILTIN_CORE = "builtin_core"
    BUILTIN_SECONDARY = "builtin_secondary"
    USER_ACTIVE = "user_active"
    USER_OTHER = "user_other"

    @property
    def is_reported(self) -> bool:
        """Return whether solvers with this role are benchmarked and appear in reports."""
        return self is not SolverRole.USER_OTHER

    @property
    def is_used_for_characterization(self) -> bool:
        """Return whether results of solvers with this role characterize the test functions."""
        return self is SolverRole.BUILTIN_CORE

    @property
    def is_builtin_only(self) -> bool:
        """Return whether only a config defined inside the sunnbear package may take this role.

        This restriction ensures that only sunnbear's own solvers set the baseline and characterize the
        test functions, so every installation characterizes them identically.
        """
        return self in (SolverRole.BUILTIN_BASELINE, SolverRole.BUILTIN_CORE, SolverRole.BUILTIN_SECONDARY)
