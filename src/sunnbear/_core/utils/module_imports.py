"""`worker_pool_for_modules` returns a `WorkerPool` whose workers first import the modules that the tasks need.

A task may look up a class by id in a registry, such as the class of a formula or a solver config, and a registry holds
only the classes of the modules that its process has imported.

A new worker process has imported only what unpickling its first task needs, so each worker of the pool first imports
the modules that define the classes that the tasks look up.
"""

import functools
import importlib
import sys
from collections.abc import Collection, Sequence

from .worker_pool import WorkerPool


def worker_pool_for_modules(*, n_workers: int | None, module_names: Collection[str]) -> WorkerPool:
    """Return a `WorkerPool` with `n_workers` workers, each of which imports the modules in `module_names` first.

    An `n_workers` of ``None`` gives 1 worker per logical CPU.

    The main module is left out of the modules to import: a `WorkerPool` starts its workers with "spawn", so every
    worker runs the main script again, which defines the script's classes in that worker.

    A class defined in an interactive session has no module file that a worker could import, so a `__main__` module
    of an interactive session allows only 1 worker.

    Raises:
        ValueError: If `n_workers` is below 1, or the pool has more than 1 worker while `module_names` holds the
            `__main__` module of an interactive session.
    """
    worker_pool = WorkerPool(
        n_workers=n_workers,
        worker_initializer=functools.partial(import_modules, sorted(set(module_names) - {"__main__"})),
    )
    if worker_pool.n_workers > 1 and "__main__" in module_names and not hasattr(sys.modules["__main__"], "__file__"):
        raise ValueError(
            "A worker process cannot import a class that is defined in an interactive session; "
            "define the class in a module, or pass n_workers=1."
        )
    else:
        return worker_pool


def import_modules(module_names: Sequence[str]) -> None:
    """Import every module in `module_names`, which registers the classes that they define."""
    for module_name in module_names:
        importlib.import_module(module_name)
