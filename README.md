# Обобщенный шаблон репозитория

Версионирование по SemVer и GitFlow: базовая версия в `version.json`, полная версия с пререлизом и метаданными — через `make version-full`. 

Стандартизация коммитов через Commitizen с автоматической проверкой формата сообщений.

## Как использовать

1. **Зависимости:** Git, git-flow, Python 3.x, make, [Copier](https://copier.readthedocs.io/) (`pip install copier`). На Windows — Git for Windows (включает bash и git-flow).

2. **Создать новый проект из шаблона:**
   ```bash
   copier copy ./generic-repo-template ./my-project --trust
   ```
   При запросе укажите название проекта, описание, теги и год для лицензии.

3. **Инициализировать репозиторий:**
   ```bash
   cd my-project
   make init
   ```
   Выполняются: `git init`, создание ветки `develop`, инициализация GitFlow, установка pre-commit и Commitizen.

4. **Основные команды в созданном проекте:**
   - `make help` — список всех команд
   - `make version` — базовая версия из `version.json`
   - `make version-full` — полная SemVer с учётом ветки и метаданных
   - `make commit` — интерактивный коммит через Commitizen
   - `make push [REMOTE=origin] [BRANCH=]` — отправить изменения в удалённую ветку

5. **Рабочий цикл (GitFlow):**
   - Фича: `make feature-start <имя>` → работа в ветке `feature/<имя>` → `make feature-finish <имя>`
   - Релиз: из `develop` — `make release-start`, затем в ветке `release/<версия>` — `make release-finish`
   - Хотфикс: из `main`/`master` — `make hotfix-start HOTFIX=1.2.1`, затем в ветке `hotfix/<версия>` — `make hotfix-finish HOTFIX=1.2.1`

Версию в `version.json` обновляйте через `cz bump`; полные форматы версий по веткам — в [RULES.md](RULES.md).

Подробная инструкция, примеры и устранение неполадок — в [USAGE.md](USAGE.md).