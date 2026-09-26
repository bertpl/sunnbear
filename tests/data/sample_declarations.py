"""This module holds the test-only artifact declarations:

- `SampleLinesDeclaration` has committed data files;
- `SampleDownloadedLinesDeclaration` has only a committed manifest, and its data files are
  downloaded;
- `define_declaration` defines a 1-file declaration on the fly, and `define_builtin_declaration` one
  that counts as built in.
"""

from collections.abc import Mapping

from sunnbear._core.data import ArtifactDeclaration, ArtifactSource

# The tests convert these lines with `SampleLinesDeclaration`.
SAMPLE_LINES = ["alpha", "beta", "gamma"]


class SampleLinesDeclaration(ArtifactDeclaration[list[str]]):
    """`SampleLinesDeclaration` declares text lines, with their count in a subfolder file so tests cover such paths."""

    name = "sample_lines"

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


class SampleDownloadedLinesDeclaration(SampleLinesDeclaration):
    """`SampleDownloadedLinesDeclaration` declares the same files as `SampleLinesDeclaration`, but downloaded.

    Its committed manifest lists URLs under ``example.invalid``, a domain that never resolves, so a
    test must replace `ArtifactStore._download`.
    """

    name = "sample_downloaded_lines"
    source = ArtifactSource.DOWNLOAD


def define_declaration(file_path: str = "value.txt", **attrs) -> type[ArtifactDeclaration]:
    """Define a concrete `ArtifactDeclaration` subclass with the given class attributes.

    Its value is the bytes of the file at `file_path`.
    """
    namespace = {
        "to_files": classmethod(lambda cls, value: {file_path: value}),
        "from_files": classmethod(lambda cls, files: files[file_path]),
        **attrs,
    }
    return type("_DefinedDeclaration", (ArtifactDeclaration,), namespace)


def define_builtin_declaration(name: str, file_path: str = "value.txt") -> type[ArtifactDeclaration]:
    """Define a 1-file declaration whose module name is inside sunnbear, so that it counts as built in.

    Defining the class registers it in `ArtifactRegistry`, so a test that calls this function must use
    the `isolated_artifact_registry` fixture.
    """
    return define_declaration(file_path, __module__="sunnbear._declared_in_a_test", name=name)
