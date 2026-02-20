# Юнит-тесты scripts/version.py (TEST_PLAN.md: C1–C9)
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Загрузка модуля version из шаблона
TEMPLATE_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_version_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "version",
        TEMPLATE_ROOT / "scripts" / "version.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def version_module():
    return _load_version_module()


@pytest.fixture
def version_file(tmp_path):
    """Путь к version.json во временной директории."""
    return tmp_path / "version.json"


# ---------------------------------------------------------------------------
# load_base_version
# ---------------------------------------------------------------------------

def test_load_base_version_valid(version_module, version_file):
    # arrange
    version_file.write_text('{"version": "1.2.3"}', encoding="utf-8")

    # act
    result = version_module.load_base_version(version_file)

    # assert
    assert result == "1.2.3"


def test_load_base_version_default_key(version_module, version_file):
    # arrange
    version_file.write_text('{}', encoding="utf-8")

    # act
    result = version_module.load_base_version(version_file)

    # assert (в коде data.get("version", "0.0.0") — но потом re.match не пройдёт для "0.0.0"?)
    # В version.py: version = data.get("version", "0.0.0") -> "0.0.0", re.match(r"^\d+\.\d+\.\d+", "0.0.0") -> True
    assert result == "0.0.0"


def test_load_base_version_invalid_format_raises(version_module, version_file):
    # arrange
    version_file.write_text('{"version": "v1.2.3"}', encoding="utf-8")

    # act & assert
    with pytest.raises(ValueError, match="Некорректная базовая версия"):
        version_module.load_base_version(version_file)


def test_load_base_version_invalid_format_no_semver_raises(version_module, version_file):
    # arrange
    version_file.write_text('{"version": "1.2"}', encoding="utf-8")

    # act & assert — 1.2 не совпадает с ^\d+\.\d+\.\d+
    with pytest.raises(ValueError, match="Некорректная базовая версия"):
        version_module.load_base_version(version_file)


# ---------------------------------------------------------------------------
# main() через запуск скрипта (C1, C8, C9)
# ---------------------------------------------------------------------------

def _run_version_script(cwd: Path, env=None):
    env = env or os.environ.copy()
    r = subprocess.run(
        [sys.executable, str(TEMPLATE_ROOT / "scripts" / "version.py")],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


def test_c1_version_from_version_json(tmp_path):
    # C1: make version возвращает значение из version.json (скрипт выводит полную версию)
    # arrange
    (tmp_path / "version.json").write_text('{"version": "2.0.1"}', encoding="utf-8")
    (tmp_path / ".git").mkdir()

    # act
    code, out, err = _run_version_script(tmp_path)

    # assert
    assert code == 0
    assert out.startswith("2.0.1")


def test_c8_no_git_returns_base_only(tmp_path):
    # C8: при отсутствии .git скрипт возвращает базовую версию
    # arrange
    (tmp_path / "version.json").write_text('{"version": "1.0.0"}', encoding="utf-8")
    # .git нет

    # act
    code, out, err = _run_version_script(tmp_path)

    # assert
    assert code == 0
    assert out == "1.0.0"


def test_c9_no_version_json_returns_0_0_0_and_nonzero_exit(tmp_path):
    # C9: при отсутствии version.json возвращается 0.0.0 и ненулевой код
    # arrange: только .git чтобы мы были "в репо" для вывода
    (tmp_path / ".git").mkdir()
    # version.json нет

    # act — в version.py: if not version_file.exists(): print("0.0.0"); sys.exit(1)
    code, out, err = _run_version_script(tmp_path)

    # assert
    assert code != 0
    assert out == "0.0.0"


def test_c7_invalid_version_in_json_exit_error(tmp_path):
    # C7 (негатив): некорректный формат версии в version.json приводит к ошибке
    # arrange
    (tmp_path / "version.json").write_text('{"version": "invalid"}', encoding="utf-8")
    (tmp_path / ".git").mkdir()

    # act
    code, out, err = _run_version_script(tmp_path)

    # assert — в main() base = load_base_version() поднимет ValueError, except печатает base и exit(1)
    assert code != 0
    assert "0.0.0" in out or "invalid" in err or "Некоррект" in err or "Ошибка" in err


# ---------------------------------------------------------------------------
# full_version по веткам (C2–C6) — нужен реальный git с ветками
# ---------------------------------------------------------------------------

@pytest.fixture
def git_repo(tmp_path):
    """Инициализированный git-репозиторий с version.json и одной веткой (develop)."""
    (tmp_path / "version.json").write_text('{"version": "1.3.0"}', encoding="utf-8")
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "chore: init"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    return tmp_path


def test_c2_version_full_develop(git_repo):
    # C2: version-full на develop -> X.Y.Z-alpha.N+sha.<hash>
    subprocess.run(["git", "checkout", "-b", "develop"], cwd=git_repo, capture_output=True, check=True)
    code, out, err = _run_version_script(git_repo)
    assert code == 0
    assert "1.3.0-alpha." in out
    assert "+sha." in out


def test_c3_version_full_release(git_repo):
    # C3: version-full на release/* -> X.Y.Z-rc.N+sha.<hash>
    subprocess.run(["git", "checkout", "-b", "release/1.3.0"], cwd=git_repo, capture_output=True, check=True)
    code, out, err = _run_version_script(git_repo)
    assert code == 0
    assert "1.3.0-rc." in out
    assert "+sha." in out


def test_c4_version_full_hotfix(git_repo):
    # C4: version-full на hotfix/* -> X.Y.Z-beta.N+sha.<hash>
    subprocess.run(["git", "checkout", "-b", "main"], cwd=git_repo, capture_output=True, check=True)
    subprocess.run(["git", "checkout", "-b", "hotfix/1.2.1"], cwd=git_repo, capture_output=True, check=True)
    (git_repo / "version.json").write_text('{"version": "1.2.1"}', encoding="utf-8")
    code, out, err = _run_version_script(git_repo)
    assert code == 0
    assert "1.2.1-beta." in out
    assert "+sha." in out


def test_c5_version_full_main(git_repo):
    # C5: version-full на main/master -> X.Y.Z+sha.<hash>
    subprocess.run(["git", "checkout", "-b", "main"], cwd=git_repo, capture_output=True, check=True)
    code, out, err = _run_version_script(git_repo)
    assert code == 0
    assert out.startswith("1.3.0+sha.")
    assert "-alpha" not in out and "-rc" not in out and "-beta" not in out


def test_c6_build_number_from_env(tmp_path):
    # C6: при BUILD_NUMBER=123 используется N=123
    (tmp_path / "version.json").write_text('{"version": "1.0.0"}', encoding="utf-8")
    (tmp_path / ".git").mkdir()
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "c"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(["git", "checkout", "-b", "develop"], cwd=tmp_path, capture_output=True, check=True)
    env = os.environ.copy()
    env["BUILD_NUMBER"] = "123"
    code, out, err = _run_version_script(tmp_path, env=env)
    assert code == 0
    assert "-alpha.123+sha." in out
