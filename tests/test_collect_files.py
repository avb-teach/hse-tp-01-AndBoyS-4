import subprocess
import tempfile
from collections import Counter
from collections.abc import Generator
from pathlib import Path

import pytest

from scripts.create_test_data import create_test_structure

REPO_DIR = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip())
SCRIPT_PATH = REPO_DIR / "collect_files.sh"


def run_script(input_dir: Path, output_dir: Path) -> None:
    subprocess.run([str(SCRIPT_PATH), str(input_dir), str(output_dir)], capture_output=True, text=True, check=True)


def get_all_file_names_flat(root_dir: Path) -> list[str]:
    return sorted([f.name for f in root_dir.iterdir() if f.is_file()])


def get_all_file_names_recursive(root_dir: Path) -> list[str]:
    return sorted([f.name for f in root_dir.rglob("*") if f.is_file()])


@pytest.fixture
def temp_dirs() -> Generator[tuple[Path, Path], None, None]:
    with tempfile.TemporaryDirectory() as input_tmp, tempfile.TemporaryDirectory() as output_tmp:
        yield Path(input_tmp), Path(output_tmp)


def test_script_runs_and_accepts_two_args(temp_dirs: tuple[Path, Path]) -> None:
    input_dir, output_dir = temp_dirs
    run_script(input_dir, output_dir)


def test_collect_files_depth_2(temp_dirs: tuple[Path, Path]) -> None:
    _test_collect_files(temp_dirs, depth=2)


def test_collect_files_deep(temp_dirs: tuple[Path, Path]) -> None:
    for depth in range(3, 6):
        _test_collect_files(temp_dirs, depth=depth)


def test_collect_files_non_unique(temp_dirs: tuple[Path, Path]) -> None:
    for depth in range(3, 6):
        _test_collect_files(temp_dirs, depth=depth, num_unique_files=5)


def _test_collect_files(temp_dirs: tuple[Path, Path], depth: int, num_unique_files: int | None = None) -> None:
    input_dir, output_dir = temp_dirs
    for i in range(1, 6):
        create_test_structure(
            input_dir, max_depth=depth, files_per_dir=i, dirs_per_dir=i, num_unique_names=num_unique_files
        )
        expected_files = get_all_file_names_recursive(input_dir)
        run_script(input_dir, output_dir)
        copied_files = get_all_file_names_flat(output_dir)
        if num_unique_files is None:
            assert set(copied_files) == set(expected_files)
        else:
            fnames_counter = Counter(expected_files)
            unique_expected_files = [f for f, count in fnames_counter.items() if count == 1]
            assert not set(unique_expected_files) - set(copied_files)
            non_unique_expected_files = [f for f, count in fnames_counter.items() if count > 1]
            for fname in copied_files:
                if fname in unique_expected_files:
                    continue
                assert any(f.startswith(fname) for f in non_unique_expected_files)
