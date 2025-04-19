import random
import string
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import NamedTuple

REPO_DIR = Path(__file__).parents[1]
SCRIPT_PATH = REPO_DIR / "collect_files.sh"


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


def run_script(input_dir: Path, output_dir: Path, max_depth: int | None) -> None:
    from scripts.collect_files import collect_files

    args = [str(SCRIPT_PATH), str(input_dir), str(output_dir)]
    if max_depth is not None:
        args.append("--max_depth")
        args.append(str(max_depth))
    collect_files(input_dir, output_dir, max_depth)


class FileData(NamedTuple):
    path: Path
    depth: int


def get_all_files_info(root_dir: str | Path) -> list[FileData]:
    result: list[FileData] = []
    root_path = Path(root_dir).resolve()
    for p in root_path.rglob("*"):
        if p.is_file():
            depth = len(p.relative_to(root_path).parents)
            result.append(FileData(path=p, depth=depth))
    return result


def _check_non_unique_files(expected_fnames: list[str], copied_fnames: list[str]) -> None:
    fnames_counter = Counter(expected_fnames)
    unique_expected_fnames = [f for f, count in fnames_counter.items() if count == 1]
    assert not set(unique_expected_fnames) - set(copied_fnames)
    non_unique_expected_files = [f for f, count in fnames_counter.items() if count > 1]
    for fname in copied_fnames:
        if fname in unique_expected_fnames:
            continue
        assert any(f.startswith(fname) for f in non_unique_expected_files)


def _check_max_depth_files(expected_files: list[FileData], copied_files: list[FileData], depth: int) -> None:
    depth_to_expected_fnames: dict[int, set[str]] = defaultdict(set)
    for f in expected_files:
        expected_depth = min(f.depth, depth)
        depth_to_expected_fnames[expected_depth].add(f.path.name)
    depth_to_copied_fnames: dict[int, set[str]] = defaultdict(set)
    for f in copied_files:
        depth_to_copied_fnames[f.depth].add(f.path.name)
    assert depth_to_expected_fnames == depth_to_copied_fnames


def _test_collect_files(
    depth: int,
    num_unique_files: int | None = None,
    max_depth: int | None = None,
) -> None:
    assert not all([num_unique_files is not None, max_depth is not None])
    for i in range(1, 6):
        with tempfile.TemporaryDirectory() as input_tmp, tempfile.TemporaryDirectory() as output_tmp:
            input_dir, output_dir = Path(input_tmp), Path(output_tmp)
            create_test_structure(
                input_dir, depth=depth, files_per_dir=i, dirs_per_dir=i, num_unique_names=num_unique_files
            )
            expected_files = get_all_files_info(input_dir)
            expected_fnames = [f.path.name for f in expected_files]

            run_script(input_dir, output_dir, max_depth=max_depth)
            copied_files = get_all_files_info(output_dir)
            copied_fnames = [f.path.name for f in expected_files]

            if max_depth is not None:
                _check_max_depth_files(expected_files, copied_files, depth=max_depth)
            elif num_unique_files is not None:
                _check_non_unique_files(expected_fnames, copied_fnames)
            else:
                assert {p.path.name for p in expected_files} == {p.path.name for p in copied_files}


class NameGenerator:
    MAX_ITERS = 10**5

    def __init__(self, always_unique: bool = True, max_unique: int | None = None, random_state: int = 42) -> None:
        self.rng = random.Random(random_state)
        self._used_names: set[str] = set()
        self._prepared_names: list[str] | None = None
        self.always_unique = always_unique

        if always_unique and max_unique:
            raise ValueError

        if max_unique is None:
            return

        name_set: set[str] = set()
        for _ in range(self.MAX_ITERS):
            if len(name_set) == max_unique:
                self._prepared_names = list(name_set)
                return
            name_set.add(random_filename(self.rng))
        raise ValueError(f"Didn't generate enough unique names in {self.MAX_ITERS} iterations")

    def get_name(self) -> str:
        if self.always_unique:
            for _ in range(self.MAX_ITERS):
                name = random_filename(self.rng)
                if name not in self._used_names:
                    self._used_names.add(name)
                    return name
            raise ValueError(f"Didn't generate new unique name in {self.MAX_ITERS} iterations")

        if self._prepared_names is not None:
            return self.rng.choice(self._prepared_names)

        return random_filename(self.rng)


def random_filename(rng: random.Random, name_len: int = 10, extension: str = ".txt") -> str:
    name = "".join(rng.choices(string.ascii_letters + string.digits, k=name_len))
    return f"{name}{extension}"


def create_test_structure(
    base_dir: Path,
    depth: int = 3,
    files_per_dir: int = 2,
    dirs_per_dir: int = 2,
    current_depth: int = 0,
    num_unique_names: int | None = None,
    unique_names: list[str] | None = None,
    _name_gen: NameGenerator | None = None,
) -> None:
    if current_depth >= depth:
        return

    if _name_gen is None:
        _name_gen = NameGenerator(max_unique=num_unique_names, always_unique=num_unique_names is None)

    for _ in range(files_per_dir):
        file_path = base_dir / _name_gen.get_name()
        with open(file_path, "w") as f:
            f.write(f"Test content at depth {current_depth}\n")

    for i in range(dirs_per_dir):
        dir_name = f"dir_{current_depth}_{i}"
        new_dir_path = base_dir / dir_name
        new_dir_path.mkdir(exist_ok=True)
        create_test_structure(
            new_dir_path,
            depth=depth,
            files_per_dir=files_per_dir,
            dirs_per_dir=dirs_per_dir,
            current_depth=current_depth + 1,
            unique_names=unique_names,
            _name_gen=_name_gen,
        )
