"""
Тест 2: Обработка SystemExit.

Проверяет, что тестер корректно обрабатывает вызов sys.exit()
во время выполнения тестов.
"""

from utils.Tester.common.test_common import test
import sys
import time


_executed_tests = []
_exit_code = None


@test("Тест A - первый")
def test_a_first():
    """
    Первый тест в последовательности.
    """
    global _executed_tests
    _executed_tests.append("A")
    print("✅ Тест A выполнен")
    assert True


@test("Тест B - с sys.exit(0)")
def test_b_exit_success():
    """
    Тест, который вызывает sys.exit(0) (успешное завершение).
    """
    global _executed_tests, _exit_code
    _executed_tests.append("B")
    
    print("⏳ Тест B: подготовка к exit(0)...")
    time.sleep(0.2)
    
    print("📢 Вызов sys.exit(0)")
    _exit_code = 0
    sys.exit(0)
    
    # Этот код не выполнится
    print("❌ Этот код не должен выполниться")
    assert False


@test("Тест C - после exit (не должен выполниться)")
def test_c_after_exit():
    """
    Тест, который не должен выполниться после sys.exit().
    """
    global _executed_tests
    _executed_tests.append("C")
    print("❌ Тест C выполнился, хотя не должен был!")
    assert False


@test("Тест D - с sys.exit(1)")
def test_d_exit_error():
    """
    Тест, который вызывает sys.exit(1) (ошибка).
    """
    global _executed_tests, _exit_code
    _executed_tests.append("D")
    
    print("⏳ Тест D: подготовка к exit(1)...")
    time.sleep(0.2)
    
    print("📢 Вызов sys.exit(1)")
    _exit_code = 1
    sys.exit(1)
    
    print("❌ Этот код не должен выполниться")
    assert False


@test("Тест E - с sys.exit в блоке try")
def test_e_exit_in_try():
    """
    Тест, который вызывает sys.exit внутри try/finally.
    Проверяет, что finally выполняется.
    """
    global _executed_tests
    
    print("⏳ Тест E: exit внутри try/finally")
    
    try:
        print("   Внутри try")
        _executed_tests.append("E_TRY")
        sys.exit(42)
    finally:
        print("   ✅ Блок finally выполняется даже при exit")
        _executed_tests.append("E_FINALLY")
    
    print("❌ Этот код не должен выполниться")
    assert False


@test("Тест F - с sys.exit во вложенной функции")
def test_f_nested_exit():
    """
    Тест с вызовом sys.exit из вложенной функции.
    """
    
    def level1():
        print("   level1")
        level2()
        print("   ❌ level1 после level2")
    
    def level2():
        print("   level2")
        level3()
        print("   ❌ level2 после level3")
    
    def level3():
        print("   level3")
        print("   📢 Вызов sys.exit из level3")
        sys.exit(99)
        print("   ❌ level3 после exit")
    
    print("⏳ Тест F: exit из вложенной функции")
    level1()
    
    print("❌ Этот код не должен выполниться")
    assert False


@test("Проверка состояния после exit")
def test_check_state_after_exit():
    """
    Проверяет состояние после вызовов sys.exit.
    """
    global _executed_tests, _exit_code
    
    print(f"\n📋 Выполненные тесты: {_executed_tests}")
    print(f"📊 Последний код выхода: {_exit_code}")
    
    # Тесты после exit не должны выполняться
    assert "C" not in _executed_tests, "Тест C выполнился после exit"
    
    # Проверяем, что finally блоки выполняются
    if "E_TRY" in _executed_tests:
        assert "E_FINALLY" in _executed_tests, "Finally не выполнился"
        print("✅ Блок finally выполнен")
    
    assert True


@test("Тест с SystemExit в потоке")
def test_exit_in_thread():
    """
    Тест с вызовом sys.exit в отдельном потоке.
    """
    import threading
    
    def thread_func():
        print("   Поток: запущен")
        time.sleep(0.2)
        print("   Поток: вызываю sys.exit")
        sys.exit(111)
        print("   ❌ Поток: после exit")
    
    thread = threading.Thread(target=thread_func)
    thread.start()
    thread.join(timeout=1)
    
    print("✅ Главный поток продолжает работу")
    assert True