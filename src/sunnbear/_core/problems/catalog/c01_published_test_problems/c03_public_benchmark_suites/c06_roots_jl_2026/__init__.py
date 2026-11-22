"""This category holds the formulas of Roots.jl (2026)."""

from sunnbear._core.problems.core import FormulaCategory, Publication

from . import f01_func2, f02_func9, f03_func10, f04_func11, f05_f2, f06_f4, f07_f5, f08_f8, f09_f9


class RootsJl2026(FormulaCategory):
    """`RootsJl2026` is the category of the formulas of 1 publication."""

    number = (1, 3, 6)
    name = "Roots.jl (2026)"
    description = "The test problems come from the tests of Roots.jl, a Julia package of root finders, version 3.0.11."
    publication = Publication(
        citation=(
            "Roots.jl v3.0.11, the test folder https://github.com/JuliaMath/Roots.jl/tree/v3.0.11/test, MIT"
            " license. The functions of the rows are in 2 files:\n- `test/test_derivative_free.jl`,"
            " https://github.com/JuliaMath/Roots.jl/blob/v3.0.11/test/test_derivative_free.jl\n-"
            " `test/runbenchmarks.jl`,"
            " https://github.com/JuliaMath/Roots.jl/blob/v3.0.11/test/runbenchmarks.jl\n\nThe files cite 1 source:"
            " the comment `## multiplicity:"
            " http://ir.igsnrr.ac.cn/bitstream/311030/8840/1/%E4%BE%AF%E9%BA%9F%E7%A7%91(SCI)2.pdf` stands above"
            " `func13` in `test_derivative_free.jl`. The URL gives no title; its file name decodes to"
            " `侯麟科(SCI)2.pdf`.\n\nThe paper at the URL is Li et al. (2010): Li, X., Mu, C., Ma, J., Hou, L. (2011)."
            " Fifth-order iterative method for finding multiple roots of nonlinear equations. Numerical"
            " Algorithms 57(3), 389–398, published online in 2010. https://doi.org/10.1007/s11075-010-9434-5. Its"
            " rows are in `2010_li_multiple_roots`."
        ),
        citation_key="RootsJl26",
        year=2026,
        title="Roots.jl",
        url="https://github.com/JuliaMath/Roots.jl/tree/v3.0.11/test",
    )
