# Инструкция по использованию шаблона

## Предварительные требования

Для использования шаблона необходимо установить следующие инструменты:

### 1. Python

Требуется Python 3.8 или выше.

**Проверка установки:**
```bash
python --version
# или
python3 --version
```

**Установка:**
- **Windows**: Скачайте установщик с [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python3`
- **Linux**: `sudo apt-get install python3` (Ubuntu/Debian) или `sudo yum install python3` (RHEL/CentOS)

### 2. pipx (рекомендуется)

`pipx` позволяет устанавливать приложения Python в изолированном окружении.

**Установка:**
```bash
# Windows
pip install pipx
pipx ensurepath

# macOS
brew install pipx
pipx ensurepath

# Linux
python3 -m pip install --user pipx
python3 -m pip ensurepath --user
```

### 3. Copier

Установка Copier через pipx (рекомендуемый способ):
```bash
pipx install copier
```

Альтернативный способ через pip:
```bash
pip install copier
```

**Проверка установки:**
```bash
copier --version
```

## Создание нового проекта

Для создания нового проекта на основе шаблона выполните команду:

```bash
copier copy https://github.com/andreykarinskiy/repo-template.git path/to/your-project
```

Где:
- `https://github.com/andreykarinskiy/repo-template.git` — URL репозитория с шаблоном
- `path/to/your-project` — путь к директории, где будет создан новый проект

После выполнения команды Copier запросит у вас значения для параметров проекта.

## Описание параметров

При создании проекта вам будет предложено ввести следующие параметры:

### `project_name`
- **Тип**: строка
- **Описание**: Имя вашего проекта
- **Пример**: `my-awesome-project`
- **Обязательный**: Да

### `project_description`
- **Тип**: строка
- **Описание**: Краткое описание проекта
- **Пример**: `Проект для автоматизации процессов разработки`
- **Обязательный**: Да

### `project_tags`
- **Тип**: строка (список значений, разделенных запятыми)
- **Описание**: Теги проекта для категоризации (может быть пустым)
- **Пример**: `python, web, api` или `backend, microservices, docker`
- **Обязательный**: Нет (по умолчанию: пустая строка)

### `author_name`
- **Тип**: строка
- **Описание**: Имя автора проекта
- **Пример**: `Иван Иванов`
- **Примечание**: Можно получить автоматически из git config: `git config user.name`
- **Обязательный**: Нет (по умолчанию: пустая строка)

### `author_email`
- **Тип**: строка
- **Описание**: Email автора проекта
- **Пример**: `ivan.ivanov@example.com`
- **Примечание**: Можно получить автоматически из git config: `git config user.email`
- **Обязательный**: Нет (по умолчанию: пустая строка)

### `copyright_year`
- **Тип**: строка
- **Описание**: Год для копирайта в файлах лицензии
- **Пример**: `2025`
- **Обязательный**: Нет (по умолчанию: текущий год)

## Пример использования

```bash
# Создание нового проекта
copier copy https://github.com/andreykarinskiy/repo-template.git my-project

# В процессе генерации вам будет предложено ввести:
# project_name: my-project
# project_description: Мой новый проект
# project_tags: python, web
# author_name: Иван Иванов
# author_email: ivan@example.com
# copyright_year: 2025
```

## Обновление шаблона

Если шаблон был обновлен, вы можете обновить существующий проект до новой версии.

### Автоматическое обновление

Перейдите в корневую директорию вашего проекта и выполните:

```bash
copier update
```

Copier автоматически определит источник шаблона из файла `.copier-answers.yml` и предложит применить изменения.

### Ручное указание источника

Если необходимо указать источник шаблона явно:

```bash
copier update https://github.com/andreykarinskiy/repo-template.git
```

### Процесс обновления

1. Copier проанализирует изменения в шаблоне
2. Предложит вам выбрать, какие изменения применить (если есть конфликты)
3. Применит обновления к вашему проекту
4. Сохранит ваши ответы на вопросы в `.copier-answers.yml`

**Важно**: Рекомендуется создать резервную копию проекта перед обновлением, особенно если в проекте были внесены значительные изменения.

## Дополнительная информация

- Документация Copier: https://copier.readthedocs.io/
- Репозиторий шаблона: https://github.com/andreykarinskiy/repo-template
