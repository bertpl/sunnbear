"""This module lists the built-in data artifacts, and reads the manifest of one of them."""

import functools
import importlib
import pkgutil

from sunnbear._core.data import ArtifactDeclaration, ArtifactError, ArtifactManifest, ArtifactRegistry, ArtifactStore
from sunnbear._core.utils.class_origin import is_defined_in_sunnbear

# Every module below this package is imported, so every built-in declaration is registered.
_CORE_PACKAGE = "sunnbear._core"


def artifact_names() -> tuple[str, ...]:
    """Return the names of sunnbear's built-in data artifacts, sorted."""
    return tuple(declaration_cls.name for declaration_cls in _builtin_declarations())


def artifact_manifest(name: str) -> ArtifactManifest:
    """Return the manifest of the built-in data artifact with this name, without reading or downloading its data files.

    The manifest records the artifact's content hash, the versions of the libraries that built it,
    and, where one exists, the public call that generated it.

    Raises:
        ArtifactError: If sunnbear has no data artifact with this name, or its manifest is missing
            or malformed.
    """
    declarations_by_name = {declaration_cls.name: declaration_cls for declaration_cls in _builtin_declarations()}
    if name not in declarations_by_name:
        raise ArtifactError(
            f"sunnbear has no data artifact named {name!r}; its data artifacts are {sorted(declarations_by_name)}."
        )
    return ArtifactStore.load_manifest(declarations_by_name[name])


def import_builtin_declarations() -> None:
    """Import every module of `sunnbear._core`, so that every built-in declaration is registered.

    The imports run once per process; later calls return at once.
    """
    _import_core_modules()


# ==================================================================================================
#  Helpers
# ==================================================================================================
def _builtin_declarations() -> list[type[ArtifactDeclaration]]:
    """Return the registered declarations that are defined inside sunnbear, sorted by name."""
    import_builtin_declarations()
    return [
        declaration_cls
        for declaration_cls in ArtifactRegistry.declarations()
        if is_defined_in_sunnbear(declaration_cls)
    ]


@functools.cache
def _import_core_modules() -> None:
    """Import every module of `sunnbear._core`, once per process."""
    core_package = importlib.import_module(_CORE_PACKAGE)
    for module_info in pkgutil.walk_packages(core_package.__path__, prefix=f"{_CORE_PACKAGE}."):
        importlib.import_module(module_info.name)
