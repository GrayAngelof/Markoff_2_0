"""
Тест 2: Точность измерения времени.

Проверяет приблизительную точность измерения времени выполнения.
Использует sleep для создания предсказуемых задержек.
"""

from utils.Tester.common.test_common import test
import time


# Допустимая погрешность (в процентах)
TOLERANCE_PERCENT = 20  # 20% погрешности допустимо


@test("Точность 10ms задержки")
def test_accuracy_10ms():
    """
    Проверяет точность измерения задержки 10ms.
    """
    delay = 0.010  # 10ms
    start = time.time()
    time.sleep(delay)
    elapsed = time.time() - start
    
    # Вычисляем погрешность в процентах
    error_percent = abs(elapsed - delay) / delay * 100
    
    print(f"🕒 Ожидалось: {delay*1000:.3f}ms")
    print(f"🕒 Получено:   {elapsed*1000:.3f}ms")
    print(f"📊 Погрешность: {error_percent:.1f}%")
    
    # Проверяем, что погрешность в допустимых пределах
    assert error_percent <= TOLERANCE_PERCENT, \
        f"Слишком большая погрешность: {error_percent:.1f}% > {TOLERANCE_PERCENT}%"
    
    # Дополнительно проверяем, что время не отрицательное
    assert elapsed >= 0


@test("Точность 50ms задержки")
def test_accuracy_50ms():
    """
    Проверяет точность измерения задержки 50ms.
    """
    delay = 0.050  # 50ms
    start = time.time()
    time.sleep(delay)
    elapsed = time.time() - start
    
    error_percent = abs(elapsed - delay) / delay * 100
    
    print(f"🕒 Ожидалось: {delay*1000:.3f}ms")
    print(f"🕒 Получено:   {elapsed*1000:.3f}ms")
    print(f"📊 Погрешность: {error_percent:.1f}%")
    
    assert error_percent <= TOLERANCE_PERCENT
    assert elapsed >= 0


@test("Точность 100ms задержки")
def test_accuracy_100ms():
    """
    Проверяет точность измерения задержки 100ms.
    """
    delay = 0.100  # 100ms
    start = time.time()
    time.sleep(delay)
    elapsed = time.time() - start
    
    error_percent = abs(elapsed - delay) / delay * 100
    
    print(f"🕒 Ожидалось: {delay*1000:.3f}ms")
    print(f"🕒 Получено:   {elapsed*1000:.3f}ms")
    print(f"📊 Погрешность: {error_percent:.1f}%")
    
    assert error_percent <= TOLERANCE_PERCENT
    assert elapsed >= 0


@test("Точность 200ms задержки")
def test_accuracy_200ms():
    """
    Проверяет точность измерения задержки 200ms.
    """
    delay = 0.200  # 200ms
    start = time.time()
    time.sleep(delay)
    elapsed = time.time() - start
    
    error_percent = abs(elapsed - delay) / delay * 100
    
    print(f"🕒 Ожидалось: {delay*1000:.3f}ms")
    print(f"🕒 Получено:   {elapsed*1000:.3f}ms")
    print(f"📊 Погрешность: {error_percent:.1f}%")
    
    assert error_percent <= TOLERANCE_PERCENT
    assert elapsed >= 0


@test("Точность 500ms задержки")
def test_accuracy_500ms():
    """
    Проверяет точность измерения задержки 500ms.
    """
    delay = 0.500  # 500ms
    start = time.time()
    time.sleep(delay)
    elapsed = time.time() - start
    
    error_percent = abs(elapsed - delay) / delay * 100
    
    print(f"🕒 Ожидалось: {delay*1000:.3f}ms")
    print(f"🕒 Получено:   {elapsed*1000:.3f}ms")
    print(f"📊 Погрешность: {error_percent:.1f}%")
    
    assert error_percent <= TOLERANCE_PERCENT
    assert elapsed >= 0


@test("Точность нескольких последовательных задержек")
def test_accuracy_sequence():
    """
    Проверяет точность при нескольких последовательных задержках.
    """
    delays = [0.010, 0.020, 0.030, 0.040, 0.050]
    total_delay = sum(delays)
    
    start = time.time()
    
    for i, delay in enumerate(delays):
        time.sleep(delay)
        print(f"  После задержки {i+1}: {time.time() - start:.4f}s")
    
    elapsed = time.time() - start
    error_percent = abs(elapsed - total_delay) / total_delay * 100
    
    print(f"🕒 Суммарная задержка: {total_delay*1000:.3f}ms")
    print(f"🕒 Общее время: {elapsed*1000:.3f}ms")
    print(f"📊 Погрешность: {error_percent:.1f}%")
    
    assert error_percent <= TOLERANCE_PERCENT
    assert elapsed >= total_delay * 0.8  # Не должно быть слишком быстро


@test("Стабильность измерений")
def test_measurement_stability():
    """
    Проверяет стабильность измерений при повторных замерах.
    """
    delays = []
    
    # Делаем несколько замеров одной и той же задержки
    for i in range(5):
        start = time.time()
        time.sleep(0.050)  # 50ms
        elapsed = time.time() - start
        delays.append(elapsed)
        print(f"  Замер {i+1}: {elapsed*1000:.3f}ms")
    
    # Вычисляем статистику
    avg_delay = sum(delays) / len(delays)
    min_delay = min(delays)
    max_delay = max(delays)
    variation = (max_delay - min_delay) / avg_delay * 100
    
    print(f"\n📊 Статистика:")
    print(f"  Среднее: {avg_delay*1000:.3f}ms")
    print(f"  Минимум: {min_delay*1000:.3f}ms")
    print(f"  Максимум: {max_delay*1000:.3f}ms")
    print(f"  Разброс: {variation:.1f}%")
    
    # Разброс не должен быть слишком большим
    assert variation <= 30, f"Слишком большой разброс: {variation:.1f}%"


@test("Минимальное измеряемое время")
def test_minimal_duration():
    """
    Проверяет, что даже очень быстрые тесты имеют ненулевое время.
    """
    # Очень быстрая операция
    x = 42
    y = x * x
    z = y / x
    
    # Время должно быть > 0
    # (это проверяется раннером, мы не можем здесь измерить)
    assert z == 42
    print("⏱️  Время этого теста должно быть > 0ms")