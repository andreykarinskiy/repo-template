# Универсальные команды управления репозиторием.
# ВНИМАНИЕ! Команды, помеченные как "TODO", нужно реализовать, а после удалить текст "TODO:".
# Определение shell в зависимости от ОС (кроссплатформенность: Windows, Linux, Mac)

MAKEFLAGS += --no-print-directory

ifeq ($(OS),Windows_NT)
    DEVNULL := >NUL 2>&1
    # Явный путь к bash.exe Git for Windows (не "bash" из PATH — там может быть WSL)
    ifneq ($(wildcard C:/PROGRA~1/Git/bin/bash.exe),)
        GIT_BASH_EXE := C:/PROGRA~1/Git/bin/bash.exe
    else ifneq ($(wildcard C:/PROGRA~2/Git/bin/bash.exe),)
        GIT_BASH_EXE := C:/PROGRA~2/Git/bin/bash.exe
    else ifneq ($(wildcard C:/Program Files/Git/bin/bash.exe),)
        GIT_BASH_EXE := C:/Program Files/Git/bin/bash.exe
    else ifneq ($(wildcard C:/Program Files (x86)/Git/bin/bash.exe),)
        GIT_BASH_EXE := C:/Program Files (x86)/Git/bin/bash.exe
    else
        GIT_BASH_EXE :=
    endif
    ifneq ($(GIT_BASH_EXE),)
        SHELL := $(GIT_BASH_EXE)
    else
        $(error Git bash не найден. Установите Git for Windows и добавьте его в PATH)
    endif
    .SHELLFLAGS := -c
    # Явный путь к bash — обход WSL (bash в PATH может быть wsl.exe) и бага CreateProcess
    GIT_INIT_CMD := cmd /c "\"$(GIT_BASH_EXE)\" scripts/git-init.sh"
else
    DEVNULL := >/dev/null 2>&1
    SHELL := /bin/bash
    .SHELLFLAGS := -c
    GIT_INIT_CMD := bash scripts/git-init.sh
endif

.DEFAULT_GOAL := help
.PHONY: help init version version-full build test clean commit push feature-start feature-finish release-start release-finish hotfix-start hotfix-finish
.SILENT:

#------------------------------------------------------------------------------------------------
# args
#------------------------------------------------------------------------------------------------

# Захват позиционных аргументов: make <target> arg1 arg2 → ARGS = arg1 arg2
ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
# Превращаем аргументы в пустые цели, чтобы make не ругался
$(eval $(ARGS):;@:)

# Имя фичи: используем FEATURE_NAME из окружения, если задано, иначе объединяем все аргументы через дефис
# Это позволяет использовать имена с пробелами через переменную окружения:
# FEATURE_NAME="ISSUE-123 add login" make feature-start
# Или использовать дефисы: make feature-start ISSUE-123-add-login
empty :=
space := $(empty) $(empty)
FEATURE_NAME ?= $(subst $(space),-,$(ARGS))

# Проверка наличия аргумента (используется в feature-start/finish)
define check-feature-arg
$(if $(FEATURE_NAME),,$(error Укажите имя фичи, напр.: make $(1) ISSUE-123-desc или FEATURE_NAME="name with spaces" make $(1)))
endef

# Определение команды Python 3.x с учетом платформы
# Используем прямой вызов Python для проверки доступности и версии
ifeq ($(OS),Windows_NT)
    # На Windows проверяем доступность Python через прямой вызов
    # Пробуем python3, затем python, затем python.exe и python3.exe
    PYTHON_CMD := $(shell python3 --version $(DEVNULL) && echo python3 || (python --version $(DEVNULL) && echo python || (python.exe --version $(DEVNULL) && echo python.exe || (python3.exe --version $(DEVNULL) && echo python3.exe || echo ""))))
else
    # На Unix-системах используем command -v
    PYTHON_CMD := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo "")
endif

# Проверка наличия Python
ifeq ($(PYTHON_CMD),)
    $(error Python не найден. Установите Python 3.x и добавьте его в PATH)
endif

# Проверка версии Python (должен быть 3.x) с улучшенной обработкой ошибок
PYTHON_VERSION_CHECK := $(shell $(PYTHON_CMD) -c "import sys; exit(0 if sys.version_info >= (3, 0) else 1)" $(DEVNULL) && echo "ok" || echo "error")
ifeq ($(PYTHON_VERSION_CHECK),error)
    PYTHON_VERSION := $(shell $(PYTHON_CMD) --version 2>&1)
    $(error Требуется Python 3.x. Найденная версия Python не поддерживается: $(PYTHON_VERSION). Проверьте установку Python 3.x)
endif

ifeq ($(wildcard version.json),)
    VERSION := 0.0.0
else
    VERSION := $(shell $(PYTHON_CMD) -c "import json, sys, os, re; \
        try: \
            with open('version.json', 'r', encoding='utf-8') as f: \
                data = json.load(f); \
                version = data.get('version', '0.0.0'); \
                if version and not re.match(r'^\d+\.\d+\.\d+', str(version)): \
                    print(f'Ошибка: некорректный формат версии в version.json: {version}. Ожидается SemVer (X.Y.Z)', file=sys.stderr); \
                    sys.exit(1); \
                print(str(version) if version else '0.0.0'); \
        except (json.JSONDecodeError, KeyError, IOError, ValueError, AttributeError) as e: \
            print(f'Ошибка при чтении version.json: {e}', file=sys.stderr); \
            print('0.0.0'); \
        except Exception as e: \
            print(f'Неожиданная ошибка: {e}', file=sys.stderr); \
            print('0.0.0')" 2>&1 || echo "0.0.0")
endif

help: ## Список поддерживаемых команд
	@$(PYTHON_CMD) -c "import re, sys, os; os.system('') if os.name == 'nt' else None; f = open('$(MAKEFILE_LIST)', encoding='utf-8'); [print(f'\033[33m{m.group(1):15} [TODO] {m.group(2).replace(\"TODO:\", \"\").strip()}\033[0m' if 'TODO:' in m.group(2) else f'\033[36m{m.group(1):15}\033[0m {m.group(2)}') for m in [re.search(r'^([a-zA-Z_-]+):.*?## (.*)$$', l) for l in f] if m]"

#------------------------------------------------------------------------------------------------
# init 
#------------------------------------------------------------------------------------------------
init: git-init install-git-hooks install-commitizen ## Инициализация репозитория.

git-init:
	@$(GIT_INIT_CMD)


install-git-hooks: # Установка git-хуков для валидации, линтинга и т.п.
	@$(PYTHON_CMD) -m pip install pre-commit
	@$(PYTHON_CMD) -m pre_commit install --hook-type commit-msg

install-commitizen:
	@$(PYTHON_CMD) -m pip install commitizen


#------------------------------------------------------------------------------------------------
# version 
#------------------------------------------------------------------------------------------------
version: ## Показать версию репозитория.
	@echo $(VERSION)

version-full: ## Показать полную SemVer-версию с учётом GitFlow и метаданных сборки.
	@$(PYTHON_CMD) scripts/version.py


#------------------------------------------------------------------------------------------------
# build 
#------------------------------------------------------------------------------------------------
build: ## TODO: Сборка проекта
	@echo Build...


#------------------------------------------------------------------------------------------------
# test 
#------------------------------------------------------------------------------------------------
test: ## TODO: Тестирование проекта
	@echo Test...


#------------------------------------------------------------------------------------------------
# clean 
#------------------------------------------------------------------------------------------------
clean: ## TODO: Очистка артефактов сборки проекта.
	@echo Cleanup repository...


#------------------------------------------------------------------------------------------------
# commit (Git) 
#------------------------------------------------------------------------------------------------
commit: ## Сделать проверяемый коммит через Commitizen (Git)
	@# Проверка наличия commitizen
	@if ! command -v cz >/dev/null 2>&1; then \
		echo "Ошибка: Commitizen не найден. Установите его: make install-commitizen"; \
		exit 1; \
	fi
	@cz commit

#------------------------------------------------------------------------------------------------
# push (Git) 
#------------------------------------------------------------------------------------------------
REMOTE ?= origin
BRANCH ?=

push: ## Отправить изменения в удаленную ветку (Git). Использование: make push [REMOTE=origin] [BRANCH=develop]
	@# Проверка, что находимся внутри git-репозитория
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		echo "Ошибка: текущий каталог не является git-репозиторием."; \
		exit 1; \
	fi
	@# Определение ветки для push
	@if [ -z "$(BRANCH)" ]; then \
		BRANCH=$$(git rev-parse --abbrev-ref HEAD); \
	else \
		BRANCH=$(BRANCH); \
	fi
	@# Проверка наличия remote
	@if ! git remote | grep -q "^$(REMOTE)$$"; then \
		echo "Ошибка: remote '$(REMOTE)' не найден."; \
		echo "Доступные remotes:"; \
		git remote; \
		exit 1; \
	fi
	@echo Отправка ветки $$BRANCH в $(REMOTE)...
	@git push $(REMOTE) $$BRANCH


#------------------------------------------------------------------------------------------------
# feature start (GitFlow) 
#------------------------------------------------------------------------------------------------
feature-start: ## Начать фичу: make feature-start <имя> (напр.: make feature-start ISSUE-123-desc)
	$(call check-feature-arg,feature-start)
	@# Проверка, что находимся внутри git-репозитория
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		echo "Ошибка: текущий каталог не является git-репозиторием."; \
		exit 1; \
	fi
	@# Проверка, что текущая ветка develop
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	if [ "$$current_branch" != "develop" ]; then \
		echo "Ошибка: feature-start можно вызывать только из ветки 'develop' (сейчас '$$current_branch')."; \
		exit 1; \
	fi
	@# Проверка, что рабочее дерево чистое
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Ошибка: рабочее дерево не чистое. Закоммитьте или откатите изменения перед стартом фичи."; \
		exit 1; \
	fi
	@# Проверка, что ветка feature/<имя> ещё не существует
	@if git rev-parse "feature/$(FEATURE_NAME)" >/dev/null 2>&1; then \
		echo "Ошибка: ветка 'feature/$(FEATURE_NAME)' уже существует."; \
		exit 1; \
	fi
	@echo Старт фичи $(FEATURE_NAME)...
	@git flow feature start "$(FEATURE_NAME)"


#------------------------------------------------------------------------------------------------
# feature finish (GitFlow) 
#------------------------------------------------------------------------------------------------
feature-finish: ## Завершить фичу и смержить в develop: make feature-finish <имя>
	$(call check-feature-arg,feature-finish)
	@# Проверка, что находимся внутри git-репозитория
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		echo "Ошибка: текущий каталог не является git-репозиторием."; \
		exit 1; \
	fi
	@# Проверка, что находимся в корректной feature-ветке
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	expected_branch="feature/$(FEATURE_NAME)"; \
	if [ "$$current_branch" != "$$expected_branch" ]; then \
		echo "Ошибка: feature-finish нужно вызывать из ветки '$$expected_branch' (сейчас '$$current_branch')."; \
		exit 1; \
	fi
	@# Проверка, что рабочее дерево чистое
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Ошибка: рабочее дерево не чистое. Закоммитьте или откатите изменения перед завершением фичи."; \
		exit 1; \
	fi
	@echo Завершение фичи $(FEATURE_NAME)...
	@git flow feature finish "$(FEATURE_NAME)"
	@if git remote | grep -q "^origin$$"; then \
		git push origin develop; \
	else \
		echo "Предупреждение: remote 'origin' не настроен, пропускаем push."; \
	fi


#------------------------------------------------------------------------------------------------
# release (GitFlow) 
#------------------------------------------------------------------------------------------------
release-start: ## Начать релиз: создать release/* ветку от develop (версия из version.json)
	@# Проверка, что находимся внутри git-репозитория
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		echo "Ошибка: текущий каталог не является git-репозиторием."; \
		exit 1; \
	fi
	@# Проверка, что текущая ветка develop
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	if [ "$$current_branch" != "develop" ]; then \
		echo "Ошибка: release-start можно вызывать только из ветки 'develop' (сейчас '$$current_branch')."; \
		exit 1; \
	fi
	@# Проверка, что рабочее дерево чистое
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Ошибка: рабочее дерево не чистое. Закоммитьте или откатите изменения перед стартом релиза."; \
		exit 1; \
	fi
	@# Проверка отсутствия существующего тега с такой версией
	@if git rev-parse "$(VERSION)" >/dev/null 2>&1 || git rev-parse "v$(VERSION)" >/dev/null 2>&1; then \
		echo "Ошибка: тег для версии '$(VERSION)' уже существует."; \
		exit 1; \
	fi
	@echo Старт релиза $(VERSION)...
	@git flow release start "$(VERSION)"

release-finish: ## Завершить релиз: теги, слияние в main/master и develop (версия из version.json)
	@# Проверка, что находимся внутри git-репозитория
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		echo "Ошибка: текущий каталог не является git-репозиторием."; \
		exit 1; \
	fi
	@# Проверка, что находимся в корректной release-ветке
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	expected_branch="release/$(VERSION)"; \
	if [ "$$current_branch" != "$$expected_branch" ]; then \
		echo "Ошибка: release-finish нужно вызывать из ветки '$$expected_branch' (сейчас '$$current_branch')."; \
		exit 1; \
	fi
	@# Проверка, что рабочее дерево чистое
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Ошибка: рабочее дерево не чистое. Закоммитьте или откатите изменения перед завершением релиза."; \
		exit 1; \
	fi
	@echo Завершение релиза $(VERSION)...
	@git flow release finish -m "Release $(VERSION)" "$(VERSION)"
	@if git remote | grep -q "^origin$$"; then \
		git push --all; \
		git push --tags; \
	else \
		echo "Предупреждение: remote 'origin' не настроен, пропускаем push."; \
	fi

#------------------------------------------------------------------------------------------------
# hotfix (GitFlow) 
#------------------------------------------------------------------------------------------------
HOTFIX ?=

hotfix-start: ## Начать хотфикс от main/master (HOTFIX=1.2.1)
	@if [ -z "$(HOTFIX)" ]; then echo "Укажите HOTFIX, напр.: HOTFIX=1.2.1"; exit 1; fi
	@# Проверка, что находимся внутри git-репозитория
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		echo "Ошибка: текущий каталог не является git-репозиторием."; \
		exit 1; \
	fi
	@# Проверка, что текущая ветка main/master
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	if [ "$$current_branch" != "main" ] && [ "$$current_branch" != "master" ]; then \
		echo "Ошибка: hotfix-start можно вызывать только из ветки 'main' или 'master' (сейчас '$$current_branch')."; \
		exit 1; \
	fi
	@# Проверка, что рабочее дерево чистое
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Ошибка: рабочее дерево не чистое. Закоммитьте или откатите изменения перед стартом хотфикса."; \
		exit 1; \
	fi
	@# Проверка отсутствия существующего тега с такой версией
	@if git rev-parse "$(HOTFIX)" >/dev/null 2>&1 || git rev-parse "v$(HOTFIX)" >/dev/null 2>&1; then \
		echo "Ошибка: тег для версии '$(HOTFIX)' уже существует."; \
		exit 1; \
	fi
	@echo Старт хотфикса $(HOTFIX)...
	@git flow hotfix start "$(HOTFIX)"

hotfix-finish: ## Завершить хотфикс: теги, слияние в main/master и develop (HOTFIX=1.2.1)
	@if [ -z "$(HOTFIX)" ]; then echo "Укажите HOTFIX, напр.: HOTFIX=1.2.1"; exit 1; fi
	@# Проверка, что находимся внутри git-репозитория
	@if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		echo "Ошибка: текущий каталог не является git-репозиторием."; \
		exit 1; \
	fi
	@# Проверка, что находимся в корректной hotfix-ветке
	@current_branch=$$(git rev-parse --abbrev-ref HEAD); \
	expected_branch="hotfix/$(HOTFIX)"; \
	if [ "$$current_branch" != "$$expected_branch" ]; then \
		echo "Ошибка: hotfix-finish нужно вызывать из ветки '$$expected_branch' (сейчас '$$current_branch')."; \
		exit 1; \
	fi
	@# Проверка, что рабочее дерево чистое
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Ошибка: рабочее дерево не чистое. Закоммитьте или откатите изменения перед завершением хотфикса."; \
		exit 1; \
	fi
	@echo Завершение хотфикса $(HOTFIX)...
	@git flow hotfix finish -m "Hotfix $(HOTFIX)" "$(HOTFIX)"
	@if git remote | grep -q "^origin$$"; then \
		git push --all; \
		git push --tags; \
	else \
		echo "Предупреждение: remote 'origin' не настроен, пропускаем push."; \
	fi
