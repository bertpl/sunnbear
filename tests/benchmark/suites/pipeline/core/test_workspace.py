"""`PipelineWorkspace` replaces the files of an earlier run's build details, and reads the files back."""

from sunnbear._core.benchmark.suites.pipeline.core import PipelineWorkspace


def test_the_build_details_files_replace_those_of_an_earlier_run_and_read_back(tmp_path):
    """After a run with 2 files, a run with 1 of them leaves only that file, with its new content, and the workspace
    reads it back."""
    # --- arrange ----------------------
    workspace = PipelineWorkspace(tmp_path)
    workspace.write_build_details_files({"run.json": b"first\n", "edis.parquet": b"first edis"})

    # --- act --------------------------
    workspace.write_build_details_files({"run.json": b"second\n"})

    # --- assert -----------------------
    assert workspace.read_build_details_files() == {"run.json": b"second\n"}
