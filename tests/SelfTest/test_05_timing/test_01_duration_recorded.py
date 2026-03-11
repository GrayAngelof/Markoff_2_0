"""
Тест 1: Запись времени выполнения.

Проверяет, что тестер записывает время выполнения каждого теста
и что время имеет разумные значения.
"""

from utils.Tester.common.test_common import test
import time


@test("Очень быстрый тест")
def test_very_fast():
    """
    Тест, который выполняется мгновенно.
    """
    # Простая операция
    x = 42
    y = x * 2
    z = y / 2
    
    assert z == 42
    
    # Время должно быть очень маленьким (< 1ms)


@test("Тест с микро-задержкой")
def test_micro_delay():
    """
    Тест с очень маленькой задержкой.
    """
    time.sleep(0.001)  # 1ms
    assert True


@test("Тест с миллисекундной задержкой")
def test_millisecond_delay():
    """
    Тест с задержкой в несколько миллисекунд.
    """
    time.sleep(0.010)  # 10ms
    assert True


@test("Тест с короткой задержкой")
def test_short_delay():
    """
    Тест с задержкой 50ms.
    """
    time.sleep(0.050)  # 50ms
    assert True


@test("Тест со средней задержкой")
def test_medium_delay():
    """
    Тест с задержкой 100ms.
    """
    time.sleep(0.100)  # 100ms
    assert True


@test("Тест с разными операциями")
def test_mixed_operations():
    """
    Тест с mix быстрых операций и небольших задержек.
    """
    # Быстрые вычисления
    result = 0
    for i in range(1000):
        result += i
    
    # Небольшая задержка
    time.sleep(0.020)  # 20ms
    
    # Еще вычисления
    data = [x * 2 for x in range(500)]
    
    # Еще задержка
    time.sleep(0.030)  # 30ms
    
    assert result == 499500
    assert len(data) == 500


@test("Проверка времени выполнения")
def test_check_duration():
    """
    Этот тест не выполняется напрямую, а служит для проверки,
    что раннер записывает время.
    """
    start = time.time()
    
    # Небольшая работа
    for i in range(10000):
        _ = i * i
    
    end = time.time()
    elapsed = (end - start) * 1000  # в миллисекундах
    
    print(f"🕒 Измеренное время в тесте: {elapsed:.3f}ms")
    
    # Время должно быть записано раннером
    assert True