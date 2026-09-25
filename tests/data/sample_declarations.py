"""`SampleLinesDeclaration` is a test-only artifact declaration."""

from collections.abc import Mapping

from sunnbear._core.data import ArtifactDeclaration

# The tests convert these lines with `SampleLinesDeclaration`.
SAMPLE_LINES = ["alpha", "beta", "gamma"]


class SampleLinesDeclaration(ArtifactDeclaration[list[str]]):
    """`SampleLinesDeclaration` declares text lines, with their count in a subfolder file so tests cover such paths."""

    name = "sample_lines"
    data_schema_version = 1

    @classmethod
    def to_files(cls, value: list[str]) -> dict[str, bytes]:
        """Write the lines to ``lines.txt`` and their count to ``meta/count.txt``."""
        return {
            "lines.txt": "".join(f"{line}\n" for line in value).encode(),
            "meta/count.txt": f"{len(value)}\n".encode(),
        }

    @classmethod
    def from_files(cls, files: Mapping[str, bytes]) -> list[str]:
        """Read the lines back from ``lines.txt``."""
        return files["lines.txt"].decode().splitlines()
