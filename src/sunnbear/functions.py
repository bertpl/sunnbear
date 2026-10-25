"""This module re-exports `TestFunction`, its id `FunctionId`, and the types of the callables that it returns.

- `TestFunction` holds a formula with its parameter values, its interval and the range of its parameter `c`;
- `FunctionId` identifies a test function by its formula number and its named parameter values;
- `XFun` and `XCFun` are the types of what `TestFunction.build_x_fun` and `TestFunction.xc_fun` return.

How test functions are built from formulas is described in the docstring of the implementation package,
`sunnbear._core.functions.core`.
"""

from ._core.functions import FunctionId, TestFunction, XCFun, XFun

__all__ = ["FunctionId", "TestFunction", "XCFun", "XFun"]
