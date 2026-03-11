"""
Тест 2: Обнаружение нескольких тестовых функций.

Проверяет, что тестер находит все функции с префиксом test_ в файле.
"""

from utils.Tester.common.test_common import test


@test("Первая тестовая функция")
def test_first():
    assert True


@test("Вторая тестовая функция")
def test_second():
    assert True


@test("Третья тестовая функция")
def test_third():
    assert True


# Обычная функция не должна быть обнаружена
def helper_function():
    return 42