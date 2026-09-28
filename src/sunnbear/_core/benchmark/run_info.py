"""This module defines `BenchmarkRunInfo` and the `BenchmarkRunFunctionInfo` records that it holds.

A run's results depend on:

- its `BenchmarkRunSettings`;
- the solvers, by id and version;
- the test functions, by id and calibrated c-range;
- the identity of every data artifact that the run loads, such as the Monte Carlo tuple set;
- the versions of Python, of sunnbear, and of sunnbear's installed dependencies.

A resumed run must depend on exactly the same inputs and versions, so `check_resumable_as` compares the
stored run info with the run info of the call that resumes the run.

The platform and the timestamps are recorded for readers only.
"""

import datetime
import importlib.metadata
import json
import platform
import re
from collections.abc import Sequence
from typing import Self

from pydantic import BaseModel, ConfigDict

from sunnbear._core.artifacts import ArtifactStore
from sunnbear._core.functions.core import FunctionId, TestFunction
from sunnbear._core.solvers.core import SolverConfig

from .exceptions import BenchmarkRunError
from .mc_tuples.artifact import MCTuplesDeclaration
from .run_settings import BenchmarkRunSettings

# A requirement string starts with the distribution name, which ends at the first character that a name
# cannot contain, e.g. `numpy` in "numpy>=2.0.0; python_version == '3.12'".
_REQUIREMENT_NAME_END_PATTERN = re.compile(r"[^A-Za-z0-9._-]")


# ==================================================================================================
#  BenchmarkRunInfo
# ==================================================================================================
class BenchmarkRunInfo(BaseModel):
    """`BenchmarkRunInfo` records a benchmark run: what its results depend on, and where and when it ran.

    Attributes:
        run_settings: The settings that every task of the run shares.
        solver_versions: The version of each solver config's solver class, keyed by solver id, in the
            order of the result rows.
        functions: The test functions, in the caller's order.
        artifact_hashes: The content hash of every data artifact that the run loads, keyed by artifact
            name.
        package_versions: The versions of Python, of sunnbear, and of every installed runtime dependency
            of sunnbear, keyed by name.
        platform: The operating system and machine architecture, e.g. ``Linux-x86_64``.
        started_at: When the run started, in UTC; a resumed run keeps the time of its first start.
        finished_at: When the last formula's results file was written, in UTC; ``None`` while the run
            is not finished.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    run_settings: BenchmarkRunSettings
    solver_versions: dict[str, int]
    functions: tuple["BenchmarkRunFunctionInfo", ...]
    artifact_hashes: dict[str, str]
    package_versions: dict[str, str]
    platform: str
    started_at: datetime.datetime
    finished_at: datetime.datetime | None = None

    # --------------------------------------------------------------------------
    #  Construction
    # --------------------------------------------------------------------------
    @classmethod
    def for_new_run(
        cls,
        *,
        run_settings: BenchmarkRunSettings,
        solver_configs: Sequence[SolverConfig],
        functions: Sequence[TestFunction],
    ) -> Self:
        """Return the run info of a run that starts now, with the artifact hashes and package versions of this process.

        Raises:
            ValueError: If `solver_configs` or `functions` is empty or holds an id twice.
        """
        cls._check_ids_are_unique("solver_configs", [config.solver_id for config in solver_configs])
        cls._check_ids_are_unique("functions", [str(function.id) for function in functions])
        return cls(
            run_settings=run_settings,
            solver_versions={config.solver_id: config.solver_cls.version for config in solver_configs},
            functions=tuple(BenchmarkRunFunctionInfo.from_test_function(function) for function in functions),
            artifact_hashes={
                MCTuplesDeclaration.name: ArtifactStore.load_manifest(MCTuplesDeclaration).content_hash,
            },
            package_versions=cls._installed_package_versions(),
            platform=f"{platform.system()}-{platform.machine()}",
            started_at=datetime.datetime.now(datetime.UTC),
        )

    def with_finished_at_now(self) -> Self:
        """Return a copy of this run info whose `finished_at` is now."""
        return self.model_copy(update={"finished_at": datetime.datetime.now(datetime.UTC)})

    # --------------------------------------------------------------------------
    #  Derived values
    # --------------------------------------------------------------------------
    @property
    def is_finished(self) -> bool:
        """A run is finished when every formula's results file was written."""
        return self.finished_at is not None

    @property
    def formula_ids(self) -> list[str]:
        """The formula ids of the run's test functions, each once, in order of first appearance, e.g. ``["f2.1.1"]``."""
        return list(dict.fromkeys(function.formula_id for function in self.functions))

    # --------------------------------------------------------------------------
    #  Resuming
    # --------------------------------------------------------------------------
    def check_resumable_as(self, other: "BenchmarkRunInfo") -> None:
        """Check that `other`, the run info of a run that wants to resume this run, has the same inputs and versions.

        Raises:
            BenchmarkRunError: If any field other than the platform and the timestamps differs, naming
                each such field.
        """
        fields_for_readers_only = {"platform", "started_at", "finished_at"}
        differing_fields = [
            name
            for name in type(self).model_fields
            if name not in fields_for_readers_only and getattr(self, name) != getattr(other, name)
        ]
        if differing_fields:
            raise BenchmarkRunError(
                f"The run folder holds a run with different {', '.join(differing_fields)}; "
                f"resume it with the same inputs and packages, or use another folder."
            )

    # --------------------------------------------------------------------------
    #  JSON
    # --------------------------------------------------------------------------
    def to_json(self) -> str:
        """Return the run info as JSON that `from_json` parses back, with sorted keys for readable diffs."""
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2) + "\n"

    @classmethod
    def from_json(cls, text: str) -> Self:
        """Parse a run info written by `to_json`.

        Raises:
            BenchmarkRunError: If the text is not a well-formed run info.
        """
        try:
            return cls.model_validate_json(text)
        except ValueError as error:
            raise BenchmarkRunError(f"Malformed run info: {error}") from error

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _check_ids_are_unique(argument_name: str, ids: Sequence[str]) -> None:
        """Check that `ids`, the ids of the items of the argument `argument_name`, is not empty and holds no id twice.

        The run info keys the solvers by id, so a repeated id would merge 2 solvers into 1 entry.

        Raises:
            ValueError: If `ids` is empty or holds an id twice.
        """
        if not ids:
            raise ValueError(f"{argument_name} must hold at least 1 item.")
        duplicate_ids = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
        if duplicate_ids:
            raise ValueError(f"{argument_name} holds these ids more than once: {duplicate_ids}.")

    @staticmethod
    def _installed_package_versions() -> dict[str, str]:
        """Return the versions of Python, of sunnbear, and of every installed runtime dependency of sunnbear.

        The dependencies are sunnbear's declared requirements; one that is not installed, because its
        environment marker excludes this Python version, is left out.
        """
        versions = {"python": platform.python_version(), "sunnbear": importlib.metadata.version("sunnbear")}
        for requirement in importlib.metadata.requires("sunnbear") or []:
            name = _REQUIREMENT_NAME_END_PATTERN.split(requirement, maxsplit=1)[0]
            try:
                versions[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                continue
        return versions


# ==================================================================================================
#  BenchmarkRunFunctionInfo
# ==================================================================================================
class BenchmarkRunFunctionInfo(BaseModel):
    """`BenchmarkRunFunctionInfo` records 1 test function of a run: its id and its calibrated c-range."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    function_id: str
    c_min: float
    c_max: float

    @classmethod
    def from_test_function(cls, function: TestFunction) -> Self:
        """Return the record of a calibrated test function."""
        return cls(function_id=str(function.id), c_min=function.c_min, c_max=function.c_max)

    @property
    def formula_id(self) -> str:
        """The formula id of the test function, e.g. ``f2.1.1``."""
        return FunctionId.from_string(self.function_id).formula_id
