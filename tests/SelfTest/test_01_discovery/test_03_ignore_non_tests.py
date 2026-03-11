"""
Тест 3: Игнорирование функций без префикса test_.

Проверяет, что обычные функции не попадают в список тестов.
"""

from utils.Tester.common.test_common import test, get_test_metadata


# Тестовая функция
@test("Настоящий тест")
def test_real():
    assert True


# Обычные функции без декоратора @test
def normal_function():
    return "not a test"


def another_function(x, y):
    return x + y


class Helper:
    @staticmethod
    def utility():
        return "utility"


# Проверочная функция (будет найдена тестером)
@test("Проверка игнорирования не-тестов")
def test_verify_non_tests():
    """
    Эта функция выполняется раннером и проверяет метаданные.
    """
    # Проверяем, что у обычных функций нет метаданных теста
    assert not hasattr(normal_function, '_test_metadata')
    assert not hasattr(another_function, '_test_metadata')
    assert not hasattr(Helper.utility, '_test_metadata')