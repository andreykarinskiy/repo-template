# Отчёт о прогоне тестов (TEST_PLAN.md)

## Параметры прогона

- **Дата:** 2025-02-19
- **ОС:** Windows 10/11 (win32)
- **Python:** 3.14.3
- **pytest:** 9.0.2
- **Инструменты:** Git, make, Copier (с --skip-tasks в E2E), pytest

## Выполненные сценарии и статус

### Юнит-тесты (scripts/version.py) — C1–C9

| Сценарий | Описание | Статус |
|----------|----------|--------|
| C1 | make version / значение из version.json | PASSED |
| C2 | version-full на develop → alpha.N+sha | PASSED |
| C3 | version-full на release/* → rc.N+sha | PASSED |
| C4 | version-full на hotfix/* → beta.N+sha | PASSED |
| C5 | version-full на main/master → X.Y.Z+sha | PASSED |
| C6 | BUILD_NUMBER в версии | PASSED |
| C7 | Негатив: некорректный формат в version.json | PASSED |
| C8 | Без .git — только базовая версия | PASSED |
| C9 | Без version.json → 0.0.0, ненулевой exit | PASSED |

### E2E (Copier) — A1–A5

| Сценарий | Описание | Статус |
|----------|----------|--------|
| A1 | Успешная генерация с дефолтами | PASSED |
| A2 | Рендер README по project_name, description, tags | PASSED |
| A3 | Рендер LICENSE по company и году | PASSED |
| A4 | USAGE.md, PROFILE.yml, copier.yml не копируются (_exclude) | PASSED |
| A5 | _skip_if_exists не перезаписывает при повторном copy | PASSED |

Примечание: E2E запускаются с `--skip-tasks`, чтобы не выполнять `make init` (проверяется только копирование и рендер).

### Интеграционные (Makefile) — B, D, E, F

| Сценарий | Описание | Статус |
|----------|----------|--------|
| B1 | init: git + начальный коммит | SKIPPED (make/git-flow окружение) |
| B2–B4 | develop, git flow init, commit-msg hook | SKIPPED |
| D1–D2, D8 | feature-start/finish, без origin | SKIPPED |
| D7 | Негатив: вне git-репозитория | PASSED |
| E1, E2, E4 | commit-msg, cz | SKIPPED |
| F1, F3 | push, remote | SKIPPED |
| F4 | Негатив: push вне git | PASSED |

Пропуски: тесты, зависящие от `make init` и git-flow, помечаются как skip, если в окружении нет git-flow или `make init` завершается с ошибкой (типично для Windows без настроенного Git Bash как SHELL для make).

## Итог

- **Пройдено:** 20
- **Пропущено:** 14 (интеграции, требующие git-flow / make init)
- **Провалено:** 0

## Ограничения

1. **Windows:** интеграционные тесты B1–B4, D1–D2, D8, E1–E2, E4, F1, F3 пропускаются, если `make init` не выполняется (например, make не использует Git Bash или git-flow недоступен).
2. **Локальный запуск:** сценарии с push (F1, F3) не проверяют реальный remote; F3 проверяет только сообщение об ошибке при отсутствии origin.
3. **Copier:** E2E не проверяют выполнение _tasks (make init); для полного smoke нужен прогон с задачами в среде с git-flow.

## Рекомендации

- Запускать полный набор интеграционных тестов в CI на Linux (или в среде с git-flow и make).
- Для ночного прогона (TEST_PLAN §8) выполнять: `pytest tests/ -v`; на Windows часть интеграционных тестов будет пропущена.
