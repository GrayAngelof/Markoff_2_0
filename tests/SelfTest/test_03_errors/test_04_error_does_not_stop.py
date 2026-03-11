"""
Тест 4: Ошибки не останавливают раннер.

Проверяет, что падение одного теста не останавливает
выполнение остальных тестов (если не включен fail-fast).
"""

from utils.Tester.common.test_common import test
import time


# Счетчик выполненных тестов
_executed_tests = []
_execution_counter = 0


@test("Первый тест - успешный")
def test_first_success():
    """
    Первый тест проходит успешно.
    """
    global _executed_tests, _execution_counter
    _execution_counter += 1
    _executed_tests.append("first_success")
    print(f"✅ Тест 1 (успех) - счетчик: {_execution_counter}")
    assert True


@test("Второй тест - падает с AssertionError")
def test_second_fail_assert():
    """
    Второй тест падает с AssertionError.
    """
    global _executed_tests, _execution_counter
    _execution_counter += 1
    _executed_tests.append("second_fail_assert")
    print(f"❌ Тест 2 (assert) - счетчик: {_execution_counter}")
    
    # Этот тест падает
    assert 1 == 2, "Этот тест должен упасть"


@test("Третий тест - успешный (должен выполниться)")
def test_third_success():
    """
    Третий тест должен выполниться, даже если второй упал.
    """
    global _executed_tests, _execution_counter
    _execution_counter += 1
    _executed_tests.append("third_success")
    print(f"✅ Тест 3 (успех) - счетчик: {_execution_counter}")
    assert "second_fail_assert" in _executed_tests
    assert True


@test("Четвертый тест - падает с исключением")
def test_fourth_fail_exception():
    """
    Четвертый тест падает с исключением.
    """
    global _executed_tests, _execution_counter
    _execution_counter += 1
    _executed_tests.append("fourth_fail_exception")
    print(f"❌ Тест 4 (исключение) - счетчик: {_execution_counter}")
    
    # Генерируем исключение
    raise ValueError("Это тестовое исключение")


@test("Пятый тест - успешный с задержкой")
def test_fifth_success_slow():
    """
    Пятый тест с задержкой должен выполниться.
    """
    global _executed_tests, _execution_counter
    _execution_counter += 1
    _executed_tests.append("fifth_success_slow")
    
    print(f"⏱️ Тест 5 (медленный) - счетчик: {_execution_counter}")
    time.sleep(0.2)
    assert True


@test("Шестой тест - падает с AssertionError")
def test_sixth_fail_another():
    """
    Шестой тест снова падает.
    """
    global _executed_tests, _execution_counter
    _execution_counter += 1
    _executed_tests.append("sixth_fail_another")
    print(f"❌ Тест 6 (еще один assert) - счетчик: {_execution_counter}")
    
    data = [1, 2, 3]
    assert len(data) == 5, f"Длина списка {len(data)}, ожидалось 5"


@test("Седьмой тест - успешный")
def test_seventh_success():
    """
    Седьмой тест должен выполниться последним.
    """
    global _executed_tests, _execution_counter
    _execution_counter += 1
    _executed_tests.append("seventh_success")
    print(f"✅ Тест 7 (успех) - счетчик: {_execution_counter}")
    assert True


@test("Проверка выполнения всех тестов")
def test_check_all_executed():
    """
    Проверяет, что все тесты были выполнены,
    несмотря на падения.
    """
    global _executed_tests, _execution_counter
    
    print(f"\n📋 Выполненные тесты ({len(_executed_tests)}):")
    for i, test_name in enumerate(_executed_tests, 1):
        status = "✅" if "success" in test_name else "❌"
        print(f"   {i}. {status} {test_name}")
    
    print(f"\n🔢 Счетчик: {_execution_counter}")
    
    # Должно быть выполнено 7 тестов
    expected_count = 7
    assert _execution_counter == expected_count, \
        f"Ожидалось {expected_count} тестов, выполнено {_execution_counter}"
    
    # Проверяем, что все тесты в списке
    expected_tests = [
        "first_success",
        "second_fail_assert",
        "third_success",
        "fourth_fail_exception",
        "fifth_success_slow",
        "sixth_fail_another",
        "seventh_success"
    ]
    
    for expected in expected_tests:
        assert expected in _executed_tests, f"Тест {expected} не выполнен"
    
    # Проверяем порядок (должен сохраняться)
    assert _executed_tests == expected_tests, \
        f"Порядок нарушен: {_executed_tests}"
    
    # Проверяем соотношение успешных/падающих
    passed = sum(1 for t in _executed_tests if "success" in t)
    failed = sum(1 for t in _executed_tests if "fail" in t)
    
    print(f"\n📊 Статистика:")
    print(f"   ✅ Успешных: {passed}")
    print(f"   ❌ Падающих: {failed}")
    print(f"   📈 Всего: {passed + failed}")
    
    assert passed == 4, f"Ожидалось 4 успешных, получено {passed}"
    assert failed == 3, f"Ожидалось 3 падающих, получено {failed}"