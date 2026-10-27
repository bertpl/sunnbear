"""This category holds the modified versions of the formulas of Roots.jl (2026)."""

from sunnbear._core.problems.core import FormulaCategory

from . import f02_func9, f03_func10, f04_func11


class ModifiedRootsJl2026(FormulaCategory):
    """`ModifiedRootsJl2026` holds the modified versions of the formulas of 1 publication.

    Roots.jl v3.0.11, the test folder https://github.com/JuliaMath/Roots.jl/tree/v3.0.11/test, MIT license. The
    functions of the rows are in 2 files: - `test/test_derivative_free.jl`,
    https://github.com/JuliaMath/Roots.jl/blob/v3.0.11/test/test_derivative_free.jl - `test/runbenchmarks.jl`,
    https://github.com/JuliaMath/Roots.jl/blob/v3.0.11/test/runbenchmarks.jl

    The files cite 1 source: the comment `## multiplicity:
    http://ir.igsnrr.ac.cn/bitstream/311030/8840/1/%E4%BE%AF%E9%BA%9F%E7%A7%91(SCI)2.pdf` stands above `func13` in
    `test_derivative_free.jl`. The URL gives no title; its file name decodes to `侯麟科(SCI)2.pdf`.

    The paper at the URL is Li et al. (2010): Li, X., Mu, C., Ma, J., Hou, L. (2011). Fifth-order iterative method for
    finding multiple roots of nonlinear equations. Numerical Algorithms 57(3), 389–398, published online in 2010.
    https://doi.org/10.1007/s11075-010-9434-5. Its rows are in `2010_li_multiple_roots`.
    """

    number = (1, 99, 3, 6)
    name = "Roots.jl (2026)"
