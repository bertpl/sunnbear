"""Each `SolverRole` carries the treatment that the benchmark reads from its properties."""

import pytest

from sunnbear.solvers import SolverRole

# role: (is_reported, is_used_for_function_characterization, is_builtin_only)
_TREATMENT_BY_ROLE = {
    SolverRole.BUILTIN_BASELINE: (True, False, True),
    SolverRole.BUILTIN_CORE: (True, True, True),
    SolverRole.BUILTIN_SECONDARY: (True, False, True),
    SolverRole.USER_ACTIVE: (True, False, False),
    SolverRole.USER_OTHER: (False, False, False),
}


def test_treatment_table_covers_every_role():
    """`_TREATMENT_BY_ROLE` has an entry for every member of `SolverRole`."""
    # --- act / assert -----------------
    assert set(_TREATMENT_BY_ROLE) == set(SolverRole)


@pytest.mark.parametrize("role, treatment", list(_TREATMENT_BY_ROLE.items()))
def test_role_properties_match_treatment(role, treatment):
    """Each role's ``is_reported``, ``is_used_for_function_characterization`` and ``is_builtin_only`` match its entry
    in `_TREATMENT_BY_ROLE`."""
    # --- act --------------------------
    actual = (role.is_reported, role.is_used_for_function_characterization, role.is_builtin_only)

    # --- assert -----------------------
    assert actual == treatment
