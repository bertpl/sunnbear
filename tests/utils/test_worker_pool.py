"""`WorkerPool` runs tasks in this process for 1 worker, or in worker processes that start when the first tasks run and
serve every later call of `run` in the same with block; it splits items into batches without splitting the items that
share a key.
"""

import multiprocessing
import os
import sys
import types
from dataclasses import dataclass

import pytest

from sunnbear._core.utils.worker_pool import WorkerPool

_IMPORTED_MODULE_NAME = f"{__name__.rpartition('.')[0]}.worker_pool_imported_module"


# ==================================================================================================
#  Tasks
# ==================================================================================================
@dataclass(frozen=True)
class ProcessIdTask:
    """`ProcessIdTask` returns the id of the process that runs it."""

    def run(self) -> int:
        return os.getpid()


@dataclass(frozen=True)
class FailingTask:
    """`FailingTask` raises a `ValueError`."""

    def run(self) -> None:
        raise ValueError("the task failed")


@dataclass(frozen=True)
class IsModuleImportedTask:
    """`IsModuleImportedTask` returns whether the process that runs it has imported `module_name`."""

    module_name: str

    def run(self) -> bool:
        return self.module_name in sys.modules


# ==================================================================================================
#  Running tasks
# ==================================================================================================
def test_a_pool_with_1_worker_runs_the_tasks_in_this_process_in_order():
    """With 1 worker, the tasks run in this process, in the order of the mapping, with or without a with block."""
    # --- arrange ----------------------
    worker_pool = WorkerPool(n_workers=1, module_names=[])

    # --- act --------------------------
    results = list(worker_pool.run({"b": ProcessIdTask(), "a": ProcessIdTask()}))

    # --- assert -----------------------
    assert results == [("b", os.getpid()), ("a", os.getpid())]


def test_a_pool_with_workers_runs_the_tasks_in_worker_processes_that_its_runs_share():
    """With 2 workers, each task's key comes with its result, and 2 calls of `run` in 1 with block use at most 2
    processes."""
    # --- act --------------------------
    with WorkerPool(n_workers=2, module_names=[]) as worker_pool:
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
    with WorkerPool(n_workers=2, module_names=[]) as worker_pool:
        assert not multiprocessing.active_children()
        list(worker_pool.run({0: ProcessIdTask()}))
        assert multiprocessing.active_children()
    assert not multiprocessing.active_children()


@pytest.mark.parametrize("module_names, is_imported_expected", [([], False), ([_IMPORTED_MODULE_NAME], True)])
def test_each_worker_imports_the_named_modules(module_names, is_imported_expected):
    """A worker imports the modules that the pool names before its first task; a worker of a pool that names none
    lacks the module."""
    # --- act --------------------------
    with WorkerPool(n_workers=2, module_names=module_names) as worker_pool:
        [(_, is_imported)] = list(worker_pool.run({0: IsModuleImportedTask(_IMPORTED_MODULE_NAME)}))

    # --- assert -----------------------
    assert is_imported == is_imported_expected


@pytest.mark.parametrize("n_workers", [1, 2])
def test_a_failing_task_raises_its_exception(n_workers):
    """The exception of a failing task is raised from `run`, in this process or in a worker."""
    # --- act / assert -----------------
    with WorkerPool(n_workers=n_workers, module_names=[]) as worker_pool, pytest.raises(ValueError, match="failed"):
        list(worker_pool.run({0: ProcessIdTask(), 1: FailingTask()}))


def test_a_pool_with_workers_runs_no_task_outside_its_with_block():
    """A pool with 2 workers raises `RuntimeError` when it runs tasks outside its with block."""
    # --- arrange ----------------------
    worker_pool = WorkerPool(n_workers=2, module_names=[])

    # --- act / assert -----------------
    with pytest.raises(RuntimeError, match="inside its with block"):
        list(worker_pool.run({0: ProcessIdTask()}))


def test_importing_the_modules_registers_their_classes():
    """`_import_modules`, which each worker runs first, imports every named module."""
    # --- act --------------------------
    WorkerPool._import_modules([_IMPORTED_MODULE_NAME])

    # --- assert -----------------------
    assert _IMPORTED_MODULE_NAME in sys.modules


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
    """`split_into_batches` keeps the items that share a first letter in 1 batch, in about `BATCHES_PER_WORKER` batches
    per worker."""
    # --- arrange ----------------------
    worker_pool = WorkerPool(n_workers=n_workers, module_names=[])

    # --- act --------------------------
    batches = worker_pool.split_into_batches(items, key=lambda item: item[0])

    # --- assert -----------------------
    assert batches == batches_expected


# ==================================================================================================
#  for_modules
# ==================================================================================================
def test_a_pool_for_modules_has_1_worker_per_cpu_by_default_and_leaves_out_the_main_module(monkeypatch):
    """An `n_workers` of None gives 1 worker per CPU; the main module of a script is not among the modules to import."""
    # --- arrange ----------------------
    script_main_module = types.ModuleType("__main__")
    script_main_module.__file__ = "script.py"
    monkeypatch.setitem(sys.modules, "__main__", script_main_module)

    # --- act --------------------------
    worker_pool = WorkerPool.for_modules(n_workers=None, module_names={"__main__", "b_module", "a_module"})

    # --- assert -----------------------
    assert worker_pool.n_workers == (os.cpu_count() or 1)
    assert worker_pool.module_names == ("a_module", "b_module")


def test_a_pool_with_workers_refuses_a_main_module_of_an_interactive_session(monkeypatch):
    """A `__main__` module without a file cannot be imported by a worker, so only 1 worker is allowed."""
    # --- arrange ----------------------
    monkeypatch.setitem(sys.modules, "__main__", types.ModuleType("__main__"))

    # --- act / assert -----------------
    WorkerPool.for_modules(n_workers=1, module_names={"__main__"})
    with pytest.raises(ValueError, match="defined in an interactive session"):
        WorkerPool.for_modules(n_workers=2, module_names={"__main__"})


def test_a_pool_refuses_fewer_than_1_worker():
    """An `n_workers` below 1 raises `ValueError`."""
    # --- act / assert -----------------
    with pytest.raises(ValueError, match="n_workers must be at least 1"):
        WorkerPool(n_workers=0, module_names=[])
