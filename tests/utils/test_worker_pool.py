"""`WorkerPool` runs tasks in this process for 1 worker, and splits items into batches without splitting the items
that share a key.

With 2 or more workers, the tasks run in worker processes that:

- start when the first tasks run;
- run the pool's worker initializer before their first task;
- serve every later call of `run` in the same with block.
"""

import multiprocessing
import os
from dataclasses import dataclass

import pytest

from sunnbear._core.utils.worker_pool import WorkerPool


# ==================================================================================================
#  Tasks
# ==================================================================================================
@dataclass(frozen=True)
class ProcessIdTask:
    """`ProcessIdTask` returns the id of the process that runs it."""

    def run(self) -> int:
        """Return the id of this process."""
        return os.getpid()


@dataclass(frozen=True)
class FailingTask:
    """`FailingTask` raises a `ValueError`."""

    def run(self) -> None:
        """Raise a `ValueError`."""
        raise ValueError("the task failed")


@dataclass(frozen=True)
class IsWorkerInitializedTask:
    """`IsWorkerInitializedTask` returns whether a worker initializer has marked its process as initialized."""

    def run(self) -> bool:
        """Return whether `mark_initialized` has run in this process."""
        return _WORKER_STATE["is_initialized"]


# ==================================================================================================
#  Helpers
# ==================================================================================================
# `mark_initialized` sets `is_initialized` to True in each worker process that calls `mark_initialized` as its worker
# initializer.
_WORKER_STATE = {"is_initialized": False}


def mark_initialized() -> None:
    """Mark the calling process as initialized, in `_WORKER_STATE`."""
    _WORKER_STATE["is_initialized"] = True


# ==================================================================================================
#  Running tasks
# ==================================================================================================
def test_a_pool_with_1_worker_runs_the_tasks_in_this_process_in_order():
    """With 1 worker, the tasks run in this process, in the order of the mapping, with or without a with block."""
    # --- arrange ----------------------
    worker_pool = WorkerPool(n_workers=1)

    # --- act --------------------------
    results = list(worker_pool.run({"b": ProcessIdTask(), "a": ProcessIdTask()}))

    # --- assert -----------------------
    assert results == [("b", os.getpid()), ("a", os.getpid())]


def test_a_pool_with_workers_runs_the_tasks_in_worker_processes_that_its_runs_share():
    """With 2 workers, each task's key comes with its result, and 2 calls of `run` in 1 with block use at most 2
    processes."""
    # --- act --------------------------
    with WorkerPool(n_workers=2) as worker_pool:
        first_process_ids = dict(worker_pool.run({key: ProcessIdTask() for key in range(4)}))
        second_process_ids = dict(worker_pool.run({key: ProcessIdTask() for key in range(4, 8)}))

    # --- assert -----------------------
    assert sorted(first_process_ids | second_process_ids) == list(range(8))
    worker_process_ids = set(first_process_ids.values()) | set(second_process_ids.values())
    assert os.getpid() not in worker_process_ids
    assert len(worker_process_ids) <= 2


def test_workers_start_with_the_first_tasks_and_stop_at_the_end_of_the_with_block():
    """No worker process exists before the first tasks run, and none remains after the with block."""
    # --- act / assert -----------------
    with WorkerPool(n_workers=2) as worker_pool:
        assert not multiprocessing.active_children()
        list(worker_pool.run({0: ProcessIdTask()}))
        assert multiprocessing.active_children()
    assert not multiprocessing.active_children()


@pytest.mark.parametrize("worker_initializer, is_initialized_expected", [(None, False), (mark_initialized, True)])
def test_each_worker_runs_the_worker_initializer_before_its_first_task(worker_initializer, is_initialized_expected):
    """A worker runs the pool's worker initializer before its first task; a worker of a pool without one does not."""
    # --- act --------------------------
    with WorkerPool(n_workers=2, worker_initializer=worker_initializer) as worker_pool:
        [(_, is_initialized)] = list(worker_pool.run({0: IsWorkerInitializedTask()}))

    # --- assert -----------------------
    assert is_initialized == is_initialized_expected


@pytest.mark.parametrize("n_workers", [1, 2])
def test_a_failing_task_raises_its_exception(n_workers):
    """The exception of a failing task is raised from `run`, in this process or in a worker."""
    # --- act / assert -----------------
    with WorkerPool(n_workers=n_workers) as worker_pool, pytest.raises(ValueError, match="failed"):
        list(worker_pool.run({0: ProcessIdTask(), 1: FailingTask()}))


def test_a_pool_with_workers_runs_no_task_outside_its_with_block():
    """A pool with 2 workers raises `RuntimeError` when it runs tasks outside its with block."""
    # --- arrange ----------------------
    worker_pool = WorkerPool(n_workers=2)

    # --- act / assert -----------------
    with pytest.raises(RuntimeError, match="inside its with block"):
        list(worker_pool.run({0: ProcessIdTask()}))


# ==================================================================================================
#  Splitting into batches
# ==================================================================================================
@pytest.mark.parametrize(
    "items, n_workers, batches_expected",
    [
        # With 1 worker, the 8 groups of 1 item fill 4 batches of 2 items.
        (["a", "b", "c", "d", "e", "f", "g", "h"], 1, [["a", "b"], ["c", "d"], ["e", "f"], ["g", "h"]]),
        # With 2 workers, the 8 items fill 8 batches of 1 item.
        (["a", "b", "c", "d", "e", "f", "g", "h"], 2, [["a"], ["b"], ["c"], ["d"], ["e"], ["f"], ["g"], ["h"]]),
        # A group larger than a batch's maximum of 2 items forms a batch of its own, and no batch splits a group.
        (["a1", "a2", "a3", "b1", "c1", "c2"], 1, [["a1", "a2", "a3"], ["b1"], ["c1", "c2"]]),
        # The groups keep their order of first appearance, and the items keep their order within a group.
        (["b1", "a1", "b2"], 1, [["b1", "b2"], ["a1"]]),
        ([], 1, []),
    ],
)
def test_items_are_split_into_batches_of_whole_groups(items, n_workers, batches_expected):
    """`split_into_batches` keeps the items that share a first letter in 1 batch, in about `TARGET_BATCHES_PER_WORKER`
    batches per worker."""
    # --- arrange ----------------------
    worker_pool = WorkerPool(n_workers=n_workers)

    # --- act --------------------------
    batches = worker_pool.split_into_batches(items, group_key=lambda item: item[0])

    # --- assert -----------------------
    assert batches == batches_expected


# ==================================================================================================
#  Worker count
# ==================================================================================================
def test_a_pool_has_1_worker_per_cpu_by_default():
    """An `n_workers` of None gives 1 worker per logical CPU."""
    # --- act --------------------------
    worker_pool = WorkerPool(n_workers=None)

    # --- assert -----------------------
    assert worker_pool.n_workers == (os.cpu_count() or 1)


def test_a_pool_refuses_fewer_than_1_worker():
    """An `n_workers` below 1 raises `ValueError`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="n_workers must be at least 1"):
        WorkerPool(n_workers=0)
