"""
Тест 2: Runtime исключения.

Проверяет обработку различных типов исключений
во время выполнения тестов.
"""

from utils.Tester.common.test_common import test


@test("ZeroDivisionError")
def test_zero_division():
    """
    Тест с делением на ноль.
    """
    print("Пытаемся поделить на ноль...")
    result = 1 / 0
    print(f"Результат: {result}")  # Не выполнится


@test("KeyError")
def test_key_error():
    """
    Тест с обращением по несуществующему ключу словаря.
    """
    data = {"name": "Alice", "age": 30}
    print(f"Данные: {data}")
    
    # Этот ключ отсутствует
    value = data["address"]
    print(f"Адрес: {value}")


@test("IndexError")
def test_index_error():
    """
    Тест с обращением по несуществующему индексу списка.
    """
    items = [1, 2, 3]
    print(f"Список: {items}, длина: {len(items)}")
    
    # Индекс за пределами
    value = items[10]
    print(f"Значение: {value}")


@test("TypeError")
def test_type_error():
    """
    Тест с неверным типом данных.
    """
    # Сложение строки с числом
    result = "hello" + 42
    print(f"Результат: {result}")


@test("ValueError")
def test_value_error():
    """
    Тест с некорректным значением.
    """
    import math
    
    # Квадратный корень из отрицательного числа
    result = math.sqrt(-1)
    print(f"Результат: {result}")  # В Python это вернет NaN, не ошибку
    
    # Лучше так:
    int("not a number")  # ValueError


@test("AttributeError")
def test_attribute_error():
    """
    Тест с обращением к несуществующему атрибуту.
    """
    obj = object()
    print(f"Объект: {obj}")
    
    # Несуществующий атрибут
    obj.non_existent_attribute


@test("ImportError")
def test_import_error():
    """
    Тест с ошибкой импорта.
    """
    import sys
    print(f"sys.path: {sys.path[:2]}...")
    
    # Импорт несуществующего модуля
    import non_existent_module  # noqa


@test("NameError")
def test_name_error():
    """
    Тест с использованием неопределенной переменной.
    """
    print("Пытаемся использовать неопределенную переменную...")
    
    # Переменная не определена
    result = undefined_variable * 2
    print(f"Результат: {result}")


@test("RecursionError")
def test_recursion_error():
    """
    Тест с бесконечной рекурсией.
    """
    
    def recursive_function(depth):
        print(f"Глубина: {depth}")
        return recursive_function(depth + 1)
    
    # Бесконечная рекурсия
    recursive_function(1)


@test("Пользовательское исключение")
def test_custom_exception():
    """
    Тест с пользовательским исключением.
    """
    
    class CustomTestError(Exception):
        """Пользовательское исключение для тестов"""
        def __init__(self, code, message):
            self.code = code
            self.message = message
            super().__init__(f"[{code}] {message}")
    
    # Генерируем исключение
    raise CustomTestError(42, "Это тестовое исключение")


@test("Цепочка исключений")
def test_exception_chain():
    """
    Тест с цепочкой исключений (PEP 3134).
    """
    try:
        try:
            data = {"key": "value"}
            data["missing"]  # KeyError
        except KeyError as e:
            # Оборачиваем в другое исключение
            raise RuntimeError("Ошибка обработки данных") from e
    except RuntimeError:
        # Перехватываем и генерируем новое
        raise ValueError("Критическая ошибка в тесте")