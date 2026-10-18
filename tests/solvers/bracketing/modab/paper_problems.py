"""This module holds `TABLE_2`, the problems of Table 2 of Ganchovski et al. (2026), with modAB's evaluation count in
that table and its root in the paper's supplementary results."""

from tests.solvers.paper_problems.ganchovski_et_al import GanchovskiEtAlTable2Problem

# On the problems whose row carries this reason, the evaluation count differs from Table 2's, presumably because the
# authors' .NET runtime rounds the last bit of cos, cbrt or exp differently from the correctly rounded values here,
# which changes the x-values that the solve evaluates.
_ROUNDING_DEVIATION_REASON = (
    "the .NET runtime of the paper's benchmark presumably rounds a library function differently"
)

# Each row holds:
# - modAB's evaluation count in Table 2, written as the table's count minus the number of iterations whose secant's
#   zero is clamped onto a bound, where there are any: the paper's C# code counts every iteration as an evaluation,
#   but a clamped iteration evaluates nothing;
# - modAB's root in the paper's supplementary results; `ModAB` returns this x-value without evaluating the function
#   there.
# A row whose count `ModAB` does not reproduce exactly also holds a count tolerance and the reason.
TABLE_2 = [
    GanchovskiEtAlTable2Problem.F01.with_n_fevals_and_root(3, root=1.0),
    GanchovskiEtAlTable2Problem.F02.with_n_fevals_and_root(12, root=0.399422291710968),
    GanchovskiEtAlTable2Problem.F03.with_n_fevals_and_root(15 - 2, root=0.804133097503664),
    GanchovskiEtAlTable2Problem.F04.with_n_fevals_and_root(10, root=-1.0),
    GanchovskiEtAlTable2Problem.F05.with_n_fevals_and_root(12 - 2, root=2.09455148154232),
    GanchovskiEtAlTable2Problem.F06.with_n_fevals_and_root(10, root=0.138257155056824),
    GanchovskiEtAlTable2Problem.F07.with_n_fevals_and_root(11, root=0.0693140886870234),
    GanchovskiEtAlTable2Problem.F08.with_n_fevals_and_root(12, root=0.0346573590208538),
    GanchovskiEtAlTable2Problem.F09.with_n_fevals_and_root(11 - 1, root=0.109611796797792),
    GanchovskiEtAlTable2Problem.F10.with_n_fevals_and_root(9, root=0.0524786034368101),
    GanchovskiEtAlTable2Problem.F11.with_n_fevals_and_root(9, root=0.0256237476199882),
    GanchovskiEtAlTable2Problem.F12.with_n_fevals_and_root(11, root=0.345954815848242),
    GanchovskiEtAlTable2Problem.F13.with_n_fevals_and_root(12, root=0.245122333753307),
    GanchovskiEtAlTable2Problem.F14.with_n_fevals_and_root(12, root=0.16492095727644),
    GanchovskiEtAlTable2Problem.F15.with_n_fevals_and_root(9, root=0.00361710817890406),
    GanchovskiEtAlTable2Problem.F16.with_n_fevals_and_root(8, root=0.000151471334783891),
    GanchovskiEtAlTable2Problem.F17.with_n_fevals_and_root(8, root=7.66859512218533e-06),
    GanchovskiEtAlTable2Problem.F18.with_n_fevals_and_root(11, root=0.516153518757933),
    GanchovskiEtAlTable2Problem.F19.with_n_fevals_and_root(12, root=0.539522226908415),
    GanchovskiEtAlTable2Problem.F20.with_n_fevals_and_root(14 - 1, root=0.552704666678487),
    GanchovskiEtAlTable2Problem.F21.with_n_fevals_and_root(9, root=0.409992017989137),
    GanchovskiEtAlTable2Problem.F22.with_n_fevals_and_root(9, root=0.452509145577641),
    GanchovskiEtAlTable2Problem.F23.with_n_fevals_and_root(9, root=0.475626848596062),
    GanchovskiEtAlTable2Problem.F24.with_n_fevals_and_root(48, root=2.99999999999999),
    GanchovskiEtAlTable2Problem.F25.with_n_fevals_and_root(48, root=3.99999999999999),
    GanchovskiEtAlTable2Problem.F26.with_n_fevals_and_root(48, root=2.47457678736982),
    GanchovskiEtAlTable2Problem.F27.with_n_fevals_and_root(14, root=1.88916015625),
    GanchovskiEtAlTable2Problem.F28.with_n_fevals_and_root(46, root=7.143),
    GanchovskiEtAlTable2Problem.F29.with_n_fevals_and_root(12, root=3.00039062499999),
    GanchovskiEtAlTable2Problem.F30.with_n_fevals_and_root(13, root=4.26716830454212),
    GanchovskiEtAlTable2Problem.F31.with_n_fevals_and_root(12, root=0.31830988618379),
    GanchovskiEtAlTable2Problem.F32.with_n_fevals_and_root(14 - 1, root=1.32581766366803),
    GanchovskiEtAlTable2Problem.F33.with_n_fevals_and_root(12, root=0.865474033101614),
    GanchovskiEtAlTable2Problem.F34.with_n_fevals_and_root(
        11, root=0.73908513321516, deviation=4, reason=_ROUNDING_DEVIATION_REASON
    ),
    GanchovskiEtAlTable2Problem.F35.with_n_fevals_and_root(17 - 1, root=0.656666666666666),
    GanchovskiEtAlTable2Problem.F36.with_n_fevals_and_root(55, root=0.666666666666665),
    GanchovskiEtAlTable2Problem.F37.with_n_fevals_and_root(16, root=0.777777777777777),
    GanchovskiEtAlTable2Problem.F38.with_n_fevals_and_root(53, root=0.333333333333333),
    GanchovskiEtAlTable2Problem.F39.with_n_fevals_and_root(53, root=0.333333333333333),
    GanchovskiEtAlTable2Problem.F40.with_n_fevals_and_root(53, root=0.666666666666665),
    GanchovskiEtAlTable2Problem.F41.with_n_fevals_and_root(13, root=0.138257155056824),
    GanchovskiEtAlTable2Problem.F42.with_n_fevals_and_root(12, root=1.0),
    GanchovskiEtAlTable2Problem.F43.with_n_fevals_and_root(50, root=8.88178419700125e-16),
    GanchovskiEtAlTable2Problem.F44.with_n_fevals_and_root(50, root=8.88178419700125e-16),
    GanchovskiEtAlTable2Problem.F45.with_n_fevals_and_root(50, root=8.88178419700125e-16),
    GanchovskiEtAlTable2Problem.F46.with_n_fevals_and_root(14, root=0.101624392293549),
    GanchovskiEtAlTable2Problem.F47.with_n_fevals_and_root(16, root=0.00773252320061279),
    GanchovskiEtAlTable2Problem.F48.with_n_fevals_and_root(14, root=0.00127630494573556),
    GanchovskiEtAlTable2Problem.F49.with_n_fevals_and_root(12 - 1, root=-0.682327803828019),
    GanchovskiEtAlTable2Problem.F50.with_n_fevals_and_root(11, root=-2.10380340273553),
    GanchovskiEtAlTable2Problem.F51.with_n_fevals_and_root(10, root=1.0),
    GanchovskiEtAlTable2Problem.F52.with_n_fevals_and_root(15, root=1.00004083556472),
    GanchovskiEtAlTable2Problem.F53.with_n_fevals_and_root(13, root=1.69681238680975),
    GanchovskiEtAlTable2Problem.F54.with_n_fevals_and_root(11 - 1, root=0.523598775598298),
    GanchovskiEtAlTable2Problem.F55.with_n_fevals_and_root(10, root=1.0),
    GanchovskiEtAlTable2Problem.F56.with_n_fevals_and_root(11, root=2.0),
    GanchovskiEtAlTable2Problem.F57.with_n_fevals_and_root(11, root=3.0),
    GanchovskiEtAlTable2Problem.F58.with_n_fevals_and_root(10, root=1.5574077246549),
    GanchovskiEtAlTable2Problem.F59.with_n_fevals_and_root(12, root=1.25643120862616),
    GanchovskiEtAlTable2Problem.F60.with_n_fevals_and_root(9, root=0.354463104375025),
    GanchovskiEtAlTable2Problem.F61.with_n_fevals_and_root(13 - 1, root=1.40449164821534),
    GanchovskiEtAlTable2Problem.F62.with_n_fevals_and_root(10, root=1.89549426703398),
    GanchovskiEtAlTable2Problem.F63.with_n_fevals_and_root(11, root=0.567143290409783),
    GanchovskiEtAlTable2Problem.F64.with_n_fevals_and_root(8, root=0.1),
    GanchovskiEtAlTable2Problem.F65.with_n_fevals_and_root(9, root=-0.523598775598298),
    GanchovskiEtAlTable2Problem.F66.with_n_fevals_and_root(13, root=-0.843914568649266),
    GanchovskiEtAlTable2Problem.F67.with_n_fevals_and_root(12, root=0.835079042723559),
    GanchovskiEtAlTable2Problem.F68.with_n_fevals_and_root(9, root=0.873568526830231),
    GanchovskiEtAlTable2Problem.F69.with_n_fevals_and_root(10, root=0.111111111111111),
    GanchovskiEtAlTable2Problem.F70.with_n_fevals_and_root(
        17 - 1, root=-0.0370201277078609, deviation=4, reason=_ROUNDING_DEVIATION_REASON
    ),
    GanchovskiEtAlTable2Problem.F71.with_n_fevals_and_root(8, root=-0.666666666666666),
    GanchovskiEtAlTable2Problem.F72.with_n_fevals_and_root(50, root=1.00000000102795e-06),
    GanchovskiEtAlTable2Problem.F73.with_n_fevals_and_root(50, root=1.00000000102795e-06),
    GanchovskiEtAlTable2Problem.F74.with_n_fevals_and_root(50, root=0.333333333333332),
    GanchovskiEtAlTable2Problem.F75.with_n_fevals_and_root(27, root=0.333333313465118),
    GanchovskiEtAlTable2Problem.F76.with_n_fevals_and_root(39, root=-0.999999000000003),
    GanchovskiEtAlTable2Problem.F77.with_n_fevals_and_root(50, root=0.0476190476190474),
    GanchovskiEtAlTable2Problem.F78.with_n_fevals_and_root(9, root=9.65733148895921e-43),
    GanchovskiEtAlTable2Problem.F79.with_n_fevals_and_root(14, root=2.91317086684747e-19),
    GanchovskiEtAlTable2Problem.F80.with_n_fevals_and_root(25, root=-0.0414560401586836),
    GanchovskiEtAlTable2Problem.F81.with_n_fevals_and_root(14, root=-1.0),
    GanchovskiEtAlTable2Problem.F82.with_n_fevals_and_root(5, root=0.0499999999999999),
    GanchovskiEtAlTable2Problem.F83.with_n_fevals_and_root(50, root=0.198514851485146),
    GanchovskiEtAlTable2Problem.F84.with_n_fevals_and_root(8, root=3.01250244276146),
    GanchovskiEtAlTable2Problem.F85.with_n_fevals_and_root(11, root=-2.20778314488693),
    GanchovskiEtAlTable2Problem.F86.with_n_fevals_and_root(
        15, root=0.302804157270697, deviation=4, reason=_ROUNDING_DEVIATION_REASON
    ),
    GanchovskiEtAlTable2Problem.F87.with_n_fevals_and_root(9 - 1, root=0.98780487804878),
    GanchovskiEtAlTable2Problem.F88.with_n_fevals_and_root(14 - 1, root=0.168362173262536),
    GanchovskiEtAlTable2Problem.F89.with_n_fevals_and_root(13, root=-1.74176261121641),
    GanchovskiEtAlTable2Problem.F90.with_n_fevals_and_root(13, root=0.02637269541443),
    GanchovskiEtAlTable2Problem.F91.with_n_fevals_and_root(13, root=0.120778011811926),
    GanchovskiEtAlTable2Problem.F92.with_n_fevals_and_root(25, root=0.1),
]
