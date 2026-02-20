# E2E: проверка генерации через Copier (TEST_PLAN.md: A)
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent.parent


def copier_available():
    r = subprocess.run(
        [sys.executable, "-m", "copier", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    return r.returncode == 0


@pytest.fixture(scope="session")
def has_copier():
    return copier_available()
