"""
Тест 5: Тестовые методы внутри классов.

Проверяет, что тестер правильно обнаруживает методы классов с префиксом test_.
"""

from utils.Tester.common.test_common import test


class TestMathOperations:
    """Класс с тестовыми методами"""
    
    @test("Проверка сложения")
    def test_addition(self):
        assert 1 + 1 == 2
    
    @test("Проверка вычитания")
    def test_subtraction(self):
        assert 5 - 3 == 2
    
    @test("Проверка умножения")
    def test_multiplication(self):
        assert 3 * 3 == 9
    
    # Обычный метод не должен быть тестом
    def helper_method(self):
        return "helper"


class TestStringOperations:
    """Еще один класс с тестами"""
    
    def setUp(self):
        self.test_string = "hello"
    
    @test("Проверка конкатенации")
    def test_concatenation(self):
        result = "hello" + " world"
        assert result == "hello world"
    
    @test("Проверка длины строки")
    def test_string_length(self):
        assert len("test") == 4
    
    # Статический метод с тестом
    @staticmethod
    @test("Статический тест")
    def test_static():
        assert True


class TestWithInheritance(TestMathOperations):
    """Наследованный класс с тестами"""
    
    @test("Тест в наследнике")
    def test_inherited(self):
        assert True
    
    # Переопределенный тест
    @test("Переопределенный тест сложения")
    def test_addition(self):
        assert 2 + 2 == 4