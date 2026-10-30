"""`FullCharacterizationStage` adds the full feature vectors."""

from sunnbear._core.benchmark.suites.pipeline.features import CandidateCharacterizationStage, FeatureFidelity


# ==================================================================================================
#  FullCharacterizationStage
# ==================================================================================================
class FullCharacterizationStage(CandidateCharacterizationStage):
    """`FullCharacterizationStage` adds a feature vector to each candidate that spacing keeps.

    The benchmark suites are selected by the full feature vectors, so by default the stage runs at the full fidelity,
    whose tuple sets and snuffled analysis budget are larger than the coarse fidelity's.

    Its feature scales are computed only on the candidates that the spacing stage keeps, because the benchmark suites
    are selected from those candidates.

    The full fidelity can reject a candidate that the coarse one kept, for example a candidate whose f fails only at an
    x that the coarse fidelity's solves never evaluate, but the solves on the full fidelity's larger tuple set do.
    Spacing does not run again, so the candidates that spacing dropped near such a candidate stay dropped.
    """

    output_name = "s5_full_features"
    column_prefix = "full"
    default_fidelity = FeatureFidelity.FULL
