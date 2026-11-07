"""`BenchmarkSuitesBuildDetailsDeclaration` declares the data artifact `benchmark_suites_build_details`.

The artifact holds the build details of a benchmark suite pipeline run over the shipped test problems, as the files of
`BenchmarkSuitesBuildDetails.to_files`. The files are downloaded from a data release, and the artifact's manifest ships
in the package.

The release script stops when `BenchmarkSuitesBuildDetails.staleness_reasons` reports that the
artifact no longer fits the shipped test problems; a maintainer then rebuilds it with
``scripts/generate_benchmark_suites_build_details.py``.
"""

from collections.abc import Mapping

from sunnbear._core.artifacts import ArtifactDeclaration, ArtifactError, ArtifactSource

from .state import BenchmarkSuitesBuildDetails


# ==================================================================================================
#  BenchmarkSuitesBuildDetailsDeclaration
# ==================================================================================================
class BenchmarkSuitesBuildDetailsDeclaration(ArtifactDeclaration[BenchmarkSuitesBuildDetails]):
    """`BenchmarkSuitesBuildDetailsDeclaration` declares the `benchmark_suites_build_details` artifact."""

    name = "benchmark_suites_build_details"
    source = ArtifactSource.DOWNLOAD

    @classmethod
    def to_files(cls, value: BenchmarkSuitesBuildDetails) -> dict[str, bytes]:
        """Return the files of `BenchmarkSuitesBuildDetails.to_files`."""
        return value.to_files()

    @classmethod
    def from_files(cls, files: Mapping[str, bytes]) -> BenchmarkSuitesBuildDetails:
        """Rebuild the build details from their files.

        Raises:
            ArtifactError: If this sunnbear cannot read the files, because a file or a field that
                `BenchmarkSuitesBuildDetails.to_files` writes is missing, they record other core solver configs than
                `DiversityFeatureFactory.solver_ids`, or they hold a stage id or another value that this sunnbear does
                not define.
        """
        try:
            return BenchmarkSuitesBuildDetails.from_files(files)
        except (KeyError, ValueError) as error:
            raise ArtifactError(f"This sunnbear cannot read the benchmark suites build details: {error}") from error
