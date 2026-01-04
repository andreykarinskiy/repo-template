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

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import yaml
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


def check_readme_content(readme_path: Path, test_data: dict, profile_path: Path = None) -> Tuple[bool, str]:
    """
    Проверяет содержимое README.md.
    
    Args:
        readme_path: Путь к файлу README.md
        test_data: Тестовые данные для проверки
        profile_path: Путь к файлу PROFILE.yml для проверки атрибутов
        
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
        
        # Проверяем атрибуты из PROFILE.yml, если файл указан
        if profile_path and profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile = yaml.safe_load(f)
            
            # Проверяем наличие organization
            if profile.get('organization'):
                if profile['organization'] not in content:
                    return False, f"organization '{profile['organization']}' не найден в README.md"
            
            # Проверяем наличие contact
            contact = profile.get('contact', {})
            if contact.get('email') and contact['email'] not in content:
                return False, f"contact.email '{contact['email']}' не найден в README.md"
            if contact.get('telegram_id') and contact['telegram_id'] not in content:
                return False, f"contact.telegram_id '{contact['telegram_id']}' не найден в README.md"
            
            # Проверяем наличие author (имя автора из PROFILE.yml может использоваться в License)
            author = profile.get('author', {})
            if author.get('name') and author['name'] not in content:
                return False, f"author.name '{author['name']}' не найден в README.md"
        
        return True, "Содержимое README.md корректно"
        
    except Exception as e:
        return False, f"Ошибка при чтении README.md: {str(e)}"


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(
        description="Скрипт автотестирования шаблона Copier"
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="Не удалять временную директорию после выполнения тестов (полезно для отладки)"
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("Автотестирование шаблона Copier")
    print("=" * 60)
    
    # Создаем временную директорию для тестирования
    temp_dir = tempfile.mkdtemp(prefix="copier_test_")
    test_project_path = Path(temp_dir) / TEST_DATA["project_name"]
    
    try:
        print(f"\n1. Запуск copier copy...")
        print(f"   Шаблон: {TEMPLATE_DIR}")
        print(f"   Назначение: {test_project_path}")
        
        success, message = run_copier_copy(TEMPLATE_DIR, test_project_path, TEST_DATA)
        if not success:
            print(f"   [ERROR] {message}")
            sys.exit(1)
        
        print(f"   [OK] {message}")
        
        print(f"\n2. Проверка наличия файлов...")
        files_ok, missing_files = check_files_exist(test_project_path, EXPECTED_FILES)
        if not files_ok:
            print(f"   [ERROR] Отсутствуют файлы: {', '.join(missing_files)}")
            sys.exit(1)
        
        print(f"   [OK] Все файлы присутствуют")
        
        print(f"\n3. Проверка наличия директорий...")
        dirs_ok, missing_dirs = check_dirs_exist(test_project_path, EXPECTED_DIRS)
        if not dirs_ok:
            print(f"   [ERROR] Отсутствуют директории: {', '.join(missing_dirs)}")
            sys.exit(1)
        
        print(f"   [OK] Все директории присутствуют")
        
        print(f"\n4. Проверка содержимого README.md...")
        readme_path = test_project_path / "README.md"
        profile_path = test_project_path / "PROFILE.yml"
        content_ok, content_message = check_readme_content(readme_path, TEST_DATA, profile_path)
        if not content_ok:
            print(f"   [ERROR] {content_message}")
            sys.exit(1)
        
        print(f"   [OK] {content_message}")
        
        print(f"\n{'=' * 60}")
        print("[OK] Все проверки пройдены успешно!")
        print(f"{'=' * 60}\n")
        
    finally:
        # Удаляем временную директорию, если флаг --keep не установлен
        if not args.keep:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"\n[WARNING] Не удалось удалить временную директорию {temp_dir}: {e}")
        else:
            print(f"\n[INFO] Временная директория сохранена: {test_project_path}")


if __name__ == "__main__":
    main()
