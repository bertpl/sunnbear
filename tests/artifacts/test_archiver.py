"""`ArtifactArchiver` packs data files into a tar file reproducibly, and unpacks only the requested files."""

import io

import pytest

from sunnbear._core.artifacts import ArtifactArchiver, ArtifactError
from sunnbear._core.artifacts.archiver import tarfile

_CONTENTS = {"lines.txt": b"alpha\nbeta\n", "meta/count.txt": b"2\n"}


def _pack_members(members: list[tuple[tarfile.TarInfo, bytes]]) -> bytes:
    """Return a zstd-compressed tar file that holds `members`, each a header and its content."""
    buffer = io.BytesIO()
    with tarfile.open(name=None, mode="w:zst", fileobj=buffer) as archive:
        for member, content in members:
            archive.addfile(member, io.BytesIO(content))
    return buffer.getvalue()


def _regular_file(name: str, content: bytes) -> tuple[tarfile.TarInfo, bytes]:
    """Return the header of a regular file member, and its content."""
    member = tarfile.TarInfo(name)
    member.size = len(content)
    return member, content


# ==================================================================================================
#  Packing
# ==================================================================================================
def test_unpack_returns_what_pack_packed():
    """Unpacking a packed archive gives back every file, including one in a subfolder."""
    assert ArtifactArchiver.unpack(ArtifactArchiver.pack(_CONTENTS), _CONTENTS.keys()) == _CONTENTS


def test_pack_gives_the_same_bytes_for_the_same_contents():
    """Packing sorts the files and zeroes their times and owners, so repeated packing gives equal bytes."""
    # --- act --------------------------
    first_bytes = ArtifactArchiver.pack(_CONTENTS)
    second_bytes = ArtifactArchiver.pack(dict(reversed(_CONTENTS.items())))

    # --- assert -----------------------
    assert first_bytes == second_bytes
    with tarfile.open(name=None, mode="r:zst", fileobj=io.BytesIO(first_bytes)) as archive:
        members = archive.getmembers()
    assert [member.name for member in members] == sorted(_CONTENTS)
    assert {(member.mtime, member.uid, member.gid, member.uname, member.gname, member.mode) for member in members} == {
        (0, 0, 0, "", "", 0o644)
    }


def test_archive_file_name_is_the_artifact_name_with_the_archive_suffix():
    """The archive of ``uv_tuples`` is named ``uv_tuples.tar.zst``."""
    assert ArtifactArchiver.archive_file_name("uv_tuples") == "uv_tuples.tar.zst"


# ==================================================================================================
#  Unpacking
# ==================================================================================================
def test_unpack_ignores_members_that_are_not_asked_for():
    """A member outside the requested paths, such as one whose path starts with ``..``, is never returned."""
    # --- arrange ----------------------
    archive_bytes = _pack_members([_regular_file("lines.txt", b"alpha\n"), _regular_file("../escape.txt", b"x")])

    # --- act / assert -----------------
    assert ArtifactArchiver.unpack(archive_bytes, ["lines.txt"]) == {"lines.txt": b"alpha\n"}


def test_unpack_refuses_a_link_in_place_of_a_requested_file():
    """A symbolic link named like a requested file is not followed, so the file counts as missing."""
    # --- arrange ----------------------
    link = tarfile.TarInfo("lines.txt")
    link.type = tarfile.SYMTYPE
    link.linkname = "/etc/passwd"
    archive_bytes = _pack_members([(link, b"")])

    # --- act / assert -----------------
    with pytest.raises(ArtifactError, match=r"lacks the files \['lines\.txt'\]"):
        ArtifactArchiver.unpack(archive_bytes, ["lines.txt"])


@pytest.mark.parametrize(
    "archive_bytes",
    [
        b"not an archive",
        ArtifactArchiver.pack({"big.txt": bytes(range(256)) * 400})[:-5],
    ],
)
def test_unpack_refuses_bytes_that_are_not_a_complete_archive(archive_bytes):
    """Bytes that are not a zstd-compressed tar file, or a truncated one, raise `ArtifactError`."""
    with pytest.raises(ArtifactError, match="Cannot read the artifact archive"):
        ArtifactArchiver.unpack(archive_bytes, ["big.txt"])
