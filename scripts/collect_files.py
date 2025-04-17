import shutil
import sys
from collections import defaultdict
from pathlib import Path


def collect_files(input_dir: Path, output_dir: Path) -> None:
    if not input_dir.is_dir():
        print(f"Ошибка: {input_dir} не является директорией.")
        sys.exit(1)

    output_dir.mkdir(exist_ok=True)

    name_counts = defaultdict(int)

    for file_path in input_dir.rglob("*"):
        if not file_path.is_file():
            continue
        fname = file_path.name
        stem = file_path.stem
        suffix = file_path.suffix

        count = name_counts[fname]
        new_name = fname if count == 0 else f"{stem}{count}{suffix}"

        name_counts[fname] += 1

        destination = output_dir / new_name
        shutil.copy2(file_path, destination)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python collect_files.py /path/to/input_dir /path/to/output_dir")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    collect_files(input_dir, output_dir)
