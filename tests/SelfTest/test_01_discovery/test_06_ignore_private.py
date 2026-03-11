"""
Тест 6: Игнорирование приватных функций.

Проверяет, что функции с префиксом _ не считаются тестами,
даже если они используют декоратор @test.
"""

from utils.Tester.common.test_common import test, is_test_function


# Публичная тестовая функция (должна быть обнаружена)
@test("Публичный тест")
def test_public():
    assert True


# Приватная функция с декоратором @test (НЕ должна быть обнаружена)
@test("Приватный тест")
def _test_private():
    """Эта функция не должна считаться тестом из-за префикса _"""
    assert True


# Приватная функция без декоратора (не тест)
def _helper_private():
    return "private"


# Функция с именем, начинающимся с test_, но приватная
@test("Тест с подчеркиванием в начале")
def _test_also_private():
    assert True


# Вложенная приватная функция
class TestClass:
    @test("Приватный метод класса")
    def _test_private_method(self):
        assert True
    
    @test("Публичный метод класса")
    def test_public_method(self):
        assert True


# Проверочный тест
@test("Проверка игнорирования приватных функций")
def test_verify_private_ignored():
    """
    Проверяет, что приватные функции не помечены как тесты.
    """
    # Проверяем приватные функции
    assert not is_test_function(_test_private)
    assert not is_test_function(_test_also_private)
    assert not is_test_function(_helper_private)
    
    # Проверяем публичные
    assert is_test_function(test_public)
    assert is_test_function(TestClass().test_public_method)
    assert not is_test_function(TestClass()._test_private_method)