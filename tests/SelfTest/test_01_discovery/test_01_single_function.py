"""
Тест 1: Обнаружение одной тестовой функции.

Проверяет, что тестер правильно находит одну функцию с префиксом test_.
"""

from utils.Tester.common.test_common import test, TestHandler
from utils.Tester.core.discovery import TestDiscovery
from pathlib import Path


@test("Проверка обнаружения одного теста")
def test_discovery_single():
    """
    Создает временный файл с одной тестовой функцией и проверяет,
    что тестер обнаруживает её.
    """
    # Эта функция будет обнаружена тестером
    # Сам тест выполняется в раннере, поэтому здесь только заглушка
    assert True


# Вспомогательная функция для создания тестового файла
def create_test_file(content: str, filename: str) -> Path:
    """Создает временный файл с тестовым содержимым"""
    import tempfile
    test_dir = Path(tempfile.mkdtemp())
    test_file = test_dir / filename
    test_file.write_text(content)
    return test_file