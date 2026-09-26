"""`ArtifactStore` is the only code that reads or writes a data artifact's files and manifest.

An artifact's data files and its ``manifest.json`` live in one folder, which the store derives from
where the artifact's declaration is defined, so no caller passes a location:

- a declaration inside the sunnbear package uses ``_core/data/artifacts/<name>/``, which ships with
  sunnbear;
- any other declaration, in practice a test fixture, uses ``artifacts/<name>/`` next to its own
  module, so its files never ship.

Loading does not check file hashes: the files ship inside the package, and the test suite runs
`ArtifactStore.verify_builtin_artifacts` on every change.
"""

import datetime
import importlib.metadata
import sys
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any, TypeVar

from sunnbear._core.utils.class_origin import is_defined_in_sunnbear

from .artifact_declaration import ArtifactDeclaration
from .artifact_manifest import ArtifactFileEntry, ArtifactManifest
from .artifact_registry import ArtifactRegistry
from .exceptions import ArtifactError

T = TypeVar("T")

_MANIFEST_FILE_NAME = "manifest.json"
_ARTIFACTS_FOLDER_NAME = "artifacts"
# The package whose ``artifacts`` folder holds the built-in artifacts: this module's own package.
_BUILTIN_ARTIFACTS_PACKAGE = "sunnbear._core.data"


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
        """Read the artifact's files and rebuild its value through the declaration.

        Raises:
            ArtifactError: If the manifest is missing, malformed or names another artifact, or lists
                a file that is missing.
        """
        manifest = cls.load_manifest(declaration_cls)
        folder = cls._folder_of(declaration_cls)
        contents = {entry.path: cls._read_file(folder, entry.path, declaration_cls) for entry in manifest.files}
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
        """Write the artifact's files for `value` and a new manifest, replacing what the folder held.

        Files that the new value does not produce are deleted, so the folder holds exactly what the
        manifest lists. The manifest lists the files in path order, so the content hash does not
        depend on the order in which `ArtifactDeclaration.to_files` returns them.

        Args:
            declaration_cls: The artifact's declaration.
            value: The value to write.
            built_with: The versions of the libraries that affect the content, keyed by package
                name; sunnbear's own version is always recorded.
            input_artifact_hashes: The content hashes of the artifacts that `value` was generated
                from, keyed by artifact name.
            generated_by: The public function call that generated `value`, as JSON-compatible data.

        Returns:
            The manifest that was written.

        Raises:
            ArtifactError: If the declaration produces a file named like the manifest, or the
                artifact's folder is not a writable directory, e.g. inside a zipped install.
        """
        contents = declaration_cls.to_files(value)
        if _MANIFEST_FILE_NAME in contents:
            raise ArtifactError(f"{declaration_cls.__name__} produces a data file named {_MANIFEST_FILE_NAME!r}.")
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
        folder.mkdir(parents=True, exist_ok=True)
        for stale_path in cls._relative_file_paths(folder) - set(contents) - {_MANIFEST_FILE_NAME}:
            (folder / stale_path).unlink()
        for path, content in contents.items():
            (folder / path).parent.mkdir(parents=True, exist_ok=True)
            (folder / path).write_bytes(content)
        (folder / _MANIFEST_FILE_NAME).write_text(manifest.to_json())
        return manifest

    # --------------------------------------------------------------------------
    #  Verification
    # --------------------------------------------------------------------------
    @classmethod
    def verify(cls, declaration_cls: type[ArtifactDeclaration]) -> ArtifactManifest:
        """Check that the artifact's folder holds exactly the files its manifest lists, with matching content.

        Returns:
            The artifact's manifest.

        Raises:
            ArtifactError: If the manifest is missing, malformed or names another artifact, or a file
                is missing, differs from its entry, or is not listed.
        """
        manifest = cls.load_manifest(declaration_cls)
        folder = cls._folder_of(declaration_cls)
        present_paths = cls._relative_file_paths(folder) - {_MANIFEST_FILE_NAME}
        listed_paths = {entry.path for entry in manifest.files}
        problems = [f"{path} is not listed in the manifest" for path in sorted(present_paths - listed_paths)]
        for entry in manifest.files:
            if entry.path not in present_paths:
                problems.append(f"{entry.path} is missing")
            elif not entry.matches(folder.joinpath(entry.path).read_bytes()):
                problems.append(f"{entry.path} differs from its manifest entry")
        if problems:
            raise ArtifactError(f"Artifact {manifest.short_identity} fails verification: {'; '.join(problems)}.")
        return manifest

    @classmethod
    def verify_builtin_artifacts(cls) -> None:
        """Verify every built-in declaration, and check that every folder of built-in artifacts has a declaration.

        Only the declarations whose modules have been imported are known, so import the sunnbear
        modules that declare artifacts first.

        Raises:
            ArtifactError: Listing every built-in artifact that fails `verify`, and every folder of
                built-in artifacts that no declaration uses.
        """
        builtin_declarations = [d for d in ArtifactRegistry.declarations() if is_defined_in_sunnbear(d)]
        problems = []
        for declaration_cls in builtin_declarations:
            try:
                cls.verify(declaration_cls)
            except ArtifactError as error:
                problems.append(str(error))
        root = cls._builtin_artifacts_root()
        folder_names = {child.name for child in root.iterdir() if child.is_dir()} if root.is_dir() else set()
        declared_names = {declaration_cls.name for declaration_cls in builtin_declarations}
        problems += [f"Folder {name!r} holds no declared artifact" for name in sorted(folder_names - declared_names)]
        if problems:
            raise ArtifactError("Built-in artifacts are inconsistent:\n- " + "\n- ".join(problems))

    # --------------------------------------------------------------------------
    #  Files and folders
    # --------------------------------------------------------------------------
    @classmethod
    def _folder_of(cls, declaration_cls: type[ArtifactDeclaration]) -> Traversable:
        """Return the folder of an artifact's files and manifest, derived from where its declaration is defined."""
        if is_defined_in_sunnbear(declaration_cls):
            return cls._builtin_artifacts_root().joinpath(declaration_cls.name)
        else:
            module_file = sys.modules[declaration_cls.__module__].__file__
            return Path(str(module_file)).parent / _ARTIFACTS_FOLDER_NAME / declaration_cls.name

    @staticmethod
    def _builtin_artifacts_root() -> Traversable:
        """Return the folder that holds one subfolder per built-in artifact, read through `importlib.resources`."""
        # The folder need not exist yet: it is created by saving the first built-in artifact.
        return files(_BUILTIN_ARTIFACTS_PACKAGE).joinpath(_ARTIFACTS_FOLDER_NAME)

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
        """Return the path of every file below the existing `folder`, relative to it, with forward slashes."""
        paths = set()
        for child in folder.iterdir():
            if child.is_dir():
                paths |= {f"{child.name}/{path}" for path in cls._relative_file_paths(child)}
            else:
                paths.add(child.name)
        return paths
