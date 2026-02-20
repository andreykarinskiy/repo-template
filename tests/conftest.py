# Общие фикстуры для тестов generic-repo-template (TEST_PLAN.md)
import os
import shutil
import subprocess
from pathlib import Path

import pytest


# Корень шаблона (где copier.yml, Makefile, scripts/)
TEMPLATE_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def template_root():
    """Корень шаблона репозитория."""
    return TEMPLATE_ROOT


@pytest.fixture
def project_copy(tmp_path, template_root):
    """
    Копия файлов проекта (как после Copier) в временную директорию.
    Копирует только то, что попадает в целевой проект (без _exclude).
    """
    exclude = {
        ".git",
        "PROFILE.yml",
        "copier.yml",
        "USAGE.md",
        "__pycache__",
        "nul",
        "tests",  # тесты шаблона не копируются в проект
        "requirements-dev.txt",
    }
    for item in template_root.iterdir():
        if item.name in exclude or item.name.startswith(".") and item.name in (".copier-answers.yml",):
            continue
        dest = tmp_path / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
        else:
            shutil.copy2(item, dest)
    # Копируем .pre-commit-config.yaml, .cz.toml, .editorconfig, .gitignore если есть
    for name in (".pre-commit-config.yaml", ".cz.toml", ".editorconfig", ".gitignore"):
        src = template_root / name
        if src.exists():
            shutil.copy2(src, tmp_path / name)
    return tmp_path


def run_make(cwd: Path, target: str, *args, env=None, input_text: str | None = None):
    """Запуск make в каталоге cwd. Возвращает (returncode, stdout, stderr)."""
    cmd = ["make", target] + list(args)
    env = env or os.environ.copy()
    r = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
        input=input_text,
        encoding="utf-8",
        errors="replace",
    )
    return r.returncode, r.stdout or "", r.stderr or ""


def run_cmd(cwd: Path, *cmd, env=None):
    """Запуск команды в каталоге cwd. Возвращает (returncode, stdout, stderr)."""
    env = env or os.environ.copy()
    r = subprocess.run(
        list(cmd),
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        encoding="utf-8",
        errors="replace",
    )
    return r.returncode, r.stdout or "", r.stderr or ""


@pytest.fixture
def run_in_project(project_copy):
    """Запуск make в project_copy. Возвращает функцию run_make(cwd=project_copy)."""
    def _run(target, *args, env=None):
        return run_make(project_copy, target, *args, env=env)
    return _run
