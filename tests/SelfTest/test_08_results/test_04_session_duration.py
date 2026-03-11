"""
Тест 4: Длительность сессии.

Проверяет корректный расчет общего времени тестовой сессии.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestSession, TestResult, TestOutput
from utils.Tester.core.models import TestFunction
import time
import threading


def create_test_func(name: str) -> TestFunction:
    """Создает тестовую функцию."""
    def dummy():
        pass
    return TestFunction(
        name=name,
        description="",
        func=dummy,
        module_path="test.duration",
        file_path=None,
        line_number=42
    )


@test("Длительность пустой сессии")
def test_empty_session_duration():
    """
    Проверяет длительность пустой сессии.
    """
    session = TestSession(name="Empty")
    
    start = time.time()
    time.sleep(0.1)
    session.finish()
    end = time.time()
    
    # Длительность должна быть примерно равна задержке
    assert session.duration > 0.05
    assert session.duration < 0.2
    
    # Суммарное время тестов должно быть 0
    assert session.total_time == 0
    
    print(f"⏱️  Длительность пустой сессии: {session.duration:.3f}s")
    assert True


@test("Длительность с одним тестом")
def test_single_test_duration():
    """
    Проверяет длительность сессии с одним тестом.
    """
    session = TestSession(name="Single Test")
    
    # Добавляем тест с известной длительностью
    test_func = create_test_func("test_single")
    result = TestResult(
        test=test_func,
        success=True,
        duration=0.3,  # 300ms
        output=TestOutput(),
        error=None
    )
    
    session.add_result(result)
    
    time.sleep(0.1)  # Пауза между тестами
    session.finish()
    
    # Длительность сессии должна включать время теста + паузу
    assert session.duration > 0.35
    assert session.duration < 0.45
    assert session.total_time == 0.3
    
    print(f"⏱️  Длительность сессии: {session.duration:.3f}s")
    print(f"⏱️  Суммарное время тестов: {session.total_time:.3f}s")
    print(f"⏱️  Накладные расходы: {session.duration - session.total_time:.3f}s")
    
    assert True


@test("Длительность с несколькими тестами")
def test_multiple_tests_duration():
    """
    Проверяет длительность сессии с несколькими тестами.
    """
    session = TestSession(name="Multiple Tests")
    
    # Добавляем тесты с разной длительностью
    durations = [0.1, 0.2, 0.15, 0.25, 0.3]
    
    for i, d in enumerate(durations):
        test_func = create_test_func(f"test_{i}")
        result = TestResult(
            test=test_func,
            success=True,
            duration=d,
            output=TestOutput(),
            error=None
        )
        session.add_result(result)
        time.sleep(0.05)  # Пауза между добавлениями
    
    session.finish()
    
    expected_total = sum(durations)
    assert abs(session.total_time - expected_total) < 0.01
    
    # Длительность сессии должна быть больше суммы (из-за пауз)
    assert session.duration > session.total_time
    
    overhead = session.duration - session.total_time
    overhead_percent = (overhead / session.duration) * 100
    
    print(f"⏱️  Всего тестов: {len(durations)}")
    print(f"⏱️  Суммарное время тестов: {session.total_time:.3f}s")
    print(f"⏱️  Длительность сессии: {session.duration:.3f}s")
    print(f"⏱️  Накладные расходы: {overhead:.3f}s ({overhead_percent:.1f}%)")
    
    assert True


@test("Точность измерения длительности")
def test_duration_accuracy():
    """
    Проверяет точность измерения длительности.
    """
    session = TestSession(name="Accuracy Test")
    
    # Точные задержки
    delays = [0.05, 0.1, 0.15, 0.2, 0.25]
    
    start_total = time.time()
    
    for i, delay in enumerate(delays):
        test_start = time.time()
        time.sleep(delay)
        test_duration = time.time() - test_start
        
        test_func = create_test_func(f"test_{i}")
        result = TestResult(
            test=test_func,
            success=True,
            duration=test_duration,
            output=TestOutput(),
            error=None
        )
        session.add_result(result)
    
    session.finish()
    total_duration = time.time() - start_total
    
    # Проверяем, что сумма длительностей тестов примерно равна
    # времени, проведенному в sleep
    assert abs(session.total_time - sum(delays)) < 0.05
    
    # Общая длительность должна быть больше суммы (из-за накладных расходов)
    assert total_duration > session.total_time
    
    print(f"\n📊 Точность измерений:")
    for i, result in enumerate(session.results):
        error = abs(result.duration - delays[i])
        error_percent = (error / delays[i]) * 100
        print(f"   Тест {i}: ожидалось {delays[i]*1000:.1f}ms, "
              f"получено {result.duration*1000:.1f}ms "
              f"(погрешность {error_percent:.1f}%)")
    
    assert True


@test("Длительность с параллельным выполнением")
def test_parallel_duration():
    """
    Проверяет длительность при имитации параллельного выполнения.
    """
    session = TestSession(name="Parallel Test")
    
    # Функция для имитации работы в потоке
    def worker(thread_id, duration):
        start = time.time()
        time.sleep(duration)
        test_duration = time.time() - start
        
        test_func = create_test_func(f"thread_{thread_id}")
        result = TestResult(
            test=test_func,
            success=True,
            duration=test_duration,
            output=TestOutput(),
            error=None
        )
        # В реальности результаты добавляются в главном потоке
        return result
    
    # Запускаем "параллельные" тесты последовательно
    # (для теста мы просто добавляем результаты)
    durations = [0.2, 0.3, 0.1, 0.4, 0.25]
    
    start_time = time.time()
    
    for i, d in enumerate(durations):
        result = worker(i, d)
        session.add_result(result)
    
    session.finish()
    elapsed = time.time() - start_time
    
    # Суммарное время должно быть примерно равно сумме длительностей
    assert abs(session.total_time - sum(durations)) < 0.05
    
    # Общее время выполнения должно быть примерно равно сумме
    # (так как выполняем последовательно)
    assert abs(elapsed - session.total_time) < 0.1
    
    print(f"\n⏱️  Последовательное выполнение:")
    print(f"   Суммарное время тестов: {session.total_time:.3f}s")
    print(f"   Реальное время: {elapsed:.3f}s")
    
    assert True


@test("Длительность с учетом пауз между тестами")
def test_pauses_between_tests():
    """
    Проверяет учет пауз между тестами в длительности сессии.
    """
    session = TestSession(name="With Pauses")
    
    # Добавляем тесты с паузами между ними
    test_durations = [0.1, 0.2, 0.15]
    pauses = [0.05, 0.1, 0.08]  # Паузы между тестами
    
    total_sleep = 0
    
    for i, d in enumerate(test_durations):
        # Имитация выполнения теста
        time.sleep(d)
        total_sleep += d
        
        test_func = create_test_func(f"test_{i}")
        result = TestResult(
            test=test_func,
            success=True,
            duration=d,
            output=TestOutput(),
            error=None
        )
        session.add_result(result)
        
        # Пауза после теста (кроме последнего)
        if i < len(test_durations) - 1:
            time.sleep(pauses[i])
            total_sleep += pauses[i]
    
    session.finish()
    
    # Общее время сна должно быть примерно равно сумме
    assert abs(total_sleep - (sum(test_durations) + sum(pauses))) < 0.05
    
    # Длительность сессии должна быть не меньше общего времени сна
    assert session.duration >= total_sleep - 0.05
    
    print(f"\n⏱️  С учетом пауз:")
    print(f"   Суммарное время тестов: {sum(test_durations):.3f}s")
    print(f"   Паузы между тестами: {sum(pauses):.3f}s")
    print(f"   Общее время сна: {total_sleep:.3f}s")
    print(f"   Длительность сессии: {session.duration:.3f}s")
    
    assert True