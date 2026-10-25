"""This module re-exports `TestFunction`, its id `FunctionId`, and the callable types `XFun` and `XCFun`.

- `TestFunction` holds a formula with its parameter values, its interval and the range of its parameter `c`;
- `FunctionId` identifies a test function by its formula number and its named parameter values;
- `XFun` is the type that `TestFunction.build_x_fun` returns, `f(x)` at a fixed `c`; `XCFun` is the type of
  `TestFunction.xc_fun`, `f(x, c)`.

How test functions are built from formulas is described in the docstring of the implementation package,
`sunnbear._core.functions.core`.
"""

from ._core.functions import FunctionId, TestFunction, XCFun, XFun

__all__ = ["FunctionId", "TestFunction", "XCFun", "XFun"]
