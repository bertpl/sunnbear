"""`ArtifactStore` is the only code that reads or writes a data artifact's files and manifest.

An artifact's ``manifest.json`` lives in the artifact's folder, which the store derives from where
the artifact's declaration is defined, so no caller passes a location:

- a built-in artifact, whose declaration is inside the sunnbear package, uses
  ``_core/data/artifacts/<name>/``, which ships with sunnbear;
- any other declaration, in practice a test fixture, uses ``artifacts/<name>/`` next to its own
  module, so its files never ship.

Where the data files live depends on the declaration's `ArtifactSource`:

- **package**: next to the manifest. Loading does not check their hashes: the files ship inside the
  package, and the test suite runs `ArtifactStore.verify_builtin_artifacts` on every change.
- **download**: in the cache folder ``<cache root>/<artifact name>/<content hash>``, where the cache
  root is ``SUNNBEAR_CACHE_DIR`` when that environment variable is set, else the user's cache folder
  for sunnbear. The data files are downloaded as one archive, which `ArtifactArchiver` packs and
  unpacks and the manifest's ``archive`` entry describes. When the cache lacks a data file, or
  holds a copy whose hash differs from the file's manifest entry, loading:

  - downloads the archive and checks its hash;
  - unpacks the archive into the cache folder;
  - checks every unpacked file against its manifest entry.
"""

import datetime
import http.client
import importlib.metadata
import os
import sys
import urllib.request
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any, TypeVar, assert_never

import platformdirs

from sunnbear._core.utils.class_origin import is_defined_in_sunnbear

from .artifact_archiver import ArtifactArchiver
from .artifact_data_release_client import ArtifactDataReleaseClient
from .artifact_declaration import ArtifactDeclaration
from .artifact_manifest import ArtifactArchiveEntry, ArtifactFileEntry, ArtifactManifest
from .artifact_registry import ArtifactRegistry
from .artifact_source import ArtifactSource
from .exceptions import ArtifactError

T = TypeVar("T")

_MANIFEST_FILE_NAME = "manifest.json"
_ARTIFACTS_FOLDER_NAME = "artifacts"
_BUILTIN_ARTIFACTS_PARENT_PACKAGE = "sunnbear._core.data"
_CACHE_DIR_ENV_VAR = "SUNNBEAR_CACHE_DIR"
_DOWNLOAD_TIMEOUT_SEC = 60
# `ArtifactStore._download` raises these exceptions for a failed download.
_DOWNLOAD_ERRORS = (OSError, ValueError, http.client.HTTPException)


# ==================================================================================================
#  ArtifactStore
# ==================================================================================================
class ArtifactStore:
    """`ArtifactStore` loads, saves and verifies data artifacts, given their declarations."""

    # --------------------------------------------------------------------------
    #  Loading
    # --------------------------------------------------------------------------
    @classmethod
    def load(cls, declaration_cls: type[ArtifactDeclaration[T]]) -> T:
        """Read the artifact's data files and rebuild its value with `from_files`.

        Files shipped in the package are read without checking their hashes. The files of a
        downloaded artifact are read from the cache when every cached copy matches its manifest
        entry; otherwise the artifact's archive is unpacked into the cache first.

        The archive is read from the cache folder when it is there and matches the manifest's
        ``archive`` entry, e.g. because a user without network access placed it there, and
        downloaded otherwise. The archive is deleted from the cache folder once its files are
        unpacked.

        Raises:
            ArtifactError: If any of these holds:

                - the manifest is missing, malformed or names another artifact;
                - a file shipped in the package is missing;
                - the archive is needed and one of these holds:

                    - the manifest has no ``archive`` entry;
                    - the download fails, or the archive does not match that entry; the message
                      names the path where the archive can be placed by hand;
                    - the archive cannot be unpacked, or the unpacked files do not match the
                      manifest.
        """
        manifest = cls.load_manifest(declaration_cls)
        match declaration_cls.source:
            case ArtifactSource.PACKAGE:
                folder = cls._folder_of(declaration_cls)
                contents = {entry.path: cls._read_file(folder, entry.path, declaration_cls) for entry in manifest.files}
            case ArtifactSource.DOWNLOAD:
                contents = cls._read_or_unpack_downloaded_files(manifest)
            case _:
                assert_never(declaration_cls.source)
        return declaration_cls.from_files(contents)

    @classmethod
    def load_manifest(cls, declaration_cls: type[ArtifactDeclaration]) -> ArtifactManifest:
        """Read the artifact's manifest and check that it names the declared artifact.

        Raises:
            ArtifactError: If the manifest is missing or malformed, or names another artifact.
        """
        manifest_bytes = cls._read_file(cls._folder_of(declaration_cls), _MANIFEST_FILE_NAME, declaration_cls)
        manifest = ArtifactManifest.from_json(manifest_bytes.decode())
        if manifest.name != declaration_cls.name:
            raise ArtifactError(
                f"The manifest of {declaration_cls.__name__} is for {manifest.name!r}, "
                f"but the declaration is for {declaration_cls.name!r}."
            )
        return manifest

    # --------------------------------------------------------------------------
    #  Saving
    # --------------------------------------------------------------------------
    @classmethod
    def save(
        cls,
        declaration_cls: type[ArtifactDeclaration[T]],
        value: T,
        *,
        built_with: dict[str, str] | None = None,
        input_artifact_hashes: dict[str, str] | None = None,
        generated_by: dict[str, Any] | None = None,
    ) -> ArtifactManifest:
        """Write the artifact's data files for `value` and a new manifest, replacing what the artifact's folder held.

        Where the data files go depends on the declaration's `ArtifactSource`:

        - **package**: next to the manifest;
        - **download**: into the cache folder; the manifest records no ``archive`` entry, because
          `save` does not upload an archive, so no URL exists for it yet.

        Any other file in the artifact's folder is deleted, so the folder holds exactly the manifest
        and, for an artifact shipped in the package, the files that the manifest lists.

        Args:
            declaration_cls: The artifact's declaration.
            value: The value to write.
            built_with: The versions of the libraries that affect the content, keyed by package
                name; sunnbear's own version is always recorded, replacing any ``sunnbear`` entry.
            input_artifact_hashes: The content hashes of `value`'s input artifacts, keyed by
                artifact name.
            generated_by: The public function call that generated `value`, as JSON-compatible data.

        Returns:
            The manifest that was written.

        Raises:
            ArtifactError: If the declaration produces a file named like the manifest, or the
                artifact's folder is not a writable directory, e.g. inside a zipped install.
            ValueError: If the declaration produces no file, or a path that is absolute or contains
                a ``..`` part.
        """
        contents = declaration_cls.to_files(value)
        if _MANIFEST_FILE_NAME in contents:
            raise ArtifactError(f"{declaration_cls.__name__} produces a data file named {_MANIFEST_FILE_NAME!r}.")
        # Sorting by path keeps the content hash independent of the order in which `to_files` returns the files.
        manifest = ArtifactManifest(
            name=declaration_cls.name,
            files=tuple(ArtifactFileEntry.from_content(path, contents[path]) for path in sorted(contents)),
            input_artifact_hashes=input_artifact_hashes or {},
            built_with=(built_with or {}) | {"sunnbear": importlib.metadata.version("sunnbear")},
            build_date=datetime.date.today(),
            generated_by=generated_by,
        )
        folder = cls._folder_on_disk_of(declaration_cls)
        match declaration_cls.source:
            case ArtifactSource.PACKAGE:
                data_folder, data_paths_next_to_manifest = folder, set(contents)
            case ArtifactSource.DOWNLOAD:
                data_folder, data_paths_next_to_manifest = cls._cache_folder_of(manifest), set()
            case _:
                assert_never(declaration_cls.source)
        folder.mkdir(parents=True, exist_ok=True)
        # A file left over from an earlier save, and not written by this one, would contradict the new manifest.
        for leftover_path in cls._relative_data_file_paths(folder) - data_paths_next_to_manifest:
            (folder / leftover_path).unlink()
        cls._write_files(data_folder, contents)
        cls._write_manifest(declaration_cls, manifest)
        return manifest

    # --------------------------------------------------------------------------
    #  Verification
    # --------------------------------------------------------------------------
    @classmethod
    def verify(cls, declaration_cls: type[ArtifactDeclaration]) -> ArtifactManifest:
        """Check the artifact's folder against its manifest.

        The download cache of a downloaded artifact is not checked.

        Returns:
            The artifact's manifest.

        Raises:
            ArtifactError: If any of these holds:

                - the manifest is missing, malformed or names another artifact;
                - for an artifact shipped in the package, a file is missing, differs from its
                  manifest entry, or is not listed;
                - for an artifact shipped in the package, the manifest has an ``archive`` entry;
                - for a downloaded artifact, a data file lies next to the manifest, or the manifest
                  has no ``archive`` entry.
        """
        manifest = cls.load_manifest(declaration_cls)
        folder = cls._folder_of(declaration_cls)
        present_paths = cls._relative_data_file_paths(folder)
        match declaration_cls.source:
            case ArtifactSource.PACKAGE:
                problems = cls._compare_shipped_files_with_manifest(folder, present_paths, manifest)
                if manifest.archive is not None:
                    problems.append("the manifest has an archive entry, but the artifact ships in the package")
            case ArtifactSource.DOWNLOAD:
                problems = [
                    f"{path} is next to the manifest, but the artifact's data files are downloaded"
                    for path in sorted(present_paths)
                ]
                if manifest.archive is None:
                    problems.append("the manifest has no archive entry")
            case _:
                assert_never(declaration_cls.source)
        if problems:
            raise ArtifactError(f"Artifact {manifest.short_identity} fails verification: {'; '.join(problems)}.")
        return manifest

    @classmethod
    def verify_builtin_artifacts(cls) -> None:
        """Verify every built-in artifact, and check that each subfolder of the built-in artifacts folder is declared.

        `ArtifactRegistry` knows only the declarations whose modules have been imported, so import
        the sunnbear modules that declare artifacts first; the store cannot import them itself,
        because `sunnbear._core.data` must not import the sunnbear modules that depend on it.

        Raises:
            ArtifactError: If a built-in artifact fails `verify` or a subfolder of the built-in
                artifacts folder has no declaration; the message lists each one.
        """
        builtin_declarations = [
            declaration_cls
            for declaration_cls in ArtifactRegistry.declarations()
            if is_defined_in_sunnbear(declaration_cls)
        ]
        problems = []
        for declaration_cls in builtin_declarations:
            try:
                cls.verify(declaration_cls)
            except ArtifactError as error:
                problems.append(str(error))
        builtin_artifacts_folder = cls._builtin_artifacts_folder()
        folder_names = (
            {child.name for child in builtin_artifacts_folder.iterdir() if child.is_dir()}
            if builtin_artifacts_folder.is_dir()
            else set()
        )
        declared_names = {declaration_cls.name for declaration_cls in builtin_declarations}
        problems += [f"Folder {name!r} holds no declared artifact" for name in sorted(folder_names - declared_names)]
        if problems:
            raise ArtifactError("Built-in artifacts are inconsistent:\n- " + "\n- ".join(problems))

    @staticmethod
    def _compare_shipped_files_with_manifest(
        folder: Traversable, present_paths: set[str], manifest: ArtifactManifest
    ) -> list[str]:
        """Return a problem message for each data file that is missing, differs from its entry, or is unlisted."""
        listed_paths = {entry.path for entry in manifest.files}
        problems = [f"{path} is not listed in the manifest" for path in sorted(present_paths - listed_paths)]
        for entry in manifest.files:
            if entry.path not in present_paths:
                problems.append(f"{entry.path} is missing")
            elif not entry.matches(folder.joinpath(entry.path).read_bytes()):
                problems.append(f"{entry.path} differs from its manifest entry")
        return problems

    # --------------------------------------------------------------------------
    #  Publishing
    # --------------------------------------------------------------------------
    @classmethod
    def publish(cls, declaration_cls: type[ArtifactDeclaration]) -> ArtifactManifest:
        """Publish a downloaded artifact's archive as a data release, and record the archive in the manifest.

        Publishing, called right after `save`, is internal, maintainer-only functionality. A data
        release is a GitHub release that holds only this archive (see `ArtifactDataReleaseClient`).
        Publishing:

        - packs the data files from the cache;
        - creates the data release;
        - downloads the archive back from the release;
        - checks the unpacked files against the manifest, and only then records the archive.

        An artifact whose data release already exists is not published again: that release's
        archive is checked and recorded.

        Returns:
            The manifest that was written.

        Raises:
            ArtifactError: If any of these holds:

                - the artifact ships in the package, or its manifest is missing or malformed;
                - the GitHub CLI is missing, has no write access to the repository, or fails;
                - the data release does not exist and the cache lacks the data files, e.g. because
                  the artifact was not saved first;
                - the data release is a draft, e.g. left behind when publishing was interrupted;
                - the archive cannot be downloaded back from the release, or does not match the
                  manifest.
        """
        if declaration_cls.source is not ArtifactSource.DOWNLOAD:
            raise ArtifactError(f"{declaration_cls.__name__} ships in the package, so it has no data release.")
        manifest = cls.load_manifest(declaration_cls)
        ArtifactDataReleaseClient.check_write_access()
        tag = ArtifactDataReleaseClient.tag_of(manifest.name, manifest.content_hash)
        archive_file_name = ArtifactArchiver.archive_file_name(manifest.name)
        release = ArtifactDataReleaseClient.find(tag)
        if release is None:
            contents = cls._read_matching_cached_files(cls._cache_folder_of(manifest), manifest)
            if contents is None:
                raise ArtifactError(
                    f"The cache lacks the data files of {manifest.short_identity}; "
                    "save the artifact before publishing it."
                )
            ArtifactDataReleaseClient.create(
                tag,
                archive_file_name,
                ArtifactArchiver.pack(contents),
                title=f"Data: {manifest.short_identity}",
                notes=f"Data files of the sunnbear artifact `{manifest.name}`, content hash `{manifest.content_hash}`.",
            )
            # `create` returns nothing, so read the release back for the archive's download URL.
            release = ArtifactDataReleaseClient.find(tag)
        if release is None or release.is_draft or archive_file_name not in release.file_urls:
            raise ArtifactError(
                f"The data release {tag} is a draft or lacks {archive_file_name}, e.g. because publishing "
                f"was interrupted; delete the release with `gh release delete {tag} --cleanup-tag` and publish again."
            )
        url = release.file_urls[archive_file_name]
        try:
            archive_bytes = cls._download(url)
        except _DOWNLOAD_ERRORS as error:
            raise ArtifactError(f"Downloading {url} back failed: {error}") from error
        cls._unpack_and_check(manifest, archive_bytes)
        published_manifest = manifest.model_copy(
            update={"archive": ArtifactArchiveEntry.from_content(url, archive_bytes)}
        )
        cls._write_manifest(declaration_cls, published_manifest)
        return published_manifest

    # --------------------------------------------------------------------------
    #  Downloaded files
    # --------------------------------------------------------------------------
    @classmethod
    def _read_or_unpack_downloaded_files(cls, manifest: ArtifactManifest) -> dict[str, bytes]:
        """Return a downloaded artifact's data files from the cache, unpacking its archive there first if needed.

        The archive is needed when a cached file is missing or differs from its manifest entry. The
        archive is deleted from the cache folder once its files are unpacked.

        Raises:
            ArtifactError: If the archive is needed but cannot be read or downloaded, or its files do
                not match the manifest.
        """
        cache_folder = cls._cache_folder_of(manifest)
        cached_contents = cls._read_matching_cached_files(cache_folder, manifest)
        if cached_contents is not None:
            return cached_contents
        archive_file = cache_folder / ArtifactArchiver.archive_file_name(manifest.name)
        contents = cls._unpack_and_check(manifest, cls._read_or_download_archive(manifest, archive_file))
        cls._write_files(cache_folder, contents)
        archive_file.unlink(missing_ok=True)
        return contents

    @staticmethod
    def _unpack_and_check(manifest: ArtifactManifest, archive_bytes: bytes) -> dict[str, bytes]:
        """Return the data files unpacked from the artifact's archive, each checked against its manifest entry.

        Raises:
            ArtifactError: If the archive cannot be unpacked, or holds files that differ from the
                manifest.
        """
        contents = ArtifactArchiver.unpack(archive_bytes, [entry.path for entry in manifest.files])
        differing_paths = [entry.path for entry in manifest.files if not entry.matches(contents[entry.path])]
        if differing_paths:
            raise ArtifactError(
                f"The archive of {manifest.short_identity} holds files that differ from the manifest: "
                f"{differing_paths}."
            )
        return contents

    @staticmethod
    def _read_matching_cached_files(cache_folder: Path, manifest: ArtifactManifest) -> dict[str, bytes] | None:
        """Return the cached data files, or ``None`` if any of them is missing or differs from its manifest entry."""
        contents = {}
        for entry in manifest.files:
            cache_file = cache_folder / entry.path
            if not cache_file.is_file():
                return None
            content = cache_file.read_bytes()
            if not entry.matches(content):
                return None
            contents[entry.path] = content
        return contents

    @classmethod
    def _read_or_download_archive(cls, manifest: ArtifactManifest, archive_file: Path) -> bytes:
        """Return the artifact's archive: from `archive_file` if it matches the ``archive`` entry, else downloaded.

        Raises:
            ArtifactError: If the manifest has no ``archive`` entry, the download fails, or the
                downloaded bytes do not match the entry; for a failed or mismatched download, the
                message names `archive_file`, where the archive can be placed by hand.
        """
        archive_entry = manifest.archive
        if archive_entry is None:
            raise ArtifactError(
                f"The manifest of artifact {manifest.short_identity} has no archive entry, "
                f"and {archive_file.parent} holds no matching copy of its files."
            )
        if archive_file.is_file():
            archive_bytes = archive_file.read_bytes()
            if archive_entry.matches(archive_bytes):
                return archive_bytes
        try:
            archive_bytes = cls._download(archive_entry.url)
        except _DOWNLOAD_ERRORS as error:
            raise ArtifactError(
                f"Downloading {archive_entry.url} failed: {error}. The archive can also be placed at {archive_file}."
            ) from error
        if not archive_entry.matches(archive_bytes):
            raise ArtifactError(
                f"The archive downloaded from {archive_entry.url} does not match the size and sha256 in the manifest. "
                f"The correct archive can also be placed at {archive_file}."
            )
        return archive_bytes

    @staticmethod
    def _download(url: str) -> bytes:
        """Return the bytes at `url`; every download goes through this method, so tests can replace it.

        Raises:
            OSError: If the connection fails or the server returns an error status.
            ValueError: If `url` is malformed or its scheme is unsupported.
            http.client.HTTPException: If the server's response is malformed or cut short.
        """
        # The URLs come from committed manifests, so they are not user input.
        with urllib.request.urlopen(url, timeout=_DOWNLOAD_TIMEOUT_SEC) as response:  # noqa: S310
            return response.read()

    @staticmethod
    def _cache_folder_of(manifest: ArtifactManifest) -> Path:
        """Return a downloaded artifact's cache folder, under ``SUNNBEAR_CACHE_DIR`` if set, else the user cache."""
        cache_root = os.environ.get(_CACHE_DIR_ENV_VAR) or platformdirs.user_cache_dir("sunnbear")
        return Path(cache_root) / manifest.name / manifest.content_hash

    # --------------------------------------------------------------------------
    #  Files and folders
    # --------------------------------------------------------------------------
    @classmethod
    def _folder_of(cls, declaration_cls: type[ArtifactDeclaration]) -> Traversable:
        """Return the artifact's folder, which holds the manifest.

        The folder's location follows from the module that defines the declaration.
        """
        if is_defined_in_sunnbear(declaration_cls):
            return cls._builtin_artifacts_folder().joinpath(declaration_cls.name)
        else:
            module_file = sys.modules[declaration_cls.__module__].__file__
            return Path(str(module_file)).parent / _ARTIFACTS_FOLDER_NAME / declaration_cls.name

    @classmethod
    def _folder_on_disk_of(cls, declaration_cls: type[ArtifactDeclaration]) -> Path:
        """Return the artifact's folder, checked to be a directory on disk so that it can be written to.

        Raises:
            ArtifactError: If the folder is not a directory on disk, e.g. inside a zipped install.
        """
        folder = cls._folder_of(declaration_cls)
        if not isinstance(folder, Path):
            raise ArtifactError(f"The folder of {declaration_cls.__name__} is not a writable directory: {folder}.")
        return folder

    @classmethod
    def _write_manifest(cls, declaration_cls: type[ArtifactDeclaration], manifest: ArtifactManifest) -> None:
        """Write `manifest` to the artifact's folder, creating the folder if needed."""
        folder = cls._folder_on_disk_of(declaration_cls)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / _MANIFEST_FILE_NAME).write_text(manifest.to_json())

    @staticmethod
    def _builtin_artifacts_folder() -> Traversable:
        """Return the folder that holds one subfolder per built-in artifact.

        The folder does not exist until the first built-in artifact is saved.
        """
        return files(_BUILTIN_ARTIFACTS_PARENT_PACKAGE).joinpath(_ARTIFACTS_FOLDER_NAME)

    @staticmethod
    def _read_file(folder: Traversable, path: str, declaration_cls: type[ArtifactDeclaration]) -> bytes:
        """Return the bytes of one file in an artifact's folder.

        Raises:
            ArtifactError: If the file does not exist.
        """
        file = folder.joinpath(path)
        if not file.is_file():
            raise ArtifactError(f"{declaration_cls.__name__} has no file {path!r} in {folder}.")
        return file.read_bytes()

    @staticmethod
    def _write_files(folder: Path, contents: dict[str, bytes]) -> None:
        """Write each file in `contents`, a dict that maps each path below `folder` to its content."""
        for path, content in contents.items():
            (folder / path).parent.mkdir(parents=True, exist_ok=True)
            (folder / path).write_bytes(content)

    @classmethod
    def _relative_file_paths(cls, folder: Traversable) -> set[str]:
        """Return the path of every file below `folder`, relative to it, with forward slashes; `folder` must exist."""
        paths = set()
        for child in folder.iterdir():
            if child.is_dir():
                paths |= {f"{child.name}/{path}" for path in cls._relative_file_paths(child)}
            else:
                paths.add(child.name)
        return paths

    @classmethod
    def _relative_data_file_paths(cls, folder: Traversable) -> set[str]:
        """Return the path of every file in an artifact's existing `folder` except the manifest, relative to it."""
        return cls._relative_file_paths(folder) - {_MANIFEST_FILE_NAME}
