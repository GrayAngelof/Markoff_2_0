"""
Тест 3: Обработка медленных тестов.

Проверяет, что тестер корректно обрабатывает длительно выполняющиеся тесты
и правильно применяет таймауты.
"""

from utils.Tester.common.test_common import test
import time


@test("Медленный тест (0.5s)")
def test_slow_05s():
    """
    Тест с задержкой 0.5 секунды.
    """
    print("⏳ Медленный тест: ждем 0.5s...")
    time.sleep(0.5)
    print("✅ Готово")
    assert True


@test("Медленный тест (1s)")
def test_slow_1s():
    """
    Тест с задержкой 1 секунда.
    """
    print("⏳ Медленный тест: ждем 1s...")
    time.sleep(1.0)
    print("✅ Готово")
    assert True


@test("Медленный тест (2s)")
def test_slow_2s():
    """
    Тест с задержкой 2 секунды.
    """
    print("⏳ Медленный тест: ждем 2s...")
    time.sleep(2.0)
    print("✅ Готово")
    assert True


@test("Тест с вложенными задержками")
def test_nested_delays():
    """
    Тест с задержками на разных уровнях.
    """
    def level1():
        print("  level1: начало")
        time.sleep(0.2)
        level2()
        time.sleep(0.1)
        print("  level1: конец")
    
    def level2():
        print("    level2: начало")
        time.sleep(0.3)
        level3()
        time.sleep(0.1)
        print("    level2: конец")
    
    def level3():
        print("      level3: начало")
        time.sleep(0.4)
        print("      level3: конец")
    
    print("🏁 Старт теста с вложенными задержками")
    level1()
    print("🏁 Финиш")
    
    assert True


@test("Тест с прогрессивными задержками")
def test_progressive_delays():
    """
    Тест с увеличивающимися задержками.
    """
    for i in range(1, 5):
        delay = i * 0.2  # 0.2s, 0.4s, 0.6s, 0.8s
        print(f"  Итерация {i}: задержка {delay}s")
        time.sleep(delay)
    
    assert True


@test("Тест с циклическими вычислениями")
def test_computation_slow():
    """
    Тест, медленный из-за вычислений, а не sleep.
    """
    print("🧮 Выполняем тяжелые вычисления...")
    
    result = 0
    for i in range(1_000_000):
        result += (i * i) % 1000
    
    print(f"✅ Результат: {result}")
    
    assert result > 0


@test("Тест с таймаутом 0.5s", timeout=0.5)
def test_with_timeout_half_second():
    """
    Тест с явным таймаутом 0.5s.
    Должен пройти, так как спит меньше.
    """
    print("⏱️  Тест с таймаутом 0.5s, спим 0.3s")
    time.sleep(0.3)
    assert True


@test("Тест с таймаутом 0.3s", timeout=0.3)
def test_with_timeout_should_fail():
    """
    Тест с явным таймаутом 0.3s.
    Должен упасть по таймауту, так как спит 0.5s.
    """
    print("⏱️  Тест с таймаутом 0.3s, спим 0.5s")
    print("   (должен упасть по таймауту)")
    time.sleep(0.5)
    assert True  # Не должно выполниться


@test("Тест с точно на грани таймаута", timeout=0.5)
def test_edge_timeout():
    """
    Тест на грани таймаута (0.5s таймаут, 0.49s sleep).
    """
    print("⏱️  Тест на грани таймаута: 0.49s sleep при таймауте 0.5s")
    time.sleep(0.49)
    assert True


@test("Тест с задержкой и выводом")
def test_slow_with_output():
    """
    Медленный тест с периодическим выводом.
    """
    print("🚀 Запуск медленного теста с выводом")
    
    for i in range(5):
        time.sleep(0.2)
        print(f"  Итерация {i+1}/5: прошло {(i+1)*0.2:.1f}s")
    
    print("✅ Завершено")
    assert True


@test("Очень медленный тест (3s)")
def test_very_slow_3s():
    """
    Очень медленный тест 3 секунды.
    """
    print("🐢 Очень медленный тест: 3s")
    
    for i in range(3):
        time.sleep(1.0)
        print(f"  Прошло {i+1}s")
    
    assert True


@test("Проверка кумулятивного времени")
def test_cumulative_time():
    """
    Проверяет, что время всех тестов суммируется корректно.
    """
    total_delay = 0
    
    for i in range(5):
        delay = 0.1
        time.sleep(delay)
        total_delay += delay
        print(f"  После {i+1} итераций: суммарно {total_delay:.1f}s")
    
    print(f"📊 Общая задержка в тесте: {total_delay:.1f}s")
    assert total_delay == 0.5


@test("Тест с переменной скоростью")
def test_variable_speed():
    """
    Тест с переменной скоростью выполнения.
    """
    import math
    
    start = time.time()
    
    # Вычисления с увеличивающейся сложностью
    for i in range(1, 6):
        iterations = i * 100000
        print(f"  Итерация {i}: {iterations} вычислений")
        
        result = 0
        for j in range(iterations):
            result += math.sin(j) * math.cos(j)
        
        elapsed = time.time() - start
        print(f"    Прошло: {elapsed:.2f}s, результат: {result:.2f}")
    
    assert True


@test("Проверка времени последнего теста")
def test_last_timing():
    """
    Последний тест для проверки общего времени сессии.
    """
    print("\n📋 Сводка по медленным тестам:")
    print("  • test_slow_05s: 0.5s")
    print("  • test_slow_1s: 1.0s")
    print("  • test_slow_2s: 2.0s")
    print("  • test_very_slow_3s: 3.0s")
    print("  • и другие...")
    
    assert True