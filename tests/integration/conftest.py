# Фикстуры для интеграционных тестов Makefile / Git
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import TEMPLATE_ROOT, run_make, run_cmd


def has_git_flow():
    """Проверка наличия git-flow."""
    r = subprocess.run(
        ["git", "flow", "version"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return r.returncode == 0


def has_make():
    """Проверка наличия make."""
    r = subprocess.run(
        ["make", "--version"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    return r.returncode == 0


@pytest.fixture(scope="session")
def git_flow_available():
    return has_git_flow()


@pytest.fixture(scope="session")
def make_available():
    return has_make()


def _copy_template_to(tmp_path: Path) -> Path:
    """Копирует файлы шаблона (как после Copier) в tmp_path."""
    import shutil
    exclude = {".git", "PROFILE.yml", "copier.yml", "USAGE.md", "__pycache__", "nul", "tests", "requirements-dev.txt", ".copier-answers.yml"}
    for item in TEMPLATE_ROOT.iterdir():
        if item.name in exclude or (item.name.startswith(".") and item.name not in (".pre-commit-config.yaml", ".cz.toml", ".editorconfig", ".gitignore")):
            continue
        dest = tmp_path / item.name
        if item.is_dir():
            shutil.copytree(item, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
        else:
            shutil.copy2(item, dest)
    for name in (".pre-commit-config.yaml", ".cz.toml", ".editorconfig", ".gitignore"):
        src = TEMPLATE_ROOT / name
        if src.exists():
            shutil.copy2(src, tmp_path / name)
    # README.md в шаблоне может быть .jinja — копируем готовый README если есть
    readme_src = TEMPLATE_ROOT / "README.md"
    if not readme_src.exists():
        readme_src = TEMPLATE_ROOT / "README.md.jinja"
    if readme_src.exists():
        shutil.copy2(readme_src, tmp_path / "README.md")
    return tmp_path


@pytest.fixture
def project_with_git(tmp_path, git_flow_available, make_available):
    """
    Временный каталог с копией шаблона и уже выполненным make init.
    Пропускает тест, если нет git-flow или make.
    """
    if not make_available:
        pytest.skip("make не найден")
    if not git_flow_available:
        pytest.skip("git-flow не найден")
    project = _copy_template_to(tmp_path)
    # Настраиваем git для коммитов
    subprocess.run(["git", "config", "user.email", "test@test"], cwd=project, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=project, capture_output=True, check=True)
    code, out, err = run_make(project, "init")
    if code != 0:
        pytest.skip(f"make init не удался: {out} {err}")
    return project


@pytest.fixture
def project_no_init(tmp_path, make_available):
    """Копия шаблона без make init (для тестов B и негативов)."""
    if not make_available:
        pytest.skip("make не найден")
    return _copy_template_to(tmp_path)
