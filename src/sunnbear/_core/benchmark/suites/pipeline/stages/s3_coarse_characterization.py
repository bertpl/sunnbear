"""`CoarseCharacterizationStage`, the third stage of the benchmark suite pipeline, adds the coarse feature vectors."""

from sunnbear._core.benchmark.suites.pipeline.features import CandidateCharacterizationStage, FeatureFidelity


# ==================================================================================================
#  CoarseCharacterizationStage
# ==================================================================================================
class CoarseCharacterizationStage(CandidateCharacterizationStage):
    """`CoarseCharacterizationStage` adds each valid candidate's feature vector at `FeatureFidelity.COARSE`.

    The coarse vectors only need to tell the near-duplicate candidates of a formula apart, so the stage runs on every
    valid candidate at the coarse fidelity's small tuple sets and budget.
    """

    output_name = "s3_coarse_features"
    column_prefix = "coarse"
    fidelity = FeatureFidelity.COARSE
