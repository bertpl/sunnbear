# Parameter names of the catalog's formulas

This guide gives the same name to the same kind of parameter across the catalog's formulas. It is indicative, not binding: a formula takes another name where that name reads better, and its docstring then says what the parameter is.

A parameter's name is part of a test problem's id, as in `f2.1.2[p=4.0,w=10^0.3]`. Renaming a parameter therefore changes the ids of its formula's test problems.

## Reserved names

- **`x` and `c`** are arguments of every formula: the point of evaluation, and the parameter that a benchmark varies per sample.
- **`a`, `b` and `c_scale`** are parameters of the formulas of category 1: the bounds of a formula's interval and the scale of its shift along x. The class docstring of `PublishedTestProblems` states their rules.
- **A reserved name or a Python keyword gets a trailing underscore**, as in `a_` and `lambda_`.

## Which names a formula uses

The first rule that applies gives the names:

1. **A published formula keeps the parameter names of its source.** The formulas of category 1 follow this rule.
2. **A named function keeps the parameter names of its reference**, written in ASCII, such as `mu` and `sigma` for a normal distribution, or `nu` for degrees of freedom.
3. **Any other parameter takes its name from the table below.**

| name | meaning | example |
|---|---|---|
| `n` | a count: the terms of a sum, the pieces of a function, the degree of a named polynomial | `x^2 + x^4 + ... + x^(2*n)` |
| `p` | a power, integer or not | `x^p` |
| `s` | a scale of x: a steepness or a frequency | `tanh(s*x)`, `sin(s*x)` |
| `w` | a weight: the coefficient of a term | `x + w*(x^p - 1)` |
| `m` | a slope | `m*x + (1 - m)*x^p` |
| `d` | a distance: how far a pole, a kink or the edge of the domain lies from a reference point | `sqrt(x + 1 + d)` |
| `x0` | the location of a feature on the x-axis | a step at `x0` |
| `eps` | the size of a small perturbation | `x + eps*sin(x/eps)` |

## Further rules

- **A second parameter of the same kind gets a number:** `s1` and `s2`, `w1` and `w2`.
- **Where no name of the table fits, use a short word** that says what the parameter is, such as `steepness`. A numbered placeholder such as `p1` for "the first parameter" says nothing.
- **A coefficient is `w`, never `c1` or `c2`.** Beside `c` and `c_scale`, such a name reads as a value of `c`.
- **A power is `p`, never `e`.** In a formula's text, `e` reads as Euler's number.
- **Counts and powers come first in `param_names`**, then the other parameters, so that an id starts with the parameter that changes the formula's structure.
