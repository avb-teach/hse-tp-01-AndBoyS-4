import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import NamedTuple

from scripts.create_test_data import create_test_structure

REPO_DIR = Path(__file__).parents[1]
SCRIPT_PATH = REPO_DIR / "collect_files.sh"


# def run_script(input_dir: Path, output_dir: Path, max_depth: int | None) -> None:
#     from scripts.collect_files import collect_files

#     args = [str(SCRIPT_PATH), str(input_dir), str(output_dir)]
#     if max_depth is not None:
#         args.append("--max_depth")
#         args.append(str(max_depth))
#     collect_files(input_dir, output_dir, max_depth)


# class FileData(NamedTuple):
#     path: Path
#     depth: int


# def get_all_files_info(root_dir: str | Path) -> list[FileData]:
#     result: list[FileData] = []
#     root_path = Path(root_dir).resolve()
#     for p in root_path.rglob("*"):
#         if p.is_file():
#             depth = len(p.relative_to(root_path).parents)
#             result.append(FileData(path=p, depth=depth))
#     return result


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


# def _test_collect_files(
#     depth: int,
#     num_unique_files: int | None = None,
#     max_depth: int | None = None,
# ) -> None:
#     assert not all([num_unique_files is not None, max_depth is not None])
#     for i in range(1, 6):
#         with tempfile.TemporaryDirectory() as input_tmp, tempfile.TemporaryDirectory() as output_tmp:
#             input_dir, output_dir = Path(input_tmp), Path(output_tmp)
#             create_test_structure(
#                 input_dir, depth=depth, files_per_dir=i, dirs_per_dir=i, num_unique_names=num_unique_files
#             )
#             expected_files = get_all_files_info(input_dir)
#             expected_fnames = [f.path.name for f in expected_files]

#             run_script(input_dir, output_dir, max_depth=max_depth)
#             copied_files = get_all_files_info(output_dir)
#             copied_fnames = [f.path.name for f in expected_files]

#             if max_depth is not None:
#                 _check_max_depth_files(expected_files, copied_files, depth=max_depth)
#             elif num_unique_files is not None:
#                 _check_non_unique_files(expected_fnames, copied_fnames)
#             else:
#                 assert {p.path.name for p in expected_files} == {p.path.name for p in copied_files}


# def _check_non_unique_files(expected_fnames: list[str], copied_fnames: list[str]) -> None:
#     fnames_counter = Counter(expected_fnames)
#     unique_expected_fnames = [f for f, count in fnames_counter.items() if count == 1]
#     assert not set(unique_expected_fnames) - set(copied_fnames)
#     non_unique_expected_files = [f for f, count in fnames_counter.items() if count > 1]
#     for fname in copied_fnames:
#         if fname in unique_expected_fnames:
#             continue
#         assert any(f.startswith(fname) for f in non_unique_expected_files)


# def _check_max_depth_files(expected_files: list[FileData], copied_files: list[FileData], depth: int) -> None:
#     depth_to_expected_fnames: dict[int, set[str]] = defaultdict(set)
#     for f in expected_files:
#         expected_depth = min(f.depth, depth)
#         depth_to_expected_fnames[expected_depth].add(f.path.name)
#     depth_to_copied_fnames: dict[int, set[str]] = defaultdict(set)
#     for f in copied_files:
#         depth_to_copied_fnames[f.depth].add(f.path.name)
#     assert depth_to_expected_fnames == depth_to_copied_fnames
