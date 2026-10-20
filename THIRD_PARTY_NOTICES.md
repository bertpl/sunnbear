# Third-party notices

sunnbear is licensed under the Apache License 2.0 (see `LICENSE`). Parts of it derive from the third-party code below, which keeps its own license.

## ModAB-Root-Finding

- **Used in:** `src/sunnbear/_core/solvers/bracketing/modab/solver.py`. Both variants of `ModAB` are ported from this C# code.
- **Source:** https://github.com/Proektsoft-EOOD/ModAB-Root-Finding, at commit `0d6efd59e5dcb34b7bccf90e1d4a9eee6d486e70`:
  - `"algorithms_2026"` from `MDPI-Algorithms-Data/CSharp code/Numerical/Solvers/ModAB.cs`, the code of Table A1 of Ganchovski et al. (2026), https://doi.org/10.3390/a19050332;
  - `"safeguarded_2026"` from `MDPI-Algorithms-Data-2/Root/Solvers/SgModAB.cs`, with the secant `SafeSecant` of `MDPI-Algorithms-Data-2/Root/Node.cs`.
- **License:** MIT, the same text in both folders:

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
