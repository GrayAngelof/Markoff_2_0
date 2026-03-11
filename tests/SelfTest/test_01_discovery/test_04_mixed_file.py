"""
Тест 4: Смешанный файл с тестами и обычным кодом.

Проверяет корректное выделение тестов из файла с примесью обычного кода.
"""

from utils.Tester.common.test_common import test, TestHandler


# Константы для тестов
TEST_CONSTANT = 42
TEST_MESSAGE = "Hello from test"


def setup_function():
    """Вспомогательная функция для подготовки данных"""
    return {"data": TEST_CONSTANT}


def teardown_function():
    """Вспомогательная функция для очистки"""
    pass


@test("Тест с использованием констант")
def test_with_constants():
    assert TEST_CONSTANT == 42
    assert TEST_MESSAGE == "Hello from test"


class TestHelper:
    """Вспомогательный класс для тестов"""
    
    @staticmethod
    def prepare():
        return [1, 2, 3]
    
    @classmethod
    def class_helper(cls):
        return "class helper"


@test("Тест с использованием хелпера")
def test_with_helper():
    data = TestHelper.prepare()
    assert len(data) == 3
    assert TestHelper.class_helper() == "class helper"


@test("Еще один тест")
def test_another():
    setup = setup_function()
    assert setup["data"] == 42
    teardown_function()


# Обычный код после тестов
if __name__ == "__main__":
    print("Этот блок не должен влиять на обнаружение тестов")