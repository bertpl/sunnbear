"""Each `SolverRole` carries the treatment that the benchmark reads from its properties."""

import pytest

from sunnbear.solvers import SolverRole

# role: (is_reported, contributes_to_characterization, is_sealed)
_TREATMENT_BY_ROLE = {
    SolverRole.BUILTIN_BASELINE: (True, False, True),
    SolverRole.BUILTIN_CORE: (True, True, True),
    SolverRole.BUILTIN_SECONDARY: (True, False, True),
    SolverRole.USER_ACTIVE: (True, False, False),
    SolverRole.USER_OTHER: (False, False, False),
}


def test_treatment_table_covers_every_role():
    assert set(_TREATMENT_BY_ROLE) == set(SolverRole)


@pytest.mark.parametrize("role, treatment", list(_TREATMENT_BY_ROLE.items()))
def test_role_properties_match_treatment(role, treatment):
    # --- act --------------------------
    actual = (role.is_reported, role.contributes_to_characterization, role.is_sealed)

    # --- assert -----------------------
    assert actual == treatment
