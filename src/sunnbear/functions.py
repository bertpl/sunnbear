"""This module re-exports what inspecting a test function needs: `TestFunction`, its id, and the types of its functions.

- `TestFunction` holds a formula with its parameter values, its interval and its c-range;
- `FunctionId` identifies a test function by its formula's id and its parameter values;
- `XFun` and `XCFun` are the types of what `TestFunction.build_x_fun` and `TestFunction.xc_fun` return.

How test functions are built from formulas is described in the docstring of the implementation package,
`sunnbear._core.functions.core`.
"""

from ._core.functions import FunctionId, TestFunction, XCFun, XFun

__all__ = ["FunctionId", "TestFunction", "XCFun", "XFun"]
