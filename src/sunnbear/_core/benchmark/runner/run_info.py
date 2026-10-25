"""`BenchmarkRunInfo` records what a run's results depend on, with 1 `BenchmarkRunProblemInfo` per test problem.

A run's results depend on:

- its `BenchmarkRunSettings`;
- the solvers, by id and version;
- the test problems, by id and calibrated c-range;
- the identity of every data artifact that the run loads, such as the Monte Carlo tuple set;
- the versions of Python, of sunnbear, and of sunnbear's installed dependencies.

A resumed run must depend on exactly the same inputs and versions, so `check_resumable_as` compares the
stored run info with the run info of the call that resumes the run.

The results of 2 runs can be read as 1 table when `check_combinable_with` accepts their run infos.

The platform and the timestamps are recorded for information only; neither `check_resumable_as` nor
`check_combinable_with` compares them.
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
from sunnbear._core.benchmark.mc_tuples import MCTuplesDeclaration
from sunnbear._core.problems.core import ProblemId, TestProblem
from sunnbear._core.solvers.core import SolverConfig
from sunnbear._core.utils.mapping_comparison import any_value_of_common_key_differs, common_dict_keys

from .exceptions import BenchmarkRunError
from .run_settings import BenchmarkRunSettings

# A requirement string starts with the distribution name, which ends at the first character that a name
# cannot contain, e.g. `numpy` in "numpy>=2.0.0; python_version == '3.12'".
_REQUIREMENT_NAME_END_PATTERN = re.compile(r"[^A-Za-z0-9._-]")

# These run info fields are recorded for information only; no check compares them.
_FIELDS_FOR_INFORMATION_ONLY = frozenset({"platform", "started_at", "finished_at"})

# These run info fields list a run's solvers and test problems; runs that are combined may list different ones,
# so `check_combinable_with` compares only the entries that both runs list.
_FIELDS_LISTING_SOLVERS_AND_PROBLEMS = frozenset({"solver_versions", "problem_infos"})


# ==================================================================================================
#  BenchmarkRunInfo
# ==================================================================================================
class BenchmarkRunInfo(BaseModel):
    """`BenchmarkRunInfo` records a benchmark run: what its results depend on, and where and when it ran.

    Attributes:
        run_settings: The settings that every task of the run shares.
        solver_versions: The version of each solver config's solver class, keyed by solver id, in the
            order of the result rows.
        problem_infos: The test problems, in the caller's order.
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
    problem_infos: tuple["BenchmarkRunProblemInfo", ...]
    artifact_hashes: dict[str, str]
    package_versions: dict[str, str]
    platform: str
    started_at: datetime.datetime
    finished_at: datetime.datetime | None = None

    # --------------------------------------------------------------------------
    #  Construction
    # --------------------------------------------------------------------------
    @classmethod
    def for_current_inputs(
        cls,
        *,
        run_settings: BenchmarkRunSettings,
        solver_configs: Sequence[SolverConfig],
        problems: Sequence[TestProblem],
    ) -> Self:
        """Return the run info of these inputs, started now, with this process's artifact hashes and package versions.

        A call that resumes a run compares this run info with the stored one.

        Raises:
            ValueError: If `solver_configs` or `problems` is empty or holds an id twice.
        """
        cls._validate_ids_are_nonempty_and_unique("solver_configs", [config.solver_id for config in solver_configs])
        cls._validate_ids_are_nonempty_and_unique("problems", [str(problem.id) for problem in problems])
        return cls(
            run_settings=run_settings,
            solver_versions={config.solver_id: config.solver_cls.version for config in solver_configs},
            problem_infos=tuple(BenchmarkRunProblemInfo.from_test_problem(problem) for problem in problems),
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
        """Return the formula ids of the run's test problems, each once, in order of first appearance.

        The run runs its formulas in this order, and its results list them in this order.
        """
        return list(dict.fromkeys(problem_info.formula_id for problem_info in self.problem_infos))

    @property
    def problem_infos_by_id(self) -> dict[str, "BenchmarkRunProblemInfo"]:
        """Return the run's test problem infos, keyed by problem id."""
        return {problem_info.problem_id: problem_info for problem_info in self.problem_infos}

    # --------------------------------------------------------------------------
    #  Resuming
    # --------------------------------------------------------------------------
    def check_resumable_as(self, other: "BenchmarkRunInfo") -> None:
        """Check that `other`, the run info of the call that resumes this run, has the same inputs and versions.

        Raises:
            BenchmarkRunError: If any field other than the platform and the timestamps differs, naming
                each such field.
        """
        differing_fields = self._differing_fields(other, ignored_fields=_FIELDS_FOR_INFORMATION_ONLY)
        if differing_fields:
            raise BenchmarkRunError(
                f"The run directory holds a run with different {', '.join(differing_fields)}; "
                f"resume it with the same inputs and packages, or use another directory."
            )

    # --------------------------------------------------------------------------
    #  Combining
    # --------------------------------------------------------------------------
    def check_combinable_with(self, other: "BenchmarkRunInfo") -> None:
        """Check that the results of this run info's run and of `other`'s run can be read as 1 table.

        Both runs must depend on the same inputs and versions, except that the runs may cover different solvers
        and test problems:

        - a solver in both runs must have the same version, and a test problem in both runs must have the
          same c-range;
        - no solver may have run on the same test problem in both runs, since the table would then hold
          those solves twice.

        Raises:
            BenchmarkRunError: If a field differs, naming each such field, or if a solver ran on the same
                test problem in both runs.
        """
        # --- fields that must be the same -------
        differing_fields = self._differing_fields(
            other, ignored_fields=_FIELDS_FOR_INFORMATION_ONLY | _FIELDS_LISTING_SOLVERS_AND_PROBLEMS
        )

        # --- solvers and problems in both runs --
        common_solver_ids = common_dict_keys(self.solver_versions, other.solver_versions)
        if any_value_of_common_key_differs(self.solver_versions, other.solver_versions):
            differing_fields.append("solver_versions")
        problem_infos_by_id = self.problem_infos_by_id
        other_problem_infos_by_id = other.problem_infos_by_id
        common_problem_ids = common_dict_keys(problem_infos_by_id, other_problem_infos_by_id)
        if any_value_of_common_key_differs(problem_infos_by_id, other_problem_infos_by_id):
            differing_fields.append("problem_infos")

        if differing_fields:
            raise BenchmarkRunError(f"The runs have different {', '.join(differing_fields)}.")
        if common_solver_ids and common_problem_ids:
            raise BenchmarkRunError(
                f"Both runs ran the solvers {common_solver_ids} on the test problems {common_problem_ids}."
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
    def _differing_fields(self, other: "BenchmarkRunInfo", *, ignored_fields: frozenset[str]) -> list[str]:
        """Return the fields outside `ignored_fields` whose values differ between this run info and `other`."""
        return [
            name
            for name in type(self).model_fields
            if name not in ignored_fields and getattr(self, name) != getattr(other, name)
        ]

    @staticmethod
    def _validate_ids_are_nonempty_and_unique(argument_name: str, ids: Sequence[str]) -> None:
        """Check that `ids`, the ids of the items of the argument `argument_name`, is not empty and holds no id twice.

        The run info keys the solvers by id, so a repeated solver id would merge 2 solvers into 1 entry; a
        repeated problem id would run that test problem twice.

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
#  BenchmarkRunProblemInfo
# ==================================================================================================
class BenchmarkRunProblemInfo(BaseModel):
    """`BenchmarkRunProblemInfo` records 1 test problem of a run: its id and its calibrated c-range."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    problem_id: str
    c_min: float
    c_max: float

    @classmethod
    def from_test_problem(cls, problem: TestProblem) -> Self:
        """Return the record of a calibrated test problem."""
        return cls(problem_id=str(problem.id), c_min=problem.c_min, c_max=problem.c_max)

    @property
    def formula_id(self) -> str:
        """Return the formula id of the test problem, e.g. ``f2.1.1``."""
        return ProblemId.from_string(self.problem_id).formula_id
