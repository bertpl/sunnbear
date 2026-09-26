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
  root is ``SUNNBEAR_DATA_DIR`` when that environment variable is set, else the user's cache folder
  for sunnbear. When the cache lacks a data file, or holds it with other content, loading downloads
  it from the URL in the file's manifest entry and checks its hash.
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

from .artifact_declaration import ArtifactDeclaration
from .artifact_manifest import ArtifactFileEntry, ArtifactManifest
from .artifact_registry import ArtifactRegistry
from .artifact_source import ArtifactSource
from .exceptions import ArtifactError

T = TypeVar("T")

_MANIFEST_FILE_NAME = "manifest.json"
_ARTIFACTS_FOLDER_NAME = "artifacts"
_BUILTIN_ARTIFACTS_PARENT_PACKAGE = "sunnbear._core.data"
_DATA_DIR_ENV_VAR = "SUNNBEAR_DATA_DIR"
_DOWNLOAD_TIMEOUT_SEC = 60


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

        A file shipped in the package is read without checking its hash. A downloaded file is read
        from the cache when the cache holds a copy that matches its manifest entry; otherwise it is
        downloaded, checked against its entry, and stored in the cache.

        Raises:
            ArtifactError: If any of these holds:

                - the manifest is missing, malformed or names another artifact;
                - a file shipped in the package is missing;
                - a downloaded file is not in the cache and has no URL, its download fails, or the
                  downloaded bytes do not match its manifest entry; the message names the cache path,
                  where the file can also be placed by hand.
        """
        manifest = cls.load_manifest(declaration_cls)
        contents = {entry.path: cls._read_data_file(declaration_cls, manifest, entry) for entry in manifest.files}
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
        - **download**: into the cache folder; the manifest records no download URL, because `save`
          does not upload the files, so no URL exists for them yet.

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
        folder = cls._folder_of(declaration_cls)
        if not isinstance(folder, Path):
            raise ArtifactError(f"The folder of {declaration_cls.__name__} is not a writable directory: {folder}.")
        match declaration_cls.source:
            case ArtifactSource.PACKAGE:
                data_folder, kept_paths = folder, set(contents)
            case ArtifactSource.DOWNLOAD:
                data_folder, kept_paths = cls._cache_folder_of(manifest), set()
            case _:
                assert_never(declaration_cls.source)
        folder.mkdir(parents=True, exist_ok=True)
        for stale_path in cls._relative_data_file_paths(folder) - kept_paths:
            (folder / stale_path).unlink()
        for path, content in contents.items():
            (data_folder / path).parent.mkdir(parents=True, exist_ok=True)
            (data_folder / path).write_bytes(content)
        (folder / _MANIFEST_FILE_NAME).write_text(manifest.to_json())
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
                - for a downloaded artifact, a data file lies next to the manifest, or a file entry
                  has no download URL.
        """
        manifest = cls.load_manifest(declaration_cls)
        folder = cls._folder_of(declaration_cls)
        present_paths = cls._relative_data_file_paths(folder)
        match declaration_cls.source:
            case ArtifactSource.PACKAGE:
                problems = cls._compare_shipped_files_with_manifest(folder, present_paths, manifest)
            case ArtifactSource.DOWNLOAD:
                problems = [
                    f"{path} is next to the manifest, but the artifact's data files are downloaded"
                    for path in sorted(present_paths)
                ]
                problems += [f"{entry.path} has no download URL" for entry in manifest.files if entry.url is None]
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
        """Return a problem for each data file that is missing from `folder`, differs from its entry, or is unlisted."""
        listed_paths = {entry.path for entry in manifest.files}
        problems = [f"{path} is not listed in the manifest" for path in sorted(present_paths - listed_paths)]
        for entry in manifest.files:
            if entry.path not in present_paths:
                problems.append(f"{entry.path} is missing")
            elif not entry.matches(folder.joinpath(entry.path).read_bytes()):
                problems.append(f"{entry.path} differs from its manifest entry")
        return problems

    # --------------------------------------------------------------------------
    #  Data files
    # --------------------------------------------------------------------------
    @classmethod
    def _read_data_file(
        cls, declaration_cls: type[ArtifactDeclaration], manifest: ArtifactManifest, entry: ArtifactFileEntry
    ) -> bytes:
        """Return the bytes of one data file, from the package or from the download cache."""
        match declaration_cls.source:
            case ArtifactSource.PACKAGE:
                return cls._read_file(cls._folder_of(declaration_cls), entry.path, declaration_cls)
            case ArtifactSource.DOWNLOAD:
                return cls._read_downloaded_file(manifest, entry)
            case _:
                assert_never(declaration_cls.source)

    @classmethod
    def _read_downloaded_file(cls, manifest: ArtifactManifest, entry: ArtifactFileEntry) -> bytes:
        """Return a downloaded data file from the cache, downloading it first if the cache holds no matching copy.

        Raises:
            ArtifactError: If the file is not in the cache and has no URL, its download fails, or the
                downloaded bytes do not match the entry.
        """
        cache_file = cls._cache_folder_of(manifest) / entry.path
        if cache_file.is_file():
            content = cache_file.read_bytes()
            if entry.matches(content):
                return content
        if entry.url is None:
            raise ArtifactError(
                f"Artifact {manifest.short_identity} has no download URL for {entry.path}, "
                f"and {cache_file} holds no matching copy."
            )
        try:
            content = cls._download(entry.url)
        except (OSError, ValueError, http.client.HTTPException) as error:
            raise ArtifactError(f"Downloading {entry.url} to {cache_file} failed: {error}") from error
        if not entry.matches(content):
            raise ArtifactError(
                f"The file downloaded from {entry.url} does not match its manifest entry, "
                f"so it was not stored at {cache_file}."
            )
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_bytes(content)
        return content

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
        """Return the cache folder of a downloaded artifact's data files.

        The folder is ``<cache root>/<artifact name>/<content hash>``.
        """
        cache_root = os.environ.get(_DATA_DIR_ENV_VAR) or platformdirs.user_cache_dir("sunnbear")
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
