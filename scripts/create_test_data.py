import random
import string
from pathlib import Path

import click

RANDOM_STATE = random.Random(42)


def random_filename(extension: str = ".txt") -> str:
    name = "".join(RANDOM_STATE.choices(string.ascii_lowercase, k=10))
    return f"{name}{extension}"


def create_test_structure(
    base_dir: Path,
    max_depth: int = 3,
    files_per_dir: int = 2,
    dirs_per_dir: int = 2,
    current_depth: int = 0,
    num_unique_names: int | None = None,
    unique_names: list[str] | None = None,
) -> None:
    if current_depth >= max_depth:
        return

    # To have non-unique names
    unique_names: list[str] | None = None
    if num_unique_names is not None:
        unique_names = [random_filename() for _ in range(num_unique_names)]

    for _ in range(files_per_dir):
        file_path = base_dir / RANDOM_STATE.choice(unique_names) if unique_names else base_dir / random_filename()
        with open(file_path, "w") as f:
            f.write(f"Test content at depth {current_depth}\n")

    for i in range(dirs_per_dir):
        dir_name = f"dir_{current_depth}_{i}"
        new_dir_path = base_dir / dir_name
        new_dir_path.mkdir(exist_ok=True)
        create_test_structure(
            new_dir_path, max_depth, files_per_dir, dirs_per_dir, current_depth + 1, unique_names=unique_names
        )


@click.command()
@click.argument("base_dir", type=click.Path())
@click.option("--depth", default=3, help="Максимальная глубина вложенности.", show_default=True)
@click.option("--files", default=2, help="Количество файлов в каждой директории.", show_default=True)
@click.option("--dirs", default=2, help="Количество подпапок в каждой директории.", show_default=True)
def generate(base_dir: str, depth: int, files: int, dirs: int) -> None:
    """Генерирует тестовую структуру директорий в BASE_DIR."""
    base_dir = Path(base_dir)
    base_dir.mkdir(exist_ok=True)
    create_test_structure(base_dir, depth, files, dirs)
    click.echo(f"Тестовая структура создана в {base_dir}")


if __name__ == "__main__":
    generate()
