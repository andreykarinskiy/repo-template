#!/usr/bin/env bash
set -e
echo "Инициализация Git и GitFlow..."
if ! command -v git-flow >/dev/null 2>&1 && ! git flow version >/dev/null 2>&1; then
	echo "Ошибка: git-flow не найден. Установите git-flow:"
	echo "  Windows: входит в состав Git for Windows"
	echo "  Linux: sudo apt-get install git-flow или brew install git-flow"
	exit 1
fi
git init || true
if [ -z "$(git rev-list -n 1 --all 2>/dev/null)" ]; then
	echo "Создание начального коммита..."
	git commit --allow-empty -m "chore: Initial commit" || {
		echo "Ошибка: не удалось создать начальный коммит. Убедитесь, что git настроен (user.name и user.email)"
		exit 1
	}
fi
git checkout -b develop 2>/dev/null || git checkout develop || {
	echo "Ошибка: не удалось создать ветку develop"
	exit 1
}
git flow init -d || {
	echo "Ошибка: не удалось инициализировать GitFlow. Убедитесь, что git-flow установлен."
	exit 1
}
