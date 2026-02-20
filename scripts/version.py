#!/usr/bin/env python3
"""
Формирует полную SemVer-версию по правилам GitFlow.
Базовая версия берётся из version.json, пререлиз и метаданные — из ветки и git.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def load_base_version(version_file: Path) -> str:
    """Читает базовую версию X.Y.Z из version.json."""
    data = json.loads(version_file.read_text(encoding="utf-8"))
    version = data.get("version", "0.0.0")
    if not re.match(r"^\d+\.\d+\.\d+", version):
        raise ValueError(f"Некорректная базовая версия в {version_file}: {version}")
    return version.strip()


def git_command(args: list[str], cwd: Path) -> str:
    """Выполняет git и возвращает вывод без пробелов по краям."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        # Логируем ошибку в stderr, но не прерываем выполнение
        if result.stderr:
            print(f"Предупреждение: git {' '.join(args)} завершился с ошибкой: {result.stderr.strip()}", file=sys.stderr)
        return ""
    return result.stdout.strip()


def get_branch(repo_root: Path) -> str:
    """Возвращает имя текущей ветки или пустую строку."""
    branch = git_command(["rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    if not branch:
        # Если не удалось определить ветку, пробуем получить через symbolic-ref
        branch = git_command(["symbolic-ref", "--short", "HEAD"], repo_root)
    return branch


def get_short_sha(repo_root: Path) -> str:
    """Возвращает короткий хеш текущего коммита."""
    sha = git_command(["rev-parse", "--short", "HEAD"], repo_root)
    if not sha:
        # Если не удалось получить sha, возвращаем значение по умолчанию
        return "norev"
    return sha


def has_remote(repo_root: Path, remote_name: str = "origin") -> bool:
    """Проверяет наличие remote в репозитории."""
    remotes = git_command(["remote"], repo_root)
    if not remotes:
        return False
    return remote_name in remotes.split("\n")


def is_tracking_remote(repo_root: Path, branch: str) -> bool:
    """Проверяет, отслеживается ли ветка удаленно."""
    # Проверяем через git config
    remote = git_command(["config", "--get", f"branch.{branch}.remote"], repo_root)
    if remote:
        return True
    # Альтернативная проверка через rev-parse
    upstream = git_command(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        repo_root,
    )
    return bool(upstream)


def get_commit_count(repo_root: Path) -> int:
    """
    Номер сборки: используется переменная окружения BUILD_NUMBER, если доступна,
    иначе количество коммитов от начала текущей ветки или от последнего тега.
    """
    # Проверяем переменную окружения (например, из CI/CD)
    build_number = os.environ.get("BUILD_NUMBER")
    if build_number and build_number.isdigit():
        return int(build_number)
    
    # Пытаемся получить количество коммитов от начала ветки
    branch = get_branch(repo_root)
    if branch:
        # Проверяем наличие remote и отслеживание ветки перед использованием origin/{branch}
        if has_remote(repo_root, "origin") and is_tracking_remote(repo_root, branch):
            out = git_command(["rev-list", "--count", f"origin/{branch}..HEAD"], repo_root)
            if out.isdigit() and int(out) > 0:
                return int(out)
        # Если ветка не отслеживается или remote отсутствует, используем количество от последнего тега
        out = git_command(["rev-list", "--count", "HEAD"], repo_root)
        if out.isdigit():
            return int(out)
    
    # Fallback: общее количество коммитов
    out = git_command(["rev-list", "--count", "HEAD"], repo_root)
    return int(out) if out.isdigit() else 1


def build_metadata(repo_root: Path) -> str:
    """Метаданные сборки: только короткий sha (SemVer: после +)."""
    sha = get_short_sha(repo_root)
    return f"sha.{sha}"


def full_version(base: str, repo_root: Path) -> str:
    """
    Собирает полную версию по ветке GitFlow.
    develop → X.Y.Z-alpha.N+sha.xxx
    release/* → X.Y.Z-rc.N+sha.xxx
    hotfix/* → X.Y.Z-beta.N+sha.xxx
    main/master → X.Y.Z+sha.xxx (без пререлизного идентификатора)
    """
    branch = get_branch(repo_root)
    metadata = build_metadata(repo_root)
    build_num = get_commit_count(repo_root)

    if branch == "develop":
        return f"{base}-alpha.{build_num}+{metadata}"
    if branch.startswith("release/"):
        return f"{base}-rc.{build_num}+{metadata}"
    if branch.startswith("hotfix/"):
        return f"{base}-beta.{build_num}+{metadata}"
    # main, master и прочие — без пререлизного идентификатора, только +sha
    if branch in ("main", "master"):
        return f"{base}+{metadata}"
    # Для остальных веток также без пререлизного идентификатора
    return f"{base}+{metadata}"


def main() -> None:
    repo_root = Path.cwd()
    version_file = repo_root / "version.json"
    if not version_file.exists():
        print("0.0.0", file=sys.stdout)
        sys.exit(1)
    base = load_base_version(version_file)
    # Вне репозитория или без git — только базовая версия
    if not (repo_root / ".git").exists():
        print(base)
        return
    try:
        print(full_version(base, repo_root))
    except Exception as e:
        print(f"Ошибка при определении версии: {e}", file=sys.stderr)
        print(base, file=sys.stdout)  # Явно указываем stdout
        sys.exit(1)  # Выходим с ошибкой, но версию всё равно выводим


if __name__ == "__main__":
    main()
