"""
Тест 1: Запуск одного успешного теста.

Проверяет, что тестер корректно выполняет один тест,
который должен пройти успешно.
"""

from utils.Tester.common.test_common import test, TestHandler
import time


@test("Успешный тест с простыми проверками")
def test_simple_success():
    """
    Простейший успешный тест с базовыми assert'ами.
    """
    # Арифметика
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5
    
    # Строки
    assert "hello".upper() == "HELLO"
    assert "WORLD".lower() == "world"
    
    # Списки
    assert len([1, 2, 3]) == 3
    assert [1, 2, 3][0] == 1
    
    print("Тест успешно выполнен")
    return True  # возвращаемое значение игнорируется


@test("Тест с обработчиком событий")
def test_with_handler():
    """
    Тест с использованием TestHandler для проверки событий.
    """
    handler = TestHandler("test_handler")
    
    # Эмулируем события
    handler.handle({"type": "event1", "data": 42})
    handler.handle({"type": "event2", "data": 43})
    handler.handle({"type": "event1", "data": 44})
    
    # Проверяем
    assert handler.count() == 3
    assert handler.count("event1") == 2
    assert handler.count("event2") == 1
    
    last = handler.last()
    assert last is not None
    assert last["type"] == "event1"
    assert last["data"] == 44
    
    print(f"Обработано событий: {handler.count()}")


@test("Тест с временной меткой")
def test_with_timestamp():
    """
    Тест, использующий время (проверка детерминизма).
    """
    import time
    from datetime import datetime
    
    start = time.time()
    time.sleep(0.01)  # 10ms
    end = time.time()
    
    assert end > start
    assert end - start >= 0.01
    
    # Проверка datetime
    now = datetime.now()
    assert now.year >= 2024