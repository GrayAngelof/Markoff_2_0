"""
Тест 1: Прерывание выполнения.

Проверяет корректную остановку выполнения тестов при получении сигнала остановки.
"""

from utils.Tester.common.test_common import test
import time
import signal
import os


# Глобальный счетчик для отслеживания выполнения
_executed_tests = []
_should_stop = False


def handle_interrupt(signum, frame):
    """
    Обработчик сигнала прерывания.
    """
    global _should_stop
    print(f"\n⚠️ Получен сигнал {signum}")
    _should_stop = True


@test("Тест A - первый в очереди")
def test_a_first():
    """
    Первый тест в последовательности.
    """
    global _executed_tests
    _executed_tests.append("A")
    print("✅ Тест A выполнен")
    
    # Регистрируем обработчик сигнала (только для демонстрации)
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, handle_interrupt)
    
    assert True


@test("Тест B - второй тест")
def test_b_second():
    """
    Второй тест в последовательности.
    """
    global _executed_tests
    _executed_tests.append("B")
    print("✅ Тест B выполнен")
    assert True


@test("Тест C - долгий тест")
def test_c_long():
    """
    Долгий тест, во время выполнения которого можно отправить сигнал.
    """
    global _executed_tests, _should_stop
    _executed_tests.append("C")
    
    print("⏳ Тест C: начинаем долгую операцию...")
    print("   (здесь можно отправить Ctrl+C для проверки прерывания)")
    
    # Долгая операция с проверкой флага остановки
    for i in range(10):
        if _should_stop:
            print("   ⚠️ Получен сигнал остановки, прерываем тест")
            break
        
        print(f"   Шаг {i+1}/10: работаем...")
        time.sleep(0.5)  # Полсекунды на шаг
        
        # Для автоматического тестирования можно эмулировать сигнал
        if i == 2 and os.environ.get('TEST_SIGNAL_AT_STEP') == '3':
            print("   📢 Эмулируем сигнал прерывания")
            _should_stop = True
    
    if _should_stop:
        print("   ⚠️ Тест C прерван досрочно")
        # Тест может либо упасть, либо завершиться с ошибкой
        # В данном случае мы хотим, чтобы он упал
        assert not _should_stop, "Тест был прерван сигналом"
    else:
        print("✅ Тест C выполнен полностью")
        assert True


@test("Тест D - после долгого теста")
def test_d_after_long():
    """
    Тест, который должен выполниться после долгого теста.
    Если был сигнал прерывания, этот тест не должен выполниться.
    """
    global _executed_tests
    _executed_tests.append("D")
    print("✅ Тест D выполнен")
    assert True


@test("Тест E - проверка состояния")
def test_e_check_state():
    """
    Проверяет состояние выполнения после возможного прерывания.
    """
    global _executed_tests, _should_stop
    
    print(f"\n📋 Выполненные тесты: {_executed_tests}")
    print(f"🚩 Флаг остановки: {_should_stop}")
    
    # Проверяем, что тесты выполнялись в правильном порядке
    expected_before_interrupt = ["A", "B"]
    
    for i, expected in enumerate(expected_before_interrupt):
        if i < len(_executed_tests):
            assert _executed_tests[i] == expected, \
                f"Порядок нарушен: ожидался {expected} на позиции {i}, получен {_executed_tests[i]}"
    
    # Тест C должен быть либо выполнен полностью, либо прерван
    if "C" in _executed_tests:
        c_index = _executed_tests.index("C")
        # Если тест D выполнился, он должен быть после C
        if "D" in _executed_tests:
            assert _executed_tests.index("D") > c_index
    
    print(f"\n📊 Итоговый набор тестов: {_executed_tests}")
    
    # Этот тест всегда проходит, он только проверяет состояние
    assert True


@test("Тест с собственной обработкой сигналов")
def test_custom_signal_handling():
    """
    Тест с собственной обработкой сигналов.
    Проверяет, что тестер не ломает пользовательскую обработку.
    """
    import signal
    
    original_handler = None
    
    def custom_handler(signum, frame):
        print(f"📢 Пользовательский обработчик сигнала {signum}")
        # Вызываем оригинальный обработчик тестера
        if original_handler and callable(original_handler):
            original_handler(signum, frame)
    
    if hasattr(signal, 'SIGINT'):
        # Сохраняем оригинальный обработчик
        original_handler = signal.getsignal(signal.SIGINT)
        # Устанавливаем свой
        signal.signal(signal.SIGINT, custom_handler)
        
        print("✅ Установлен пользовательский обработчик сигнала")
        
        # Восстанавливаем в конце теста (не обязательно, тестер сам восстановит)
        # signal.signal(signal.SIGINT, original_handler)
    
    assert True


@test("Тест с проверкой флага остановки")
def test_check_stop_flag():
    """
    Тест, который проверяет флаг остановки в процессе выполнения.
    """
    from utils.Tester.utils.isolation import ShutdownHandler
    
    # Создаем локальный обработчик (для демонстрации)
    handler = ShutdownHandler()
    handler.register()
    
    print("🚦 Проверка флага остановки:")
    
    for i in range(5):
        if handler.should_stop:
            print(f"  ⚠️ Обнаружен сигнал остановки на итерации {i}")
            break
        print(f"  Итерация {i}: флаг остановки = {handler.should_stop}")
        time.sleep(0.1)
    
    handler.restore()
    assert True