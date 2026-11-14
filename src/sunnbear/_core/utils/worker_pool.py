"""`WorkerPool` runs tasks in worker processes, or in this process when it has 1 worker.

A task is any picklable object with a `run` method (`WorkerTask`). A pool may also give each worker a function, its
worker initializer, to run before its first task.

Workers start with the "spawn" method on every platform: a worker then never inherits the state of this
process's threads, e.g. locks held by numba or polars, and a pool behaves the same on Linux, macOS and Windows.
"""

import math
import multiprocessing
import os
from collections.abc import Callable, Hashable, Iterator, Mapping, Sequence
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

    def __init__(self, *, n_workers: int | None, worker_initializer: Callable[[], object] | None = None) -> None:
        """Hold the worker count and the function that each worker runs before its first task.

        Args:
            n_workers: The number of worker processes; ``None`` for 1 per logical CPU.
            worker_initializer: A picklable function that each worker process calls once, before its first task;
                ``None`` for none. With 1 worker, the tasks run in this process, which never calls the worker
                initializer.

        Raises:
            ValueError: If `n_workers` is below 1.
        """
        n_workers = n_workers if n_workers is not None else (os.cpu_count() or 1)
        if n_workers < 1:
            raise ValueError(f"n_workers must be at least 1 (got {n_workers}).")
        self.n_workers = n_workers
        self.worker_initializer = worker_initializer
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
                initializer=self.worker_initializer,
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

    def split_into_batches[T](
        self, items: Sequence[T], *, group_key: Callable[[T], Hashable], max_batch_size: int | None = None
    ) -> list[list[T]]:
        """Split `items` into batches of a limited size, keeping the items of 1 key together where they fit.

        The items with the same key form a group. A batch keeps a group together when the group fits in 1 batch, so a
        group's shared work, such as compiling a function, mostly happens once per group. The batches are filled as
        follows:

        - a batch holds at most the default maximum of `ceil(len(items) / (TARGET_BATCHES_PER_WORKER * n_workers))`
          items, or at most `max_batch_size` items when that is given and smaller;
        - the groups fill the batches in order of first appearance, and the items keep their order within a group;
        - a batch takes the next group as long as the batch then holds at most its maximum size;
        - a group larger than a batch's maximum size is split into consecutive batches that hold no other group, of
          nearly equal sizes and none above that maximum. A large group then runs in several workers.

        Args:
            items: The items to split.
            group_key: Returns the key of an item's group.
            max_batch_size: The largest number of items in a batch, or ``None`` to use the default maximum alone. Set
                it for items that take so long that a batch of the default maximum size would keep 1 worker busy long
                after the others finish.

        Raises:
            ValueError: If `max_batch_size` is below 1.
        """
        if max_batch_size is not None and max_batch_size < 1:
            raise ValueError(f"max_batch_size must be at least 1 (got {max_batch_size}).")
        groups: dict[Hashable, list[T]] = {}
        for item in items:
            groups.setdefault(group_key(item), []).append(item)
        effective_max_batch_size = math.ceil(len(items) / (TARGET_BATCHES_PER_WORKER * self.n_workers))
        if max_batch_size is not None:
            effective_max_batch_size = min(effective_max_batch_size, max_batch_size)
        batches: list[list[T]] = []
        batch: list[T] = []
        for group in groups.values():
            if batch and len(batch) + len(group) > effective_max_batch_size:
                batches.append(batch)
                batch = []
            if len(group) > effective_max_batch_size:
                n_group_batches = math.ceil(len(group) / effective_max_batch_size)
                group_batch_size = math.ceil(len(group) / n_group_batches)
                batches.extend(
                    group[start : start + group_batch_size] for start in range(0, len(group), group_batch_size)
                )
            else:
                batch.extend(group)
        if batch:
            batches.append(batch)
        return batches


# ==================================================================================================
#  WorkerTask
# ==================================================================================================
class WorkerTask[R](Protocol):
    """A `WorkerTask` is a picklable object whose `run` method computes the task's result."""

    def run(self) -> R:
        """Return the task's result."""
        ...
