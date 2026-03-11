"""
Тест 1: Обработка KeyboardInterrupt.

Проверяет, что тестер корректно обрабатывает нажатие Ctrl+C
во время выполнения тестов.
"""

from utils.Tester.common.test_common import test
import time
import signal
import sys


# Глобальный флаг для отслеживания
_executed_tests = []
_interrupt_handled = False


def custom_handler(signum, frame):
    """
    Пользовательский обработчик для теста.
    """
    global _interrupt_handled
    print(f"\n⚠️ Тестовый обработчик перехватил сигнал {signum}")
    _interrupt_handled = True
    # Восстанавливаем стандартное поведение для выхода
    signal.signal(signal.SIGINT, signal.default_int_handler)


@test("Тест A - первый (быстрый)")
def test_a_fast():
    """
    Первый быстрый тест.
    """
    global _executed_tests
    _executed_tests.append("A")
    print("✅ Тест A выполнен")
    assert True


@test("Тест B - с имитацией KeyboardInterrupt")
def test_b_with_interrupt():
    """
    Тест, который имитирует получение KeyboardInterrupt.
    """
    global _executed_tests, _interrupt_handled
    _executed_tests.append("B")
    
    print("⏳ Тест B: имитация длительной операции...")
    print("   (будет сгенерировано KeyboardInterrupt)")
    
    try:
        # Имитация долгой работы
        for i in range(5):
            time.sleep(0.2)
            print(f"   Итерация {i+1}/5")
            
            # На третьей итерации генерируем KeyboardInterrupt
            if i == 2:
                print("   📢 Генерируем KeyboardInterrupt")
                raise KeyboardInterrupt("Тестовое прерывание")
        
        print("✅ Тест B завершен нормально")
    except KeyboardInterrupt as e:
        print(f"   ⚠️ Перехвачен KeyboardInterrupt: {e}")
        _interrupt_handled = True
        # В реальном тесте здесь должна быть корректная обработка
        # Но мы хотим, чтобы тест упал при прерывании
        raise
    
    assert True


@test("Тест C - после прерывания (не должен выполниться)")
def test_c_after_interrupt():
    """
    Тест, который не должен выполниться при прерывании.
    """
    global _executed_tests
    _executed_tests.append("C")
    print("❌ Тест C выполнился, хотя не должен был!")
    assert False, "Этот тест не должен был запуститься"


@test("Тест с собственным обработчиком сигнала")
def test_with_signal_handler():
    """
    Тест, который устанавливает свой обработчик сигнала.
    Проверяет, что тестер не ломает пользовательскую обработку.
    """
    global _executed_tests
    _executed_tests.append("SIGNAL_HANDLER")
    
    # Сохраняем оригинальный обработчик
    original_handler = signal.getsignal(signal.SIGINT)
    
    # Устанавливаем свой обработчик
    signal.signal(signal.SIGINT, custom_handler)
    
    print("✅ Установлен пользовательский обработчик сигнала")
    print("   (нажмите Ctrl+C для теста)")
    
    # Имитация работы
    try:
        for i in range(3):
            time.sleep(0.3)
            print(f"   Работаем... {i+1}")
    finally:
        # Восстанавливаем оригинальный обработчик
        signal.signal(signal.SIGINT, original_handler)
        print("✅ Оригинальный обработчик восстановлен")
    
    assert True


@test("Проверка состояния после возможного прерывания")
def test_check_state():
    """
    Проверяет состояние после возможного прерывания.
    """
    global _executed_tests, _interrupt_handled
    
    print(f"\n📋 Выполненные тесты: {_executed_tests}")
    print(f"🚩 Прерывание обработано: {_interrupt_handled}")
    
    # Проверяем, что тест B либо выполнился, либо был прерван
    if "B" in _executed_tests:
        print("✅ Тест B был запущен")
    else:
        print("⚠️ Тест B не запускался")
    
    # Тест C не должен быть в списке при прерывании
    if _interrupt_handled:
        assert "C" not in _executed_tests, "Тест C выполнился после прерывания"
    
    assert True


@test("Тест с множественными прерываниями")
def test_multiple_interrupts():
    """
    Тест с несколькими последовательными прерываниями.
    """
    print("⏳ Тест с множественными прерываниями")
    
    interrupt_count = 0
    
    try:
        for i in range(5):
            try:
                print(f"   Уровень {i+1}")
                if i == 2:
                    raise KeyboardInterrupt(f"Прерывание уровня {i+1}")
                time.sleep(0.1)
            except KeyboardInterrupt as e:
                interrupt_count += 1
                print(f"   ⚠️ Перехвачено прерывание: {e}")
                if i < 3:
                    # Пробрасываем дальше
                    raise
        
        print("✅ Все прерывания обработаны")
    except KeyboardInterrupt as e:
        print(f"   ⚠️ Финальное прерывание: {e}")
        raise
    
    assert interrupt_count >= 0