"""
Тест 4: Порядок выполнения тестов.

Проверяет, что тесты выполняются в ожидаемом порядке
(обычно в порядке объявления в файле).
"""

from utils.Tester.common.test_common import test
import time


# Глобальный список для отслеживания порядка
_execution_log = []
_execution_times = {}


@test("Тест A - первый по алфавиту")
def test_a_first():
    """
    Тест с именем, начинающимся на 'a'.
    Должен выполняться первым, если порядок по алфавиту.
    """
    global _execution_log
    _execution_log.append("A")
    _execution_times["A"] = time.time()
    print("🔤 Тест A выполнен")


@test("Тест B - второй по алфавиту")
def test_b_second():
    """
    Тест с именем, начинающимся на 'b'.
    Должен выполняться вторым.
    """
    global _execution_log
    _execution_log.append("B")
    _execution_times["B"] = time.time()
    print("🔤 Тест B выполнен")
    
    # Проверяем, что A был до B
    assert "A" in _execution_log
    assert _execution_log.index("A") < _execution_log.index("B")


@test("Тест C - третий по алфавиту")
def test_c_third():
    """
    Тест с именем, начинающимся на 'c'.
    Должен выполняться третьим.
    """
    global _execution_log
    _execution_log.append("C")
    _execution_times["C"] = time.time()
    print("🔤 Тест C выполнен")
    
    # Проверяем порядок
    assert _execution_log.index("B") < _execution_log.index("C")


@test("Тест с задержкой")
def test_with_delay():
    """
    Тест с искусственной задержкой.
    Проверяет, что задержка не влияет на порядок.
    """
    global _execution_log
    _execution_log.append("DELAY")
    
    time.sleep(0.2)  # 200ms задержка
    _execution_times["DELAY"] = time.time()
    print("⏱️ Тест с задержкой выполнен")


@test("Быстрый тест после задержки")
def test_fast_after_delay():
    """
    Быстрый тест, который идет после теста с задержкой.
    Должен выполняться после него, несмотря на скорость.
    """
    global _execution_log
    _execution_log.append("FAST")
    _execution_times["FAST"] = time.time()
    print("⚡ Быстрый тест выполнен")
    
    # Проверяем, что DELAY был до FAST
    assert _execution_log.index("DELAY") < _execution_log.index("FAST")


@test("Тест для проверки временных меток")
def test_check_timestamps():
    """
    Проверяет временные метки выполнения тестов.
    """
    print("\n📋 Лог выполнения:")
    for i, test_name in enumerate(_execution_log, 1):
        print(f"   {i}. {test_name}")
    
    print("\n⏱️  Временные метки:")
    for test_name, timestamp in _execution_times.items():
        print(f"   {test_name}: {timestamp:.6f}")
    
    # Проверяем общее количество тестов
    expected_tests = ["A", "B", "C", "DELAY", "FAST"]
    assert len(_execution_log) == len(expected_tests)
    
    # Проверяем, что все ожидаемые тесты выполнились
    for expected in expected_tests:
        assert expected in _execution_log, f"Тест {expected} не выполнен"


@test("Последний тест для проверки")
def test_z_last():
    """
    Самый последний тест по алфавиту.
    """
    global _execution_log
    _execution_log.append("Z")
    _execution_times["Z"] = time.time()
    print("🔚 Тест Z выполнен последним")
    
    # Проверяем, что все предыдущие тесты были до Z
    for test_name in ["A", "B", "C", "DELAY", "FAST"]:
        assert _execution_log.index(test_name) < _execution_log.index("Z")
    
    # Финальная проверка порядка
    expected_order = ["A", "B", "C", "DELAY", "FAST", "Z"]
    assert _execution_log == expected_order, \
        f"Ожидался порядок {expected_order}, получен {_execution_log}"
    
    print(f"\n✅ Все тесты выполнены в правильном порядке!")