"""
Тест 7: Пустой файл без тестов.

Проверяет поведение тестера при загрузке файла, не содержащего тестов.
"""

# В этом файле нет ни одного теста
# Только комментарии и импорты

from utils.Tester.common.test_common import test

# Обычная функция без декоратора
def utility_function():
    return "utility"

# Константы
EMPTY_FILE_CONSTANT = 42

# Класс без тестов
class HelperClass:
    @staticmethod
    def help():
        return "help"

# Даже если есть функция с именем test_, но без декоратора
def test_looking_function():
    """Эта функция не помечена @test, поэтому не должна быть тестом"""
    return "not a test"

# Если раскомментировать следующий код, файл перестанет быть пустым:
# @test("Настоящий тест")
# def test_real():
#     assert True