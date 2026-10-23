# Third-party notices

sunnbear is licensed under the Apache License 2.0 (see `LICENSE`). Parts of it derive from the third-party code below, which keeps its own license.

## ModAB-Root-Finding

- **Used in:** the package `src/sunnbear/_core/solvers/bracketing/modab/`. Its classes `ModAB` and `ModABSafeguarded` are ported from this C# code.
- **Source:** https://github.com/Proektsoft-EOOD/ModAB-Root-Finding, at commit `0d6efd59e5dcb34b7bccf90e1d4a9eee6d486e70`:
  - `ModAB` from `MDPI-Algorithms-Data/CSharp code/Numerical/Solvers/ModAB.cs`, the code of Table A1 of Ganchovski et al. (2026), https://doi.org/10.3390/a19050332;
  - `ModABSafeguarded` from `MDPI-Algorithms-Data-2/Root/Solvers/SgModAB.cs`, with the secant `SafeSecant` of `MDPI-Algorithms-Data-2/Root/Node.cs`.
- **License:** MIT, with the same license text in the folders `MDPI-Algorithms-Data` and `MDPI-Algorithms-Data-2`:

```text
MIT License

Copyright (c) 2026 Ned Ganchovski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## xsf

- **Used in:** the module `src/sunnbear/_core/utils/math_functions/bessel.py`. Its Bessel functions `bessel_j0`, `bessel_j1`, `bessel_y0` and `bessel_y1` are ported from this C++ code.
- **Source:** https://github.com/scipy/xsf, at commit `473a8f81df855a1426d5148448babcbcb7696403`: the functions `j0`, `y0`, `j1` and `y1` of `include/xsf/cephes/j0.h` and `include/xsf/cephes/j1.h`, with `polevl` and `p1evl` of `include/xsf/cephes/polevl.h`. SciPy's developers translated these files into C++ from the Cephes Math Library, whose header they keep: "Cephes Math Library Release 2.8: June, 2000. Copyright 1984, 1987, 1989, 2000 by Stephen L. Moshier".
- **License:** BSD 3-Clause:

```text
BSD 3-Clause License

Copyright (c) 2024, SciPy

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
