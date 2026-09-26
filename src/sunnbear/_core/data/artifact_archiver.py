"""`ArtifactArchiver` packs the data files of a downloaded artifact into one archive, and unpacks them.

The archive is a tar file compressed with zstd, so an artifact is downloaded and hash-checked as a
single file, whatever the number of its data files and however deep their paths. The archiver works
in memory, on bytes: it never reads or writes the file system, so unpacking a malicious archive
cannot write any file.
"""

import io
import sys
from collections.abc import Collection, Mapping

from .exceptions import ArtifactError

# `tarfile` and `compression.zstd` read and write zstd from Python 3.14; `backports.zstd` provides the
# same API on older versions.
if sys.version_info >= (3, 14):
    import tarfile

    from compression.zstd import CompressionParameter, ZstdError
else:
    from backports.zstd import CompressionParameter, ZstdError, tarfile

_ARCHIVE_SUFFIX = ".tar.zst"
# Packing uses the highest standard zstd level: an archive is packed once, by the maintainer, and
# downloaded by every user, so size matters more than packing time.
_ZSTD_LEVEL = 19
# A fixed mode, like the zeroed times and owners, keeps the packed bytes reproducible.
_FILE_MODE = 0o644


# ==================================================================================================
#  ArtifactArchiver
# ==================================================================================================
class ArtifactArchiver:
    """`ArtifactArchiver` converts between an artifact's data files and the bytes of their zstd-compressed tar file."""

    @staticmethod
    def file_name(artifact_name: str) -> str:
        """Return the file name of the archive of the artifact with this name, e.g. ``uv_tuples.tar.zst``."""
        return f"{artifact_name}{_ARCHIVE_SUFFIX}"

    @staticmethod
    def pack(contents: Mapping[str, bytes]) -> bytes:
        """Return the archive that holds `contents`, a dict that maps each file path to its content.

        For a given zstd version, the same contents always give the same bytes: the files are
        sorted by path, and their modification times and owners are zeroed. Another zstd version
        may give other bytes.
        """
        buffer = io.BytesIO()
        zstd_options: dict[int, int] = {CompressionParameter.compression_level: _ZSTD_LEVEL}
        with tarfile.open(
            name=None, mode="w:zst", fileobj=buffer, format=tarfile.PAX_FORMAT, options=zstd_options
        ) as archive:
            for path in sorted(contents):
                member = tarfile.TarInfo(path)
                member.size = len(contents[path])
                member.mode = _FILE_MODE
                archive.addfile(member, io.BytesIO(contents[path]))
        return buffer.getvalue()

    @staticmethod
    def unpack(archive_bytes: bytes, paths: Collection[str]) -> dict[str, bytes]:
        """Return the content of each file in `paths`, read from the archive.

        Only regular files whose path is in `paths` are read; any other member is ignored, so the
        result never holds a path that the caller did not ask for.

        Raises:
            ArtifactError: If the bytes are not a readable archive, or a path in `paths` is not a
                regular file in the archive.
        """
        contents = {}
        try:
            with tarfile.open(name=None, mode="r:zst", fileobj=io.BytesIO(archive_bytes)) as archive:
                for member in archive:
                    # A link is never read: `extractfile` would follow it to another member.
                    if member.isfile() and member.name in paths:
                        extracted = archive.extractfile(member)
                        # `extractfile` returns `None` only for a member that is not a regular file.
                        if extracted is not None:  # pragma: no branch
                            contents[member.name] = extracted.read()
        except (tarfile.TarError, EOFError, ZstdError) as error:
            raise ArtifactError(f"Cannot read the artifact archive: {error}") from error
        missing_paths = sorted(set(paths) - set(contents))
        if missing_paths:
            raise ArtifactError(f"The artifact archive lacks the files {missing_paths}.")
        return contents
