"""
Тест 2: Запуск нескольких успешных тестов подряд.

Проверяет, что тестер корректно выполняет последовательность
успешных тестов и правильно собирает статистику.
"""

from utils.Tester.common.test_common import test
import time


# Счетчик для проверки порядка выполнения
_execution_counter = 0
_execution_order = []


@test("Первый успешный тест")
def test_first():
    """
    Первый тест в последовательности.
    """
    global _execution_counter, _execution_order
    _execution_counter += 1
    _execution_order.append("first")
    
    print(f"Выполнен тест #1, счетчик: {_execution_counter}")
    assert _execution_counter == 1
    assert 1 == 1


@test("Второй успешный тест")
def test_second():
    """
    Второй тест в последовательности.
    """
    global _execution_counter, _execution_order
    _execution_counter += 1
    _execution_order.append("second")
    
    print(f"Выполнен тест #2, счетчик: {_execution_counter}")
    assert _execution_counter == 2
    assert 2 + 2 == 4


@test("Третий успешный тест")
def test_third():
    """
    Третий тест в последовательности.
    """
    global _execution_counter, _execution_order
    _execution_counter += 1
    _execution_order.append("third")
    
    print(f"Выполнен тест #3, счетчик: {_execution_counter}")
    assert _execution_counter == 3
    assert "hello" + " world" == "hello world"


@test("Четвертый успешный тест с задержкой")
def test_fourth_slow():
    """
    Четвертый тест с небольшой задержкой.
    """
    global _execution_counter, _execution_order
    _execution_counter += 1
    _execution_order.append("fourth")
    
    time.sleep(0.1)  # 100ms задержка
    print(f"Выполнен тест #4 (медленный), счетчик: {_execution_counter}")
    assert _execution_counter == 4


@test("Пятый успешный тест с проверкой данных")
def test_fifth_with_data():
    """
    Пятый тест с более сложными проверками.
    """
    global _execution_counter, _execution_order
    _execution_counter += 1
    _execution_order.append("fifth")
    
    # Работа со словарями
    data = {"name": "test", "value": 42, "tags": ["a", "b", "c"]}
    
    assert data["name"] == "test"
    assert data["value"] == 42
    assert len(data["tags"]) == 3
    assert "b" in data["tags"]
    
    print(f"Выполнен тест #5, счетчик: {_execution_counter}")
    assert _execution_counter == 5


@test("Тест для проверки статистики")
def test_check_statistics():
    """
    Проверяет, что все тесты были выполнены.
    Этот тест выполняется последним.
    """
    global _execution_counter, _execution_order
    
    print(f"\nИтоговый счетчик: {_execution_counter}")
    print(f"Порядок выполнения: {_execution_order}")
    
    # Проверяем, что все 5 тестов выполнились
    assert _execution_counter == 5
    
    # Проверяем порядок (должен соответствовать объявлению)
    expected_order = ["first", "second", "third", "fourth", "fifth"]
    assert _execution_order == expected_order, \
        f"Ожидался порядок {expected_order}, получен {_execution_order}"