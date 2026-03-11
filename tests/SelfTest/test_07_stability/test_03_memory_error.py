"""
Тест 3: Обработка MemoryError.

Проверяет устойчивость тестера к ошибкам нехватки памяти.
"""

from utils.Tester.common.test_common import test
import time


_executed_tests = []
_memory_errors = 0


@test("Тест A - нормальный")
def test_a_normal():
    """
    Нормальный тест без ошибок памяти.
    """
    global _executed_tests
    _executed_tests.append("A")
    print("✅ Тест A выполнен")
    assert True


@test("Тест B - MemoryError")
def test_b_memory_error():
    """
    Тест, который генерирует MemoryError.
    """
    global _executed_tests, _memory_errors
    _executed_tests.append("B")
    
    print("⏳ Тест B: подготовка к MemoryError...")
    time.sleep(0.2)
    
    try:
        # Пытаемся выделить огромный список
        print("   Пытаемся выделить 1e10 элементов...")
        _memory_errors += 1
        huge_list = [0] * (10**10)  # Это вызовет MemoryError
        print(f"   Создан список длиной {len(huge_list)}")  # Не выполнится
    except MemoryError as e:
        print(f"   ⚠️ Перехвачен MemoryError: {e}")
        # Пробрасываем дальше, чтобы тест упал
        raise
    
    assert True  # Не выполнится


@test("Тест C - MemoryError во вложенной функции")
def test_c_nested_memory_error():
    """
    Тест с MemoryError внутри вложенных вызовов.
    """
    global _executed_tests, _memory_errors
    _executed_tests.append("C")
    
    def allocate_huge():
        print("     allocate_huge: начало")
        _memory_errors += 1
        huge = [0] * (10**10)
        print("     allocate_huge: конец")  # Не выполнится
        return huge
    
    def process_data():
        print("   process_data: начало")
        data = allocate_huge()
        print("   process_data: конец")  # Не выполнится
        return data
    
    print("⏳ Тест C: запуск цепочки выделения памяти")
    result = process_data()
    print(f"✅ Результат: {len(result)}")  # Не выполнится
    
    assert True  # Не выполнится


@test("Тест D - MemoryError в цикле")
def test_d_loop_memory_error():
    """
    Тест с MemoryError внутри цикла.
    """
    global _executed_tests, _memory_errors
    _executed_tests.append("D")
    
    print("⏳ Тест D: цикл с выделением памяти")
    
    for i in range(5):
        try:
            print(f"   Итерация {i+1}: выделяем память")
            if i == 2:
                _memory_errors += 1
                huge = [0] * (10**10)
                print(f"   Создан список длиной {len(huge)}")
            else:
                # Нормальное выделение
                normal = [0] * (10**6)
                print(f"   Нормальный список: {len(normal)}")
        except MemoryError as e:
            print(f"   ⚠️ Перехвачен MemoryError на итерации {i+1}: {e}")
            if i == 2:
                # Пробрасываем только на определенной итерации
                raise
    
    assert True  # Не выполнится


@test("Тест E - MemoryError с очисткой")
def test_e_memory_error_cleanup():
    """
    Тест с MemoryError и последующей очисткой.
    """
    global _executed_tests, _memory_errors
    _executed_tests.append("E")
    
    large_data = None
    
    try:
        print("⏳ Тест E: выделение памяти с очисткой")
        
        # Сначала нормальное выделение
        large_data = [0] * (10**7)
        print(f"   Создан список: {len(large_data)}")
        
        # Потом проблемное
        _memory_errors += 1
        huge = [0] * (10**10)
        
    except MemoryError as e:
        print(f"   ⚠️ Перехвачен MemoryError: {e}")
        # Очищаем память
        large_data = None
        print("   🧹 Память очищена")
        raise
    finally:
        print("   ✅ Блок finally выполнен")
    
    assert True  # Не выполнится


@test("Проверка состояния после MemoryError")
def test_check_state_after_memory_error():
    """
    Проверяет состояние после MemoryError.
    """
    global _executed_tests, _memory_errors
    
    print(f"\n📋 Выполненные тесты: {_executed_tests}")
    print(f"📊 Количество MemoryError: {_memory_errors}")
    
    # Проверяем, что все тесты были запущены
    expected_tests = ["A", "B", "C", "D", "E"]
    for test_name in expected_tests:
        if test_name in _executed_tests:
            print(f"   ✅ Тест {test_name} запущен")
        else:
            print(f"   ❌ Тест {test_name} не запущен")
    
    # Тесты после ошибок должны выполняться (если не было фатальной ошибки)
    assert "A" in _executed_tests
    assert "B" in _executed_tests or _memory_errors > 0
    
    print(f"\n📈 Всего ошибок памяти: {_memory_errors}")
    assert _memory_errors >= 3  # Должно быть минимум 3 ошибки
    
    assert True