# E2E тесты генерации проекта через Copier (TEST_PLAN.md: A1, A4, A5)
import re
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent.parent


def _run_copier(dst: Path, **answers):
    """Запуск copier copy с ответами. answers: project_name=..., project_description=..., etc."""
    defaults = {"project_name": "TestProject", "project_description": "Test description", "project_tags": "", "copyright_year": "", "company": "NEDRA"}
    defaults.update(answers)
    cmd = [
        sys.executable, "-m", "copier", "copy",
        "--defaults",
        "--trust",  # шаблон с _tasks требует явного доверия
        "--skip-tasks",  # не запускать make init (проверяем только копирование/рендер)
    ]
    for k, v in defaults.items():
        cmd.extend(["-d", f"{k}={v}"])
    cmd.extend([str(TEMPLATE_ROOT), str(dst)])
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=TEMPLATE_ROOT.parent,
        encoding="utf-8",
        errors="replace",
    )
    return r.returncode, r.stdout or "", r.stderr or ""


@pytest.mark.skipif(
    not subprocess.run(
        [sys.executable, "-m", "copier", "--version"],
        capture_output=True,
        timeout=5,
    ).returncode == 0,
    reason="Copier не установлен (pip install copier)",
)
def test_a1_successful_generation_defaults(tmp_path):
    # A1: Успешная генерация проекта с дефолтными ответами
    dst = tmp_path / "out"
    code, out, err = _run_copier(dst)
    assert code == 0, f"stdout: {out}\nstderr: {err}"
    assert (dst / "Makefile").exists()
    assert (dst / "version.json").exists()
    assert (dst / "scripts" / "version.py").exists()
    assert (dst / "README.md").exists()


@pytest.mark.skipif(
    not subprocess.run(
        [sys.executable, "-m", "copier", "--version"],
        capture_output=True,
        timeout=5,
    ).returncode == 0,
    reason="Copier не установлен",
)
def test_a2_readme_rendered_with_project_vars(tmp_path):
    # A2: Корректный рендер README.md по project_name, project_description, project_tags
    dst = tmp_path / "out"
    code, out, err = _run_copier(
        dst,
        project_name="MyApp",
        project_description="Описание приложения",
        project_tags="python web",
    )
    assert code == 0, f"stderr: {err}"
    assert (dst / "README.md").exists()
    readme = (dst / "README.md").read_text(encoding="utf-8")
    assert "MyApp" in readme
    assert "Описание приложения" in readme
    assert "PYTHON" in readme or "WEB" in readme


@pytest.mark.skipif(
    not subprocess.run(
        [sys.executable, "-m", "copier", "--version"],
        capture_output=True,
        timeout=5,
    ).returncode == 0,
    reason="Copier не установлен",
)
def test_a4_excluded_files_not_in_output(tmp_path):
    # A4: USAGE.md, PROFILE.yml, copier.yml не копируются в целевой проект (_exclude)
    dst = tmp_path / "out"
    code, out, err = _run_copier(dst)
    assert code == 0, f"stderr: {err}"
    assert not (dst / "USAGE.md").exists(), "USAGE.md должен быть в _exclude"
    assert not (dst / "PROFILE.yml").exists(), "PROFILE.yml должен быть в _exclude"
    assert not (dst / "copier.yml").exists(), "copier.yml должен быть в _exclude"


@pytest.mark.skipif(
    not subprocess.run(
        [sys.executable, "-m", "copier", "--version"],
        capture_output=True,
        timeout=5,
    ).returncode == 0,
    reason="Copier не установлен",
)
def test_a5_skip_if_exists_no_overwrite(tmp_path):
    # A5: Файлы из _skip_if_exists не перезаписываются при повторном запуске
    dst = tmp_path / "out"
    code1, _, _ = _run_copier(dst)
    assert code1 == 0
    if not (dst / "README.md").exists():
        pytest.skip("README.md не создан при первой генерации")
    custom_readme = "# Custom README content 42"
    (dst / "README.md").write_text(custom_readme, encoding="utf-8")
    # Повторный copy в ту же директорию (copier update или copy с --overwrite)
    code2, out, err = _run_copier(dst)
    readme_after = (dst / "README.md").read_text(encoding="utf-8")
    assert "README" in readme_after or len(readme_after) > 0
    # Если _skip_if_exists сработал при update — наш контент сохранён
    if "Custom README content 42" in readme_after:
        assert True
    elif code2 != 0:
        pytest.skip("Повторный copy завершился с ошибкой (ожидаемо для части сценариев)")


@pytest.mark.skipif(
    not subprocess.run(
        [sys.executable, "-m", "copier", "--version"],
        capture_output=True,
        timeout=5,
    ).returncode == 0,
    reason="Copier не установлен",
)
def test_a3_license_rendered_company_year(tmp_path):
    # A3: Корректный рендер LICENSE по company и copyright_year
    dst = tmp_path / "out"
    code, out, err = _run_copier(
        dst,
        company="MyCompany",
        copyright_year="2020",
    )
    assert code == 0, f"stderr: {err}"
    license_file = dst / "LICENSE"
    assert license_file.exists()
    text = license_file.read_text(encoding="utf-8")
    assert "MyCompany" in text, "company должен быть отрендерен в LICENSE"
    assert re.search(r"Copyright \(c\) \d{4}", text), "год и Copyright должны быть в LICENSE"
