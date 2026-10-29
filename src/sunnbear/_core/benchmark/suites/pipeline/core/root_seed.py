"""`PIPELINE_ROOT_SEED` is the root seed of every random draw of the benchmark suite pipeline."""

# Each random draw of the pipeline, such as a snuffled analysis, derives its seed from this root seed with
# `derive_seed`, so that its results are the same in every run of the pipeline.
PIPELINE_ROOT_SEED = 0
