import tempfile
from pathlib import Path

from tests.utils import _test_collect_files, run_script


def test_script_runs_and_accepts_two_args() -> None:
    with tempfile.TemporaryDirectory() as input_tmp, tempfile.TemporaryDirectory() as output_tmp:
        input_dir, output_dir = Path(input_tmp), Path(output_tmp)
        run_script(input_dir, output_dir, max_depth=None)


def test_collect_files_depth_2() -> None:
    _test_collect_files(depth=2)


def test_collect_files_deep() -> None:
    for depth in range(3, 6):
        _test_collect_files(depth=depth)


def test_collect_files_non_unique() -> None:
    for depth in range(3, 6):
        _test_collect_files(depth=depth, num_unique_files=5)


def test_collect_files_max_depth() -> None:
    for depth in range(3, 6):
        for max_depth in range(2, 4):
            _test_collect_files(depth=depth, max_depth=max_depth)
