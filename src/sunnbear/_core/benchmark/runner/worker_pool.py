"""`BenchmarkWorkerPool` runs benchmark tasks in worker processes, or in this process when it has 1 worker.

A task looks up its formula and solver configs by id in registries, and each formula or solver config class
adds itself to its registry when it is defined.

A worker process has only imported sunnbear itself, so every
worker first imports the modules that define the run's formulas and solver configs.

Workers start with the "spawn" method on every platform: a worker then never inherits the state of this
process's threads, e.g. locks held by numba or polars, and a run behaves the same on Linux, macOS and Windows.
"""

import importlib
import multiprocessing
import os
import sys
from collections.abc import Hashable, Iterator, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Self, TypeVar

import polars as pl

from sunnbear._core.functions.core import TestFunction
from sunnbear._core.solvers.core import SolverConfig

from .task import BenchmarkTask

K = TypeVar("K", bound=Hashable)

_MAIN_MODULE_NAME = "__main__"


# ==================================================================================================
#  BenchmarkWorkerPool
# ==================================================================================================
class BenchmarkWorkerPool:
    """`BenchmarkWorkerPool` runs benchmark tasks in `n_workers` worker processes, or in this process for 1 worker."""

    def __init__(self, *, n_workers: int, module_names: Sequence[str]) -> None:
        """Hold the worker count and the names of the modules to import in each worker before its first task.

        `module_names` exists because a task looks up its formula and solver configs by id, and a registry only
        holds the classes of imported modules. A new worker has imported only sunnbear, so it imports
        `module_names` to register the formulas and solver configs defined elsewhere.

        Raises:
            ValueError: If `n_workers` is below 1.
        """
        if n_workers < 1:
            raise ValueError(f"n_workers must be at least 1 (got {n_workers}).")
        self.n_workers = n_workers
        self.module_names = tuple(module_names)

    @classmethod
    def for_run(
        cls,
        *,
        n_workers: int | None,
        solver_configs: Sequence[SolverConfig],
        functions: Sequence[TestFunction],
    ) -> Self:
        """Return a run's pool, whose workers import the modules that define the run's solver configs and formulas.

        An `n_workers` of ``None`` starts 1 worker per CPU.

        Raises:
            ValueError: If `n_workers` is below 1, or is above 1 while a formula or solver config is defined in
                an interactive session, because a worker cannot import a definition from an interactive session.
        """
        n_workers = n_workers if n_workers is not None else (os.cpu_count() or 1)
        module_names = {type(config).__module__ for config in solver_configs}
        module_names |= {type(function.formula).__module__ for function in functions}
        if (
            n_workers > 1
            and _MAIN_MODULE_NAME in module_names
            and not hasattr(sys.modules[_MAIN_MODULE_NAME], "__file__")
        ):
            raise ValueError(
                "A worker process cannot import a formula or solver config that is defined in an interactive session; "
                "define the formula or solver config in a module, or pass n_workers=1."
            )
        # The main module is left out of the import list: with "spawn", every worker already runs the main script,
        # which defines its formulas and solver configs.
        return cls(n_workers=n_workers, module_names=sorted(module_names - {_MAIN_MODULE_NAME}))

    # --------------------------------------------------------------------------
    #  Main API
    # --------------------------------------------------------------------------
    def run(self, tasks: Mapping[K, BenchmarkTask]) -> Iterator[tuple[K, pl.DataFrame]]:
        """Run every task and yield each task's key with its result rows, as the task finishes.

        The tasks run in up to `n_workers` worker processes and finish in any order. With 1 worker, they run in
        this process, in the order of `tasks`.

        When a task fails:

        - the tasks that have not started are canceled;
        - the running tasks are awaited;
        - the failed task's exception is raised.
        """
        if not tasks:
            return
        elif self.n_workers == 1:
            for key, task in tasks.items():
                yield key, task.run()
        else:
            executor = ProcessPoolExecutor(
                max_workers=min(self.n_workers, len(tasks)),
                mp_context=multiprocessing.get_context("spawn"),
                initializer=self._import_modules,
                initargs=(self.module_names,),
            )
            try:
                keys_by_future = {executor.submit(task.run): key for key, task in tasks.items()}
                for future in as_completed(keys_by_future):
                    yield keys_by_future[future], future.result()
            finally:
                executor.shutdown(wait=True, cancel_futures=True)

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _import_modules(module_names: Sequence[str]) -> None:
        """Import every module in `module_names`, which registers the formulas and solver configs they define."""
        for module_name in module_names:
            importlib.import_module(module_name)
