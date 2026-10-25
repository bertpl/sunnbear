"""This module re-exports `TestProblem`, its id `ProblemId`, and the callable types `XFun` and `XCFun`.

- `TestProblem` holds a formula with its parameter values, its interval and the range of its parameter `c`;
- `ProblemId` identifies a test problem by its formula number and its named parameter values;
- `XFun` is the type that `TestProblem.build_x_fun` returns, `f(x)` at a fixed `c`; `XCFun` is the type of
  `TestProblem.xc_fun`, `f(x, c)`.

How test problems are built from formulas is described in the docstring of the implementation package,
`sunnbear._core.functions.core`.
"""

from ._core.functions import ProblemId, TestProblem, XCFun, XFun

__all__ = ["ProblemId", "TestProblem", "XCFun", "XFun"]
