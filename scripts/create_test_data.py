import random
import string
from pathlib import Path

import click


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
