#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

IGNORED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    "build",
    "dist",
    ".cache",
    "htmlcov",
}
ALLOWED_DOT_DIRS = {".github"}
IGNORED_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
    ".coverage",
    "poetry.lock",
    "package-lock.json",
    "yarn.lock",
}
ALWAYS_INCLUDE_FILENAMES = {
    "Dockerfile",
    "Makefile",
    "LICENSE",
    ".env.example",
}
ALLOWED_EXTENSIONS = {
    ".py",
    ".pyi",
    ".txt",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".env",
    ".json",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".bat",
    ".sql",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".vue",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".pyi": "python",
    ".md": "markdown",
    ".toml": "toml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".ini": "ini",
    ".cfg": "ini",
    ".env": "bash",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".ps1": "powershell",
    ".bat": "batch",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".jsx": "jsx",
    ".vue": "vue",
}
LANGUAGE_BY_NAME = {
    "Dockerfile": "dockerfile",
    "Makefile": "makefile",
    "LICENSE": "",
}


class TreeNode:
    __slots__ = ("children", "files")

    def __init__(self) -> None:
        self.children: dict[str, TreeNode] = {}
        self.files: list[str] = []


def should_include_file(path: Path) -> bool:
    if path.name in ALWAYS_INCLUDE_FILENAMES:
        return True
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def collect_files(root: Path, excluded_paths: set[Path]) -> list[Path]:
    included: list[Path] = []

    for current_dir, dirnames, filenames in os.walk(root):
        current_path = Path(current_dir)

        dirnames[:] = [
            d
            for d in dirnames
            if d not in IGNORED_DIR_NAMES
            and (not d.startswith(".") or d in ALLOWED_DOT_DIRS)
        ]

        for filename in sorted(filenames):
            file_path = current_path / filename

            if file_path.resolve() in excluded_paths:
                continue
            if filename in IGNORED_FILE_NAMES:
                continue
            if not should_include_file(file_path):
                continue

            included.append(file_path)

    return sorted(included)


def build_tree(root: Path, files: list[Path]) -> TreeNode:
    root_node = TreeNode()

    for file_path in files:
        relative_parts = file_path.relative_to(root).parts
        node = root_node
        for part in relative_parts[:-1]:
            node = node.children.setdefault(part, TreeNode())
        node.files.append(relative_parts[-1])

    return root_node


def render_tree(node: TreeNode, prefix: str = "") -> list[str]:
    lines: list[str] = []
    entries: list[tuple[str, TreeNode | None, bool]] = []

    for dir_name in sorted(node.children):
        entries.append((dir_name, node.children[dir_name], True))
    for file_name in sorted(node.files):
        entries.append((file_name, None, False))

    for index, (name, child, is_dir) in enumerate(entries):
        connector = "└── " if index == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{name}")
        if is_dir and child is not None:
            extension = "    " if index == len(entries) - 1 else "│   "
            lines.extend(render_tree(child, prefix + extension))

    return lines


def detect_language(path: Path) -> str:
    if path.name in LANGUAGE_BY_NAME:
        return LANGUAGE_BY_NAME[path.name]
    return LANGUAGE_BY_SUFFIX.get(path.suffix.lower(), "")


def create_snapshot(root: Path, files: list[Path]) -> str:
    tree = build_tree(root, files)
    tree_lines = [root.name or "."]
    tree_lines.extend(render_tree(tree))

    parts: list[str] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    parts.append("# Project Snapshot")
    parts.append(f"_Generated on {timestamp}_")
    parts.append("")
    parts.append("## Structure")
    parts.append("```")
    parts.extend(tree_lines)
    parts.append("```")
    parts.append("")
    parts.append("## Files")

    for file_path in files:
        rel_path = file_path.relative_to(root).as_posix()
        language = detect_language(file_path)
        content = file_path.read_text(encoding="utf-8", errors="replace").rstrip()

        parts.append(f"### `{rel_path}`")
        parts.append(f"```{language}".rstrip())
        parts.append(content)
        parts.append("```")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Собирает структуру проекта и содержимое файлов в один текстовый snapshot."
    )
    parser.add_argument(
        "-r",
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Корневая директория проекта (по умолчанию текущая).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("project_snapshot.txt"),
        help="Файл, куда сохранить результат (по умолчанию project_snapshot.txt).",
    )

    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()

    if not root.is_dir():
        parser.error(f"Директория '{root}' не существует.")

    files = collect_files(root, excluded_paths={output})
    if not files:
        parser.error("Не найдено ни одного подходящего файла для выгрузки.")

    snapshot = create_snapshot(root, files)
    output.write_text(snapshot, encoding="utf-8")

    print(f"Snapshot сохранён в {output}")


if __name__ == "__main__":
    main()
# (venv) PS D:\learn\test_work> python dump.py --root . --output project_snapshot.txt
