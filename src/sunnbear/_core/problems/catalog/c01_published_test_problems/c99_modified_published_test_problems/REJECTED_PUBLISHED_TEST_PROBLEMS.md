# Published test problems that the benchmark suite pipeline rejects

The validation stage of the benchmark suite pipeline, `sunnbear._core.benchmark.suites.pipeline`, rejects every test problem that does not satisfy the benchmark suite inclusion conditions. This file lists each published test problem that the validation stage rejects, from the formulas of category 1 outside subcategory 1.99, with the decision taken for it:

- **all parameter tuples modified:** formula 1.99.x.y.z modifies every parameter tuple of formula 1.x.y.z;
- **some parameter tuples modified:** formula 1.99.x.y.z holds only some parameter tuples of formula 1.x.y.z, the ones that need the modification;
- **no action:** the published test problem keeps its rejection, for the reason in its table row.

`ModifiedPublishedTestProblems` states the rules of subcategory 1.99, and the docstring of each formula of subcategory 1.99 describes the formula's modification in full. The table names the modification in short, and marks the modifications that change what the test problem tests.

The column "Rejection reason" holds the validation stage's `RejectionReason`; the enum `RejectionReason` describes each value.

Which test problems the validation stage rejects depends on:

- the formulas;
- the stage's checks;
- the shipped Monte Carlo tuple set, which supplies the values of each formula's parameter `c` for the check that bisection spends a fixed number of evaluations.

After a change of any of them, running the pipeline, as `python -m sunnbear._core.benchmark.suites.pipeline --workspace <dir>`, shows whether this file needs an update.

| Published test problem | Rejection reason | Decision | Modified test problem | Modification, or reason for no action | Changes what the test problem tests |
|---|---|---|---|---|---|
| `f1.1.2.4` | `calibration_c_range_too_narrow` | all parameter tuples modified | `f1.99.1.2.4` | `c` added to f |  |
| `f1.1.4.3` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.4.3` | a tiny linear term added to f | yes |
| `f1.1.4.4` | `calibration_c_range_too_narrow` | no action | | f is exactly 0, by underflow, on most of the interval; the test problem tests that flat 0 | |
| `f1.1.5.3[a=0.0,b=1.5,c_scale=1.5]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.1.5.3` | interval changed to `[0.02, 1.5]` |  |
| `f1.1.6.3[n=33.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.6.3[n=33.0]` | f in an equivalent form without cancellation |  |
| `f1.1.7.2[a=0.0001,b=10^4.0,c_scale=10^4.0]` | `calibration_c_range_too_narrow` | some parameter tuples modified | `f1.99.1.7.2[a=0.0001,b=10^4.0]` | `c` scales x |  |
| `f1.1.7.2[a=1e-06,b=10^6.0,c_scale=10^6.0]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.1.7.2[a=1e-06,b=10^6.0]` | `c` scales x |  |
| `f1.1.7.2[a=1e-10,b=10^10.0,c_scale=10^10.0]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.1.7.2[a=1e-10,b=10^10.0]` | `c` scales x |  |
| `f1.1.7.2[a=1e-12,b=10^12.0,c_scale=10^12.0]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.1.7.2[a=1e-12,b=10^12.0]` | `c` scales x |  |
| `f1.1.7.7[a=-1.0,b=4.0,c_scale=5.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.7.7[a=-1.0,b=4.0,c_scale=5.0]` | a tiny linear term added to f | yes |
| `f1.1.7.7[a=-2.0,b=5.0,c_scale=7.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.7.7[a=-2.0,b=5.0,c_scale=7.0]` | a tiny linear term added to f | yes |
| `f1.1.7.7[a=-1.0,b=10.0,c_scale=11.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.7.7[a=-1.0,b=10.0,c_scale=11.0]` | a tiny linear term added to f | yes |
| `f1.1.7.7[a=-5.0,b=50.0,c_scale=55.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.7.7[a=-5.0,b=50.0,c_scale=55.0]` | a tiny linear term added to f | yes |
| `f1.1.7.7[a=-10.0,b=100.0,c_scale=110.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.7.7[a=-10.0,b=100.0,c_scale=110.0]` | a tiny linear term added to f | yes |
| `f1.1.7.8[xi=0.61489,a=0.0002,b=2.0,c_scale=2.0]` | `calibration_c_range_too_narrow` | all parameter tuples modified | `f1.99.1.7.8[xi=0.61489,a=0.0002,b=2.0]` | `c` scales x |  |
| `f1.1.7.8[xi=0.61489,a=0.0002,b=3.0,c_scale=3.0]` | `calibration_c_range_too_narrow` | all parameter tuples modified | `f1.99.1.7.8[xi=0.61489,a=0.0002,b=3.0]` | `c` scales x |  |
| `f1.1.7.8[xi=0.61489,a=0.0002,b=9.0,c_scale=9.0]` | `calibration_c_range_too_narrow` | all parameter tuples modified | `f1.99.1.7.8[xi=0.61489,a=0.0002,b=9.0]` | `c` scales x |  |
| `f1.1.7.8[xi=0.61489,a=0.0002,b=27.0,c_scale=27.0]` | `calibration_c_range_too_narrow` | all parameter tuples modified | `f1.99.1.7.8[xi=0.61489,a=0.0002,b=27.0]` | `c` scales x |  |
| `f1.1.7.8[xi=0.61489,a=0.0002,b=81.0,c_scale=81.0]` | `calibration_c_range_too_narrow` | all parameter tuples modified | `f1.99.1.7.8[xi=0.61489,a=0.0002,b=81.0]` | `c` scales x |  |
| `f1.1.7.9[a=0.0002,b=9.0,c_scale=9.0]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.1.7.9[a=0.0002,b=9.0]` | `c` scales x |  |
| `f1.1.7.9[a=0.0002,b=27.0,c_scale=27.0]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.1.7.9[a=0.0002,b=27.0]` | `c` scales x |  |
| `f1.1.7.9[a=0.0002,b=81.0,c_scale=81.0]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.1.7.9[a=0.0002,b=81.0]` | `c` scales x |  |
| `f1.1.8.1[a=0.004,b=200.0,c_scale=200.0]` | `calibration_c_range_too_narrow` | some parameter tuples modified | `f1.99.1.8.1` | `c` scales x |  |
| `f1.1.9.11` | `bisection_count_not_exact` | no action | | bisection lands on an exact 0 at the root for some values of `c` of the shipped Monte Carlo tuple set; f is exactly 0 at only a few floats there, not in a band that a form without cancellation could remove | |
| `f1.1.9.15` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.9.15` | f in an equivalent form without cancellation |  |
| `f1.1.12.1[a=-2.5,b=3.0,c_scale=5.5]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.1.12.1` | interval changed to `[-2.5, 3.06]` |  |
| `f1.1.12.2` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.1.12.2` | interval changed to `[0.02, 2]` |  |
| `f1.1.12.4` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.12.4` | f in an equivalent form without cancellation |  |
| `f1.1.13.4` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.13.4` | f in an equivalent form without cancellation |  |
| `f1.1.13.5[a=2.6,b=4.6,c_scale=2.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.13.5[a=2.6,b=4.6,c_scale=2.0]` | f in an equivalent form without cancellation |  |
| `f1.1.13.5[a=2.6,b=3.6,c_scale=1.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.13.5[a=2.6,b=3.6,c_scale=1.0]` | f in an equivalent form without cancellation |  |
| `f1.1.13.19` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.13.19` | f in an equivalent form without cancellation |  |
| `f1.1.13.21` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.1.13.21` | interval changed to `[-1.02, 1]` |  |
| `f1.1.14.5[a=-1.0,b=4.0,c_scale=5.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.14.5[a=-1.0,b=4.0,c_scale=5.0]` | a tiny linear term added to f | yes |
| `f1.1.14.5[a=-2.0,b=5.0,c_scale=7.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.14.5[a=-2.0,b=5.0,c_scale=7.0]` | a tiny linear term added to f | yes |
| `f1.1.14.5[a=-1.0,b=10.0,c_scale=11.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.14.5[a=-1.0,b=10.0,c_scale=11.0]` | a tiny linear term added to f | yes |
| `f1.1.14.5[a=-5.0,b=50.0,c_scale=55.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.14.5[a=-5.0,b=50.0,c_scale=55.0]` | a tiny linear term added to f | yes |
| `f1.1.14.5[a=-10.0,b=100.0,c_scale=110.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.1.14.5[a=-10.0,b=100.0,c_scale=110.0]` | a tiny linear term added to f | yes |
| `f1.1.15.2` | `calibration_no_finite_sign_change_at_0` | no action | | f is exactly 0 at `a`, and the interval holds no other root | |
| `f1.2.1.5[n=25.0]` | `bisection_count_not_exact` | some parameter tuples modified | `f1.99.2.1.5[n=25.0]` | a tiny linear term added to f |  |
| `f1.2.1.6` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.2.1.6` | a tiny linear term added to f | yes |
| `f1.2.4.2[a=1.000000001,b=3.999999999,c_scale=3.0]` | `calibration_c_range_too_narrow` | all parameter tuples modified | `f1.99.2.4.2[a=1.03,b=3.97,c_scale=2.94]` | interval changed to `[1.03, 3.97]` | yes |
| `f1.2.4.2[a=4.000000001,b=8.999999999,c_scale=5.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=4.05,b=8.95,c_scale=4.9]` | interval changed to `[4.05, 8.95]` | yes |
| `f1.2.4.2[a=9.000000001,b=15.999999999,c_scale=7.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=9.07,b=15.93,c_scale=6.86]` | interval changed to `[9.07, 15.93]` | yes |
| `f1.2.4.2[a=16.000000001,b=24.999999999,c_scale=9.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=16.09,b=24.91,c_scale=8.82]` | interval changed to `[16.09, 24.91]` | yes |
| `f1.2.4.2[a=25.000000001,b=35.999999999,c_scale=11.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=25.1,b=35.9,c_scale=10.8]` | interval changed to `[25.1, 35.9]` | yes |
| `f1.2.4.2[a=36.000000001,b=48.999999999,c_scale=13.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=36.1,b=48.9,c_scale=12.8]` | interval changed to `[36.1, 48.9]` | yes |
| `f1.2.4.2[a=49.000000001,b=63.999999999,c_scale=15.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=49.2,b=63.8,c_scale=14.6]` | interval changed to `[49.2, 63.8]` | yes |
| `f1.2.4.2[a=64.000000001,b=80.999999999,c_scale=17.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=64.2,b=80.8,c_scale=16.6]` | interval changed to `[64.2, 80.8]` | yes |
| `f1.2.4.2[a=81.000000001,b=99.999999999,c_scale=19.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=81.2,b=99.8,c_scale=18.6]` | interval changed to `[81.2, 99.8]` | yes |
| `f1.2.4.2[a=100.000000001,b=120.999999999,c_scale=21.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=100.2,b=120.8,c_scale=20.6]` | interval changed to `[100.2, 120.8]` | yes |
| `f1.2.4.2[a=121.000000001,b=143.999999999,c_scale=23.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=121.2,b=143.8,c_scale=22.6]` | interval changed to `[121.2, 143.8]` | yes |
| `f1.2.4.2[a=144.000000001,b=168.999999999,c_scale=25.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=144.3,b=168.7,c_scale=24.4]` | interval changed to `[144.3, 168.7]` | yes |
| `f1.2.4.2[a=169.000000001,b=195.999999999,c_scale=27.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=169.3,b=195.7,c_scale=26.4]` | interval changed to `[169.3, 195.7]` | yes |
| `f1.2.4.2[a=196.000000001,b=224.999999999,c_scale=29.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=196.3,b=224.7,c_scale=28.4]` | interval changed to `[196.3, 224.7]` | yes |
| `f1.2.4.2[a=225.000000001,b=255.999999999,c_scale=31.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=225.3,b=255.7,c_scale=30.4]` | interval changed to `[225.3, 255.7]` | yes |
| `f1.2.4.2[a=256.000000001,b=288.999999999,c_scale=33.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=256.3,b=288.7,c_scale=32.4]` | interval changed to `[256.3, 288.7]` | yes |
| `f1.2.4.2[a=289.000000001,b=323.999999999,c_scale=35.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=289.4,b=323.6,c_scale=34.2]` | interval changed to `[289.4, 323.6]` | yes |
| `f1.2.4.2[a=324.000000001,b=360.999999999,c_scale=37.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=324.4,b=360.6,c_scale=36.2]` | interval changed to `[324.4, 360.6]` | yes |
| `f1.2.4.2[a=361.000000001,b=399.999999999,c_scale=39.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.4.2[a=361.4,b=399.6,c_scale=38.2]` | interval changed to `[361.4, 399.6]` | yes |
| `f1.2.9.4` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.2.9.4` | f in an equivalent form without cancellation |  |
| `f1.2.9.6` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.2.9.6` | f in an equivalent form without cancellation |  |
| `f1.2.11.7` | `bisection_count_not_exact` | no action | | bisection lands on an exact 0 at the root for some values of `c` of the shipped Monte Carlo tuple set; f is exactly 0 at only a few floats there, not in a band that a form without cancellation could remove | |
| `f1.2.13.8` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.2.13.8` | interval changed to `[-6, -0.9]` |  |
| `f1.2.13.9` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.2.13.9` | interval changed to `[-1, 2]` |  |
| `f1.2.13.11` | `calibration_no_finite_sign_change_at_0` | no action | | f has no real root | |
| `f1.2.15.1[y=0.1]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.1]` | `c` added to f |  |
| `f1.2.15.1[y=0.2]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.2]` | `c` added to f |  |
| `f1.2.15.1[y=0.3]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.3]` | `c` added to f |  |
| `f1.2.15.1[y=0.4]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.4]` | `c` added to f |  |
| `f1.2.15.1[y=0.5]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.5]` | `c` added to f |  |
| `f1.2.15.1[y=0.6]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.6]` | `c` added to f |  |
| `f1.2.15.1[y=0.7]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.7]` | `c` added to f |  |
| `f1.2.15.1[y=0.8]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.8]` | `c` added to f |  |
| `f1.2.15.1[y=0.9]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.1[y=0.9]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.1]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.1]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.2]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.2]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.3]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.3]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.4]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.4]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.5]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.5]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.6]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.6]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.7]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.7]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.8]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.8]` | `c` added to f |  |
| `f1.2.15.2[q=2^127.0,y=0.9]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.2.15.2[q=2^127.0,y=0.9]` | `c` added to f |  |
| `f1.2.18.5[k=1.2,a=0.0,b=2.0,c_scale=2.0]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.2.18.5[k=1.2]` | interval changed to `[0.02, 2]` |  |
| `f1.2.18.6` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.2.18.6` | interval changed to `[0, 1.98]` |  |
| `f1.2.18.14[a=19.0,b=21.0,c_scale=2.0]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.2.18.14` | interval changed to `[19.02, 21]` |  |
| `f1.2.18.20` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.2.18.20` | interval changed to `[-3, 0.96]` |  |
| `f1.2.18.23` | `calibration_no_finite_sign_change_at_0` | no action | | the root has even multiplicity, so f does not change sign | |
| `f1.3.1.4[a=1e-05,b=20.0,c_scale=20.0]` | `calibration_c_range_too_narrow` | some parameter tuples modified | `f1.99.3.1.4` | `c` scales x |  |
| `f1.3.1.6[a=1e-05,b=20.0,c_scale=20.0]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.3.1.6` | interval changed to `[0.08, 20]` |  |
| `f1.3.1.12[factor=1000.0,a=-4.0,b=4.1,c_scale=8.1]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.3.1.12[factor=1000.0,a=-4.0,b=4.1,c_scale=8.1]` | a tiny linear term added to f | yes |
| `f1.3.1.12[factor=1000.0,a=0.5,b=2.0,c_scale=1.5]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.3.1.12[factor=1000.0,a=0.5,b=2.0,c_scale=1.5]` | a tiny linear term added to f | yes |
| `f1.3.1.17[a=0.988,b=1.012,c_scale=0.024]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.3.1.17[a=0.988,b=1.012,c_scale=0.024]` | f in an equivalent form without cancellation | yes |
| `f1.3.1.17[a=0.99,b=1.013,c_scale=0.023]` | `calibration_fails_at_benchmark_c_values` | all parameter tuples modified | `f1.99.3.1.17[a=0.99,b=1.013,c_scale=0.023]` | f in an equivalent form without cancellation; the modified test problem is rejected by `bisection_count_not_exact` | yes |
| `f1.3.2.3` | `calibration_c_range_too_narrow` | all parameter tuples modified | `f1.99.3.2.3` | `c` added to f | yes |
| `f1.3.2.5` | `bound_to_width_ratio` | all parameter tuples modified | `f1.99.3.2.5` | x shifted so that the interval becomes `[-0.0005, 0.0002]`; f in an equivalent form without cancellation |  |
| `f1.3.3.4[a=-1.0,b=4.0,c_scale=5.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.3.3.4[a=-1.0,b=4.0,c_scale=5.0]` | a tiny linear term added to f | yes |
| `f1.3.3.4[a=-1.1234,b=4.4567,c_scale=5.58]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.3.3.4[a=-1.1234,b=4.4567,c_scale=5.58]` | a tiny linear term added to f | yes |
| `f1.3.3.30[a=0.0,b=2.0,c_scale=2.0]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.3.3.30` | `c` added to f |  |
| `f1.3.3.33[a=0.0,b=6.0,c_scale=6.0]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.3.3.33` | `c` added to f |  |
| `f1.3.3.41` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.3.3.41` | f in an equivalent form without cancellation |  |
| `f1.3.4.2` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.3.4.2` | interval changed to `[0.03, 2.718281828459045]` |  |
| `f1.3.5.12[a=1.0,b=3.4,c_scale=2.4]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.3.5.12[a=1.0,b=3.4,c_scale=2.4]` | f in an equivalent form without cancellation | yes |
| `f1.3.5.12[a=1.0,b=2.5,c_scale=1.5]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.3.5.12[a=1.0,b=2.5,c_scale=1.5]` | f in an equivalent form without cancellation | yes |
| `f1.3.5.13` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.3.5.13` | interval changed to `[-2.04, 1.96]` | yes |
| `f1.3.6.2[a=5.0,b=12.0,c_scale=7.0]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.3.6.2` | interval changed to `[5, 7.7]` | yes |
| `f1.3.6.3` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.3.6.3` | interval changed to `[-0.2, 1]` | yes |
| `f1.3.6.4` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.3.6.4` | interval changed to `[-2, 1]` | yes |
| `f1.3.8.3` | `bisection_count_not_exact` | no action | | bisection lands on an exact 0 at the root for some values of `c` of the shipped Monte Carlo tuple set; f is exactly 0 at only a few floats there, not in a band that a form without cancellation could remove | |
| `f1.3.8.6` | `calibration_fails_at_first_probe` | no action | | rounding noise: the first value of `c` that the validation stage tries, a shift along x, takes `f(a)` from about -0.95 to about -0.008 | |
| `f1.4.1.2[a=0.0,b=2.0,c_scale=2.0]` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.1.2[a=-1.0,b=1.0,c_scale=2.0]` | x shifted so that the interval becomes `[-1, 1]`; f in an equivalent form without cancellation |  |
| `f1.4.1.2[a=0.998,b=1.002,c_scale=0.004]` | `bound_to_width_ratio` | all parameter tuples modified | `f1.99.4.1.2[a=-0.002,b=0.002,c_scale=0.004]` | x shifted so that the interval becomes `[-0.002, 0.002]`; f in an equivalent form without cancellation | yes |
| `f1.4.1.6` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.1.6` | f in an equivalent form without cancellation |  |
| `f1.4.1.7` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.1.7` | a tiny linear term added to f | yes |
| `f1.4.1.8` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.1.8` | interval changed to `[-3, 4]` |  |
| `f1.4.2.1[M=200.0,a=0.8,b=1.8,c_scale=1.0]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.1[M=200.0,a=-0.01,b=0.0,c_scale=0.01]` | x shifted so that the interval becomes `[-0.01, 0]` | yes |
| `f1.4.2.1[M=2000.0,a=0.8,b=1.8,c_scale=1.0]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.1[M=2000.0,a=-0.001,b=0.0,c_scale=0.001]` | x shifted so that the interval becomes `[-0.001, 0]` | yes |
| `f1.4.2.1[M=20000.0,a=0.8,b=1.8,c_scale=1.0]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.1[M=20000.0,a=-0.0001,b=0.0,c_scale=0.0001]` | x shifted so that the interval becomes `[-0.0001, 0]` | yes |
| `f1.4.2.1[M=200000.0,a=0.8,b=1.8,c_scale=1.0]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.1[M=200000.0,a=-1e-05,b=0.0,c_scale=1e-05]` | x shifted so that the interval becomes `[-1e-05, 0]` | yes |
| `f1.4.2.1[M=2000000.0,a=0.8,b=1.8,c_scale=1.0]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.1[M=2000000.0,a=-1e-06,b=0.0,c_scale=1e-06]` | x shifted so that the interval becomes `[-1e-06, 0]` | yes |
| `f1.4.2.1[M=20000000.0,a=0.8,b=1.8,c_scale=1.0]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.1[M=20000000.0,a=-1e-07,b=0.0,c_scale=1e-07]` | x shifted so that the interval becomes `[-1e-07, 0]` | yes |
| `f1.4.2.1[M=2000000.0,a=1.04999,b=1.05001,c_scale=2e-05]` | `bound_to_width_ratio` | all parameter tuples modified | `f1.99.4.2.1[M=2000000.0,a=-1e-05,b=0.0,c_scale=1e-05]` | x shifted so that the interval becomes `[-1e-05, 0]` | yes |
| `f1.4.2.1[M=20000000.0,a=1.04999,b=1.05001,c_scale=2e-05]` | `bound_to_width_ratio` | all parameter tuples modified | `f1.99.4.2.1[M=20000000.0,a=-1e-05,b=0.0,c_scale=1e-05]` | x shifted so that the interval becomes `[-1e-05, 0]` | yes |
| `f1.4.2.3[alpha=0.5]` | `calibration_no_finite_sign_change_at_0` | no action | | f is exactly 0 at `a`, and the interval holds no other root | |
| `f1.4.2.3[alpha=1.0]` | `calibration_no_finite_sign_change_at_0` | no action | | f is exactly 0 at `a`, and the interval holds no other root | |
| `f1.4.2.3[alpha=2.0]` | `calibration_no_finite_sign_change_at_0` | no action | | f is exactly 0 at `a`, and the interval holds no other root | |
| `f1.4.2.4[a=-2.0,b=-1.0,c_scale=1.0]` | `bisection_count_not_exact` | no action | | bisection lands on an exact 0 at the root for some values of `c` of the shipped Monte Carlo tuple set; f is exactly 0 at only a few floats there, not in a band that a form without cancellation could remove | |
| `f1.4.2.5[a_=3.4]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.5[a_=3.4,a=0.01,b=1.0,c_scale=0.99]` | interval changed to `[0.01, 1]` |  |
| `f1.4.2.5[a_=3.5]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.5[a_=3.5,a=0.01,b=1.0,c_scale=0.99]` | interval changed to `[0.01, 1]` |  |
| `f1.4.2.5[a_=3.99]` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.2.5[a_=3.99,a=0.01,b=1.0,c_scale=0.99]` | interval changed to `[0.01, 1]` |  |
| `f1.4.2.6` | `calibration_no_finite_sign_change_at_0` | no action | | f is exactly 0 at `a`, and the interval holds no other root | |
| `f1.4.3.1` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.3.1` | interval changed to `[0.04, 4]` |  |
| `f1.4.3.2` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.3.2` | f in an equivalent form without cancellation | yes |
| `f1.4.3.5[a=0.0,b=31.4159265359,c_scale=31.4]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.4.3.5` | interval changed to `[0, 30]` |  |
| `f1.4.3.6` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.3.6` | interval changed to `[-1, 1]` |  |
| `f1.4.3.14` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.3.14` | f in an equivalent form without cancellation |  |
| `f1.4.3.15` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.3.15` | interval changed to `[2, 31.41592653589793]` | yes |
| `f1.4.4.2[a=2.14159265359,b=3.14159265359,c_scale=1.0]` | `calibration_no_finite_sign_change_at_0` | no action | | the roots lie too close to `pi` for float64: f has the same sign at both bounds | |
| `f1.4.4.2[a=3.14159265359,b=4.14159265359,c_scale=1.0]` | `calibration_no_finite_sign_change_at_0` | no action | | the roots lie too close to `pi` for float64: f has the same sign at both bounds | |
| `f1.4.4.6[a=0.0,b=0.5,c_scale=0.5]` | `calibration_fails_at_first_probe` | some parameter tuples modified | `f1.99.4.4.6` | interval changed to `[0, 0.495]` |  |
| `f1.4.4.7[initial_investment=14000.0,monthly_deposit=250.0,goal=25000.0]` | `bisection_count_not_exact` | some parameter tuples modified | `f1.99.4.4.7[initial_investment=14000.0,monthly_deposit=250.0,goal=25000.0]` | f in an equivalent form without cancellation |  |
| `f1.4.4.24[a=1.0,b=2.0,c_scale=1.0]` | `bisection_count_not_exact` | no action | | bisection lands on an exact 0 at the root for some values of `c` of the shipped Monte Carlo tuple set; f is exactly 0 at only a few floats there, not in a band that a form without cancellation could remove | |
| `f1.4.4.28` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.4.28` | f in an equivalent form without cancellation |  |
| `f1.4.5.8` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.5.8` | interval changed to `[0.03, 3.141592653589793]` |  |
| `f1.4.5.10` | `calibration_no_finite_sign_change_at_0` | no action | | f has no real root | |
| `f1.4.5.14` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.5.14` | interval changed to `[0.08, 8]` |  |
| `f1.4.5.15[a=-0.2,b=0.2,c_scale=0.4]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.4.5.15` | interval changed to `[0.01, 0.2]` |  |
| `f1.4.5.20` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.5.20` | interval changed to `[1.3, 2]` |  |
| `f1.4.5.21` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.5.21` | interval changed to `[-2, 1]` |  |
| `f1.4.5.22` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.5.22` | f in an equivalent form without cancellation | yes |
| `f1.4.5.23` | `bound_to_width_ratio` | all parameter tuples modified | `f1.99.4.5.23` | x shifted so that the interval becomes `[-0.002, 0.002]`; f in an equivalent form without cancellation |  |
| `f1.4.6.1[g=9.81,m=82.0,v=36.0,t=4.0,a=3.0,b=5.0,c_scale=2.0]` | `bisection_count_not_exact` | some parameter tuples modified | `f1.99.4.6.1[g=9.81,m=82.0,v=36.0,t=4.0]` | f in an equivalent form without cancellation |  |
| `f1.4.6.2[a=3.0,b=5.0,c_scale=2.0]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.4.6.2[a=3.3,b=5.0,c_scale=1.7]` | interval changed to `[3.3, 5]` |  |
| `f1.4.6.2[a=4.2,b=4.3,c_scale=0.1]` | `calibration_no_finite_sign_change_at_0` | some parameter tuples modified | `f1.99.4.6.2[a=4.2,b=4.26,c_scale=0.06]` | interval changed to `[4.2, 4.26]` | yes |
| `f1.4.6.16` | `bisection_count_not_exact` | no action | | bisection lands on an exact 0 at the root for some values of `c` of the shipped Monte Carlo tuple set; f is exactly 0 at only a few floats there, not in a band that a form without cancellation could remove | |
| `f1.4.6.18` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.6.18` | f in an equivalent form without cancellation |  |
| `f1.4.6.20[g=9.81,L=4.0,t=2.5,v=5.0]` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.4.6.20[g=9.81,L=4.0,t=2.5,v=5.0]` | `c` added to f |  |
| `f1.4.7.4` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.7.4` | interval changed to `[-3, 1]` |  |
| `f1.4.7.8` | `calibration_no_finite_sign_change_at_0` | no action | | the root has even multiplicity, so f does not change sign | |
| `f1.4.7.9` | `calibration_fails_at_first_probe` | all parameter tuples modified | `f1.99.4.7.9` | `c` added to f |  |
| `f1.4.7.11[a=3.2,b=4.0,c_scale=0.8]` | `bisection_count_not_exact` | some parameter tuples modified | `f1.99.4.7.11` | f in an equivalent form without cancellation |  |
| `f1.4.7.19` | `calibration_no_finite_sign_change_at_0` | all parameter tuples modified | `f1.99.4.7.19` | interval changed to `[4, 4.6]` |  |
| `f1.4.7.41` | `calibration_no_finite_sign_change_at_0` | no action | | the root has even multiplicity, so f does not change sign | |
| `f1.4.7.42` | `calibration_no_finite_sign_change_at_0` | no action | | the root has even multiplicity, so f does not change sign | |
| `f1.4.7.43` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.7.43` | f in an equivalent form without cancellation |  |
| `f1.4.7.45` | `calibration_no_finite_sign_change_at_0` | no action | | the root has even multiplicity, so f does not change sign | |
| `f1.4.7.46` | `calibration_no_finite_sign_change_at_0` | no action | | the root has even multiplicity, so f does not change sign | |
| `f1.4.7.47` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.7.47` | f in an equivalent form without cancellation |  |
| `f1.4.7.48` | `bisection_count_not_exact` | all parameter tuples modified | `f1.99.4.7.48` | f in an equivalent form without cancellation |  |
