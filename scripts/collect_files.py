import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple


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


def collect_files(input_dir: Path, output_dir: Path, max_depth: int | None = None) -> None:
    if not input_dir.is_dir():
        print(f"Ошибка: {input_dir} не является директорией.")
        sys.exit(1)

    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()

    output_dir.mkdir(exist_ok=True)
    files = get_all_files_info(input_dir)
    depth_to_files: dict[int, list[FileData]] = defaultdict(list)
    for f in files:
        depth = 1
        if max_depth:
            depth = min(f.depth, max_depth)
        depth_to_files[depth].append(f)

    for depth, cur_files in depth_to_files.items():
        name_counts: dict[str, int] = defaultdict(int)

        orig_path_to_rel: dict[Path, Path] = {}
        for f in cur_files:
            rel_p = f.path.relative_to(input_dir)
            rel_p = Path(*rel_p.parts[-depth:])
            orig_path_to_rel[f.path] = rel_p
            name_counts[rel_p.name] += 1

        for orig_path, rel_path in orig_path_to_rel.items():
            fname = rel_path.name
            stem = rel_path.stem
            suffix = rel_path.suffix

            count = name_counts[fname]
            new_name = fname if count == 1 else f"{stem}{count}{suffix}"
            new_path = output_dir / rel_path.parent / new_name
            new_path.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy2(orig_path, new_path)


EXPECTED_NUM_ARGS = 4

if __name__ == "__main__":
    if len(sys.argv) != EXPECTED_NUM_ARGS:
        print("Использование: python collect_files.py /path/to/input_dir /path/to/output_dir -max_depth num")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    max_depth_ = sys.argv[3]
    max_depth = None if max_depth_ == "0" else int(max_depth_)

    collect_files(input_dir, output_dir, max_depth=max_depth)
