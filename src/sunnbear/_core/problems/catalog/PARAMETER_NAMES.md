# Parameter names of the catalog's formulas

This guide gives the same name to the same kind of parameter across the catalog's formulas. It is indicative, not binding: a formula takes another name where that name reads better, and its docstring then says what the parameter is.

A parameter's name is part of a test problem's id, as in `f2.1.2[p=4.0,w=10^0.3]`. Renaming a parameter therefore changes the ids of its formula's test problems.

## Reserved names

- **`x` and `c`** are arguments of every formula: the point of evaluation, and the parameter that a benchmark varies per sample.
- **`f`** names the function itself, as in the display `f(x, c) = …` of every formula's presentation.
- **`a`, `b` and `c_scale`** are parameters of the formulas of category 1: the bounds of a formula's interval and the scale of its shift along x. The class docstring of `PublishedTestProblems` states their rules.
- **`a` and `b` also name the bounds of the interval when a formula outside category 1 takes its interval as a parameter**, as in `BernoulliPolynomial`. The class docstring of such a formula states which values `a` and `b` may take.
- **A reserved name or a Python keyword gets a trailing underscore**, as in `c_` and `lambda_`.
- **The symbols $a$ and $b$ name only the bounds of an interval**, in every category; a catalog test checks that every parameter with these symbols is a bound. So a source's parameter that the source calls `a` or `b` takes another name and symbol, not `a_` or `b_`, such as `q` for the constant of `x^n - a`: the one exception to rule 1 of the next section.

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
- **A parameter's LaTeX symbol is 1 letter, Latin or Greek, with an optional subscript,** even where its name is a word: a word as a symbol reads as a product of letters in a formula's display.
- **A parameter whose symbol does not say what the parameter is gets a `meaning`** in its `FormulaParam`, as the parameter `slope` with the symbol `m` does.
- **A coefficient is `w`, never `c1` or `c2`.** Beside `c` and `c_scale`, such a name reads as a value of `c`.
- **A power is `p`, never `e`.** In a formula's text, `e` reads as Euler's number.
- **Counts and powers come first in `params`**, then the other parameters, so that an id starts with the parameter that changes the formula's structure.
