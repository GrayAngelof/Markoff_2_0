"""
Тест 4: Обработка неожиданных исключений.

Проверяет обработку различных неожиданных исключений.
"""

from utils.Tester.common.test_common import test
import time


_executed_tests = []
_exception_types = []


@test("Тест A - нормальный")
def test_a_normal():
    """
    Нормальный тест для базовой линии.
    """
    global _executed_tests
    _executed_tests.append("A")
    print("✅ Тест A выполнен")
    assert True


@test("Тест B - AttributeError")
def test_b_attribute_error():
    """
    Тест с обращением к несуществующему атрибуту.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("B")
    
    print("⏳ Тест B: обращение к несуществующему атрибуту")
    _exception_types.append("AttributeError")
    
    obj = object()
    obj.non_existent_attribute  # AttributeError
    
    assert True  # Не выполнится


@test("Тест C - TypeError")
def test_c_type_error():
    """
    Тест с неверным типом данных.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("C")
    
    print("⏳ Тест C: неверный тип данных")
    _exception_types.append("TypeError")
    
    result = "string" + 42  # TypeError
    
    assert True  # Не выполнится


@test("Тест D - ValueError")
def test_d_value_error():
    """
    Тест с некорректным значением.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("D")
    
    print("⏳ Тест D: некорректное значение")
    _exception_types.append("ValueError")
    
    int("not a number")  # ValueError
    
    assert True  # Не выполнится


@test("Тест E - IndexError")
def test_e_index_error():
    """
    Тест с выходом за границы списка.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("E")
    
    print("⏳ Тест E: выход за границы списка")
    _exception_types.append("IndexError")
    
    lst = [1, 2, 3]
    lst[10]  # IndexError
    
    assert True  # Не выполнится


@test("Тест F - KeyError")
def test_f_key_error():
    """
    Тест с несуществующим ключом словаря.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("F")
    
    print("⏳ Тест F: несуществующий ключ")
    _exception_types.append("KeyError")
    
    dct = {"a": 1, "b": 2}
    dct["c"]  # KeyError
    
    assert True  # Не выполнится


@test("Тест G - ZeroDivisionError")
def test_g_zero_division():
    """
    Тест с делением на ноль.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("G")
    
    print("⏳ Тест G: деление на ноль")
    _exception_types.append("ZeroDivisionError")
    
    result = 1 / 0  # ZeroDivisionError
    
    assert True  # Не выполнится


@test("Тест H - ImportError")
def test_h_import_error():
    """
    Тест с ошибкой импорта.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("H")
    
    print("⏳ Тест H: ошибка импорта")
    _exception_types.append("ImportError")
    
    import non_existent_module  # ImportError
    
    assert True  # Не выполнится


@test("Тест I - NameError")
def test_i_name_error():
    """
    Тест с неопределенной переменной.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("I")
    
    print("⏳ Тест I: неопределенная переменная")
    _exception_types.append("NameError")
    
    result = undefined_variable * 2  # NameError
    
    assert True  # Не выполнится


@test("Тест J - RecursionError")
def test_j_recursion_error():
    """
    Тест с бесконечной рекурсией.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("J")
    
    print("⏳ Тест J: бесконечная рекурсия")
    _exception_types.append("RecursionError")
    
    def recursive(n):
        return recursive(n + 1)
    
    recursive(0)  # RecursionError
    
    assert True  # Не выполнится


@test("Тест K - вложенные исключения")
def test_k_nested_exceptions():
    """
    Тест с вложенными исключениями разных типов.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("K")
    
    print("⏳ Тест K: вложенные исключения")
    
    try:
        try:
            data = [1, 2, 3]
            value = data[10]  # IndexError
        except IndexError:
            print("   Перехвачен IndexError, генерируем KeyError")
            dct = {"a": 1}
            value = dct["b"]  # KeyError
    except KeyError:
        print("   Перехвачен KeyError, генерируем TypeError")
        result = "string" + 42  # TypeError
    
    _exception_types.append("Nested")
    assert True  # Не выполнится


@test("Тест L - исключение в генераторе")
def test_l_generator_exception():
    """
    Тест с исключением внутри генератора.
    """
    global _executed_tests, _exception_types
    _executed_tests.append("L")
    
    def number_generator():
        for i in range(5):
            if i == 2:
                raise ValueError(f"Ошибка на итерации {i}")
            yield i
    
    print("⏳ Тест L: итерация по генератору")
    _exception_types.append("GeneratorError")
    
    for num in number_generator():
        print(f"   Получено: {num}")
    
    assert True  # Не выполнится


@test("Проверка обработки всех исключений")
def test_check_exception_handling():
    """
    Проверяет, что все исключения были обработаны.
    """
    global _executed_tests, _exception_types
    
    print(f"\n📋 Выполненные тесты: {_executed_tests}")
    print(f"📊 Типы исключений: {_exception_types}")
    
    # Проверяем, что все тесты были запущены
    expected_tests = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
    
    for test_name in expected_tests:
        if test_name in _executed_tests:
            print(f"   ✅ Тест {test_name} запущен")
        else:
            print(f"   ❌ Тест {test_name} не запущен")
    
    # Тест A должен быть выполнен
    assert "A" in _executed_tests
    
    # Должно быть минимум 11 тестов с исключениями
    exception_tests = [t for t in _executed_tests if t != "A"]
    print(f"\n📈 Тестов с исключениями: {len(exception_tests)}")
    assert len(exception_tests) >= 11
    
    # Проверяем разнообразие исключений
    print(f"\n🔍 Обнаруженные типы исключений:")
    for exc_type in set(_exception_types):
        print(f"   • {exc_type}")
    
    assert len(set(_exception_types)) >= 10
    
    assert True