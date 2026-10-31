"""`SuiteFamily` names a family of the suites distilled from the Core."""

from enum import StrEnum


# ==================================================================================================
#  SuiteFamily
# ==================================================================================================
class SuiteFamily(StrEnum):
    """A `SuiteFamily` names a family of suites; no 2 families share a candidate.

    A solver may be tuned on calibration suites and then measured on benchmark suites, so that no test problem of the
    measurement took part in the tuning.
    """

    BENCHMARK = "benchmark"
    CALIBRATION = "calibration"
