"""This package tests `Ellithy`.

The article's runs stop by the stopping criterion of its pseudocode, ``|f(x)| <= 1e-14`` at the x-values that each
algorithm tests, not by the criterion of its section 5.2, ``|b - a| < 1e-14`` and ``|f(x)| < 1e-14``: the published
iteration counts reproduce only with the pseudocode's criterion. So ``test_paper.py`` reproduces its tables with a
test-only subclass of `Ellithy` that stops by that criterion and counts the iterations.

The article publishes iteration counts only; an iteration evaluates the function a varying number of times, so the
iteration counts do not convert to evaluation counts.

Published results:

- Ellithy (2026), Table 12, the columns "Opt.BF", "Opt.BFMS", "Opt.TF" and "Opt.TFMS": reproduced, in
  ``test_paper.py``: all 192 iteration counts exactly.

  Of these, 163 reproduce with the article's adaptive ``delta``, the ``delta = 1e-8*max(1, |x_FP|) + 1e-15`` of its
  equation 2. The other 29, in the columns of Opt.BFMS and Opt.TFMS, reproduce only with a fixed ``delta = 1e-4``, and
  the adaptive ``delta`` takes 1 iteration fewer on each:

  - Opt.BFMS: f4, f5, f7, f10, f16, f18, f19, f34, f37, f43 and f47;
  - Opt.TFMS: f2, f4, f5, f9, f10, f12, f13, f20, f22, f26, f29, f32, f35, f37, f43, f44, f46 and f48.

  The authors' code gives the step ``delta`` a default of 1e-4, which its loop replaces by the adaptive ``delta``.
  The article's other tables reproduce with the adaptive ``delta``, and 3 of them disagree with Table 12 on these
  problems: Table 2 on f19 for Opt.BFMS, and Tables 3 and 5 on f44 and f48 for Opt.TFMS.

  Table 12 counts a root at an interval bound as 1 iteration, as the article's pseudocode does; the test counts it the
  same way.
- Ellithy (2026), Tables 2 to 5: reproduced, in ``test_paper.py``, with the adaptive ``delta``: the 16 iteration counts
  of the 4 methods on f19, f44, f30 and f48.
- Ellithy (2026), Table 7: reproduced, in ``test_paper.py``, with the adaptive ``delta``: the mean, minimum, maximum,
  median and standard deviation of each method's 48 iteration counts. The standard deviation is the sample standard
  deviation over the article's 480000 runs, which repeat each problem 10000 times.
- Ellithy (2026), the results of the article's other methods in Tables 2 to 12: not compared, because `Ellithy` does
  not implement those methods.
- Ellithy (2026), Tables 6 and 11: not compared, because they give CPU times.
- Ellithy (2026), Tables 8 to 10 and 13 to 15: not compared, because they give either summaries of the other tables or
  estimates of evaluations and flops derived from the average iteration counts of Table 7.

Third-party published results:

- None.

Reference implementations:

- hybridroots 1.0.1, the authors' package of the 4 methods: compared in ``test_twin.py``, for every variant.
- The authors' experiment scripts, which produced the article's tables: not run. They follow Algorithms 1 to 4 line by
  line, as hybridroots does, and ``test_paper.py`` reproduces their published results.
"""
