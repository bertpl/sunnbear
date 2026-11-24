"""This category holds the formulas of roots-fortran (2025)."""

from pathlib import Path

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import (
    f01_case_13,
    f02_case_14,
    f03_case_21,
    f04_case_26,
    f05_case_37,
    f06_case_38,
    f07_case_39,
    f08_case_40,
    f09_case_41,
    f10_case_42,
    f11_case_43,
    f12_case_44,
    f13_case_45,
    f14_case_46,
    f15_case_63,
    f16_case_64,
    f17_case_65,
    f18_case_66,
    f19_case_67,
    f20_case_68,
    f21_case_69,
    f22_case_70,
    f23_case_71,
    f24_case_73,
    f25_case_74,
    f26_case_75,
    f27_case_79,
    f28_case_83,
    f29_case_84,
    f30_case_86,
    f31_case_89,
    f32_case_91,
    f33_case_93,
    f34_case_95,
    f35_case_99,
    f36_case_118,
    f37_case_133,
    f38_case_138,
    f39_case_146,
    f40_case_149,
    f41_case_150,
    f42_case_152,
    f43_case_154,
    f44_case_155,
)


class RootsFortran2025(FormulaCategory):
    """`RootsFortran2025` is the category of the formulas of 1 publication."""

    number = (1, 3, 3)
    name = "roots-fortran (2025)"
    description = "The test problems come from the test program of roots-fortran, a Fortran library of root finders."
    publication = Publication.from_csl_json_file(Path(__file__).parent / "publication.csl.json")
