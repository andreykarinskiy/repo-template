#!/usr/bin/env python3
"""
Скрипт автотестирования шаблона Copier.

Проверяет генерацию проекта из шаблона:
1. Запускает copier copy с предопределенными ответами
2. Проверяет успешность выполнения команды
3. Проверяет наличие ожидаемых файлов
4. Проверяет содержимое ключевых файлов
5. Очищает результаты работы скрипта
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Tuple


# Тестовые данные для генерации проекта
TEST_DATA = {
    "project_name": "test-project",
    "project_description": "Test project description",
    "project_tags": "test, python, template",
    "author_name": "Test Author",
    "author_email": "test@example.com",
    "copyright_year": "2025",
}

# Путь к шаблону (относительно расположения скрипта)
SCRIPT_DIR = Path(__file__).parent.absolute()
TEMPLATE_DIR = SCRIPT_DIR.parent.absolute()

# Ожидаемые файлы и директории
EXPECTED_FILES = [
    "README.md",
    "PROFILE.yml",
    ".copier-answers.yml",
]

EXPECTED_DIRS = [
    "docs",
    "src",
    "tests",
    "scripts",
]


def run_copier_copy(template_path: Path, destination_path: Path, data: dict) -> Tuple[bool, str]:
    """
    Запускает команду copier copy с предопределенными данными.
    
    Args:
        template_path: Путь к шаблону
        destination_path: Путь к директории назначения
        data: Словарь с данными для подстановки
        
    Returns:
        Кортеж (успех, сообщение)
    """
    try:
        # Преобразуем данные в JSON строку для --data
        data_json = json.dumps(data)
        
        # Запускаем copier copy
        cmd = [
            "copier",
            "copy",
            str(template_path),
            str(destination_path),
            "--data",
            data_json,
            "--defaults",
            "--overwrite",
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.returncode != 0:
            return False, f"Команда завершилась с кодом {result.returncode}:\n{result.stderr}"
        
        return True, "Команда выполнена успешно"
        
    except FileNotFoundError:
        return False, "Команда copier не найдена. Убедитесь, что Copier установлен."
    except Exception as e:
        return False, f"Ошибка при выполнении команды: {str(e)}"


def check_files_exist(base_path: Path, files: list) -> Tuple[bool, list]:
    """
    Проверяет наличие файлов в директории.
    
    Args:
        base_path: Базовый путь
        files: Список файлов для проверки
        
    Returns:
        Кортеж (успех, список отсутствующих файлов)
    """
    missing = []
    for file in files:
        file_path = base_path / file
        if not file_path.exists():
            missing.append(file)
    
    return len(missing) == 0, missing


def check_dirs_exist(base_path: Path, dirs: list) -> Tuple[bool, list]:
    """
    Проверяет наличие директорий.
    
    Args:
        base_path: Базовый путь
        dirs: Список директорий для проверки
        
    Returns:
        Кортеж (успех, список отсутствующих директорий)
    """
    missing = []
    for dir_name in dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists() or not dir_path.is_dir():
            missing.append(dir_name)
    
    return len(missing) == 0, missing


def check_readme_content(readme_path: Path, test_data: dict) -> Tuple[bool, str]:
    """
    Проверяет содержимое README.md.
    
    Args:
        readme_path: Путь к файлу README.md
        test_data: Тестовые данные для проверки
        
    Returns:
        Кортеж (успех, сообщение об ошибке)
    """
    try:
        content = readme_path.read_text(encoding="utf-8")
        
        # Проверяем наличие project_name в заголовке
        if test_data["project_name"] not in content:
            return False, f"project_name '{test_data['project_name']}' не найден в README.md"
        
        # Проверяем наличие project_description
        if test_data["project_description"] not in content:
            return False, f"project_description не найден в README.md"
        
        # Проверяем наличие project_tags (если они есть)
        if test_data["project_tags"] and test_data["project_tags"] not in content:
            return False, f"project_tags не найдены в README.md"
        
        # Проверяем наличие author_name в блоке License
        if test_data["author_name"] not in content:
            return False, f"author_name '{test_data['author_name']}' не найден в README.md"
        
        # Проверяем наличие copyright_year в блоке License
        if test_data["copyright_year"] not in content:
            return False, f"copyright_year '{test_data['copyright_year']}' не найден в README.md"
        
        return True, "Содержимое README.md корректно"
        
    except Exception as e:
        return False, f"Ошибка при чтении README.md: {str(e)}"


def main():
    """Основная функция скрипта."""
    print("=" * 60)
    print("Автотестирование шаблона Copier")
    print("=" * 60)
    
    # Создаем временную директорию для тестирования
    with tempfile.TemporaryDirectory(prefix="copier_test_") as temp_dir:
        test_project_path = Path(temp_dir) / TEST_DATA["project_name"]
        
        print(f"\n1. Запуск copier copy...")
        print(f"   Шаблон: {TEMPLATE_DIR}")
        print(f"   Назначение: {test_project_path}")
        
        success, message = run_copier_copy(TEMPLATE_DIR, test_project_path, TEST_DATA)
        if not success:
            print(f"   ❌ ОШИБКА: {message}")
            sys.exit(1)
        
        print(f"   ✅ {message}")
        
        print(f"\n2. Проверка наличия файлов...")
        files_ok, missing_files = check_files_exist(test_project_path, EXPECTED_FILES)
        if not files_ok:
            print(f"   ❌ ОШИБКА: Отсутствуют файлы: {', '.join(missing_files)}")
            sys.exit(1)
        
        print(f"   ✅ Все файлы присутствуют")
        
        print(f"\n3. Проверка наличия директорий...")
        dirs_ok, missing_dirs = check_dirs_exist(test_project_path, EXPECTED_DIRS)
        if not dirs_ok:
            print(f"   ❌ ОШИБКА: Отсутствуют директории: {', '.join(missing_dirs)}")
            sys.exit(1)
        
        print(f"   ✅ Все директории присутствуют")
        
        print(f"\n4. Проверка содержимого README.md...")
        readme_path = test_project_path / "README.md"
        content_ok, content_message = check_readme_content(readme_path, TEST_DATA)
        if not content_ok:
            print(f"   ❌ ОШИБКА: {content_message}")
            sys.exit(1)
        
        print(f"   ✅ {content_message}")
        
        print(f"\n{'=' * 60}")
        print("✅ Все проверки пройдены успешно!")
        print(f"{'=' * 60}\n")
        
        # Временная директория будет автоматически удалена при выходе из with


if __name__ == "__main__":
    main()
