#!/usr/bin/env python3
# ruff: noqa: RUF001, RUF002, RUF003
"""
tree.py - выводит дерево проекта, исключая мусорные директории и файлы
python backend/app/utils/tree.py .
python app/utils/tree.py . --show-content     # + содержимое файлов
"""

import argparse
import fnmatch
import sys
from pathlib import Path

# Список игнорируемых элементов
IGNORE_LIST = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    ".env",
    ".env.local",
    ".env.prod",
    ".DS_Store",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".vscode",
    ".idea",
    "*.pyc",
    "*.log",
    "*.tmp",
    "Thumbs.db",
    "__init__.py",
    "alembic/versions",
    "redis/data",
    "script.py.mako",
    "tree.py",
    "uv.lock",
}

# Максимальный размер файла для вывода содержимого (в байтах)
MAX_FILE_SIZE = 10 * 1024  # 10 КБ


def should_ignore(relative_path: Path) -> bool:
    """Проверяет, нужно ли игнорировать файл/папку по относительному пути."""
    rel_str = str(relative_path).replace("\\", "/")  # унифицируем разделители

    for pattern in IGNORE_LIST:
        if pattern.startswith("*."):
            # Паттерн для имён (без пути)
            if relative_path.name.endswith(pattern[1:]):
                return True
        elif pattern.endswith("/"):
            # Явное указание директории
            if fnmatch.fnmatch(rel_str + "/", pattern):
                return True
        else:
            # Точное совпадение пути ИЛИ совпадение имени (для обратной совместимости)
            if rel_str == pattern or relative_path.name == pattern:
                return True
    return False


def read_file_content(file_path: Path) -> str:
    """Читает содержимое файла с обработкой ошибок и ограничением размера."""
    try:
        # Не читаем бинарные файлы по расширению
        binary_exts = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
            ".sqlite",
            ".db",
        }
        if file_path.suffix.lower() in binary_exts:
            return "  [бинарный файл]"

        if file_path.stat().st_size > MAX_FILE_SIZE:
            return f"  [Файл слишком большой (> {MAX_FILE_SIZE // 1024} КБ)]"

        with file_path.open(encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
            if not lines:
                return "  (пустой файл)"
            # Добавляем отступ ко всем строкам
            return "\n".join(f"  {line}" for line in lines)
    except OSError as e:  # FileNotFoundError, PermissionError и т.д.
        return f"  [Ошибка ввода/вывода: {e}]"
    except UnicodeDecodeError as e:
        return f"  [Ошибка кодировки: {e}]"


def tree(
    dir_path: Path,
    prefix: str = "",
    show_content: bool = False,
    root: Path | None = None,
):
    """Рекурсивно выводит структуру директории."""
    # Получаем содержимое, фильтруем игнорируемые элементы
    if root is None:
        root = dir_path.resolve()

    try:
        filtered_entries = []
        for p in dir_path.iterdir():
            try:
                # Получаем относительный путь от корня проекта
                rel_path = p.relative_to(root)
            except ValueError:
                # Если путь не внутри root (маловероятно, но на всякий случай)
                rel_path = p.name
            if not should_ignore(rel_path):
                filtered_entries.append(p)

        contents = sorted(filtered_entries, key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        print(prefix + "└── [не доступно]")
        return

    if not contents:
        return

    pointers = ["├── "] * (len(contents) - 1) + ["└── "]

    for pointer, path in zip(pointers, contents, strict=True):
        print(prefix + pointer + path.name)
        if path.is_dir():
            extension = "│   " if pointer == "├── " else "    "
            tree(path, prefix + extension, show_content=show_content, root=root)
        elif show_content and path.is_file():
            # Выводим содержимое файла
            content = read_file_content(path)
            if content:
                # Добавляем отступ под файлом
                indent = prefix + ("│   " if pointer == "├── " else "    ")
                for line in content.splitlines():
                    print(indent + line)


def main():
    parser = argparse.ArgumentParser(
        description="Выводит дерево проекта с опциональным показом содержимого файлов"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Корневая директория (по умолчанию: текущая)",
    )
    parser.add_argument(
        "-c",
        "--show-content",
        action="store_true",
        help="Показывать содержимое файлов (ограничено 10 КБ на файл)",
    )

    args = parser.parse_args()
    root_path = Path(args.path).resolve()

    if not root_path.exists():
        print(f"Ошибка: путь '{root_path}' не существует.", file=sys.stderr)
        sys.exit(1)

    print("СТРУКТУРА ПРОЕКТА:")
    print(root_path.name + "/")
    tree(root_path, show_content=args.show_content, root=root_path)


if __name__ == "__main__":
    main()

