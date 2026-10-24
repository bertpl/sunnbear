"""`WorkerPool` runs tasks in worker processes, or in this process when it has 1 worker.

A task is any picklable object with a `run` method (`WorkerTask`).

A task may look up a class by id in a registry, such as the class of a formula or a solver config, and a registry holds
only the classes of the modules that its process has imported.

A new worker has imported only what unpickling its first task needs, so every worker first imports the pool's
`module_names`.

Workers start with the "spawn" method on every platform: a worker then never inherits the state of this
process's threads, e.g. locks held by numba or polars, and a pool behaves the same on Linux, macOS and Windows.
"""

import importlib
import math
import multiprocessing
import os
import sys
from collections.abc import Callable, Collection, Hashable, Iterator, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
from typing import Protocol, Self

# `WorkerPool.split_into_batches` aims at this many batches per worker, each run as 1 task, so that a slow task does
# not leave the other workers idle at the end.
TARGET_BATCHES_PER_WORKER = 4


# ==================================================================================================
#  WorkerPool
# ==================================================================================================
class WorkerPool:
    """`WorkerPool` runs tasks in `n_workers` worker processes, or in this process for 1 worker.

    A pool with more than 1 worker runs tasks only inside a ``with`` block:

    - its workers start when the first tasks run;
    - every call of `run` inside the block shares them;
    - the block's end stops them.

    A caller that calls `run` several times inside 1 ``with`` block therefore starts the pool's workers once.
    """

    def __init__(self, *, n_workers: int, module_names: Sequence[str]) -> None:
        """Hold the worker count and the names of the modules to import in each worker before its first task.

        Raises:
            ValueError: If `n_workers` is below 1.
        """
        if n_workers < 1:
            raise ValueError(f"n_workers must be at least 1 (got {n_workers}).")
        self.n_workers = n_workers
        self.module_names = tuple(module_names)
        self._executor: ProcessPoolExecutor | None = None

    # --------------------------------------------------------------------------
    #  Context manager
    # --------------------------------------------------------------------------
    def __enter__(self) -> Self:
        """Prepare the workers of a pool with more than 1 worker, and return the pool."""
        if self.n_workers > 1:
            # An executor on the "spawn" start method starts no process here: it starts a worker process when a task
            # is submitted and no worker is idle, up to `max_workers`.
            self._executor = ProcessPoolExecutor(
                max_workers=self.n_workers,
                mp_context=multiprocessing.get_context("spawn"),
                initializer=self._import_modules,
                initargs=(self.module_names,),
            )
        return self

    def __exit__(self, *exc_info: object) -> None:
        """Stop the workers, after canceling the tasks that have not started and awaiting the running ones."""
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=True)
            self._executor = None

    # --------------------------------------------------------------------------
    #  Main API
    # --------------------------------------------------------------------------
    def run[K: Hashable, R](self, tasks: Mapping[K, "WorkerTask[R]"]) -> Iterator[tuple[K, R]]:
        """Run every task and yield each task's key with its result, as the task finishes.

        The tasks run in up to `n_workers` worker processes and finish in any order. With 1 worker, they run in
        this process, in the order of `tasks`.

        When a task fails:

        - the tasks that have not started are canceled;
        - the running tasks are awaited;
        - the failed task's exception is raised.

        Raises:
            RuntimeError: If the pool has more than 1 worker and its ``with`` block is not open.
        """
        if not tasks:
            return
        elif self.n_workers == 1:
            for key, task in tasks.items():
                yield key, task.run()
        elif self._executor is None:
            raise RuntimeError("A WorkerPool with more than 1 worker runs tasks only inside its with block.")
        else:
            keys_by_future = {self._executor.submit(task.run): key for key, task in tasks.items()}
            try:
                for future in as_completed(keys_by_future):
                    yield keys_by_future[future], future.result()
            finally:
                for future in keys_by_future:
                    future.cancel()
                wait(keys_by_future)

    def split_into_batches[T](self, items: Sequence[T], *, group_key: Callable[[T], Hashable]) -> list[list[T]]:
        """Split `items` into about `TARGET_BATCHES_PER_WORKER` batches per worker, keeping the items of 1 key together.

        The items with the same key form a group, which no batch splits, so work that a group's items share, such as
        compiling a function, happens once per group. The batches are filled as follows:

        - the groups fill the batches in order of first appearance, and the items keep their order within a group;
        - a batch takes the next group as long as the batch then holds at most
          `ceil(len(items) / (TARGET_BATCHES_PER_WORKER * n_workers))` items; a group larger than that maximum forms a
          batch of its own.
        """
        groups: dict[Hashable, list[T]] = {}
        for item in items:
            groups.setdefault(group_key(item), []).append(item)
        max_batch_size = math.ceil(len(items) / (TARGET_BATCHES_PER_WORKER * self.n_workers))
        batches: list[list[T]] = []
        batch: list[T] = []
        for group in groups.values():
            if batch and len(batch) + len(group) > max_batch_size:
                batches.append(batch)
                batch = []
            batch.extend(group)
        if batch:
            batches.append(batch)
        return batches

    # --------------------------------------------------------------------------
    #  Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def _import_modules(module_names: Sequence[str]) -> None:
        """Import every module in `module_names`, which registers the classes that they define."""
        for module_name in module_names:
            importlib.import_module(module_name)

    # --------------------------------------------------------------------------
    #  Factory methods
    # --------------------------------------------------------------------------
    @classmethod
    def for_modules(cls, *, n_workers: int | None, module_names: Collection[str]) -> Self:
        """Return a pool whose workers import `module_names`, with 1 worker per CPU for an `n_workers` of ``None``.

        The main module is left out of the modules to import: with "spawn", every worker runs the main script again,
        which defines the script's classes in that worker.

        A class defined in an interactive session has no module file that a worker could import, so a `__main__`
        module of an interactive session allows only 1 worker.

        Raises:
            ValueError: If `n_workers` is below 1, or is above 1 while `module_names` holds the `__main__` module
                of an interactive session.
        """
        n_workers = n_workers if n_workers is not None else (os.cpu_count() or 1)
        if n_workers > 1 and "__main__" in module_names and not hasattr(sys.modules["__main__"], "__file__"):
            raise ValueError(
                "A worker process cannot import a class that is defined in an interactive session; "
                "define the class in a module, or pass n_workers=1."
            )
        return cls(n_workers=n_workers, module_names=sorted(set(module_names) - {"__main__"}))


# ==================================================================================================
#  WorkerTask
# ==================================================================================================
class WorkerTask[R](Protocol):
    """A `WorkerTask` is a picklable object whose `run` method computes the task's result."""

    def run(self) -> R:
        """Return the task's result."""
        ...
