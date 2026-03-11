"""
Тест 2: Частичное выполнение после прерывания.

Проверяет, что после сигнала остановки выполняется только часть тестов,
и что оставшиеся тесты не запускаются.
"""

from utils.Tester.common.test_common import test
import time
import os
import threading


# Глобальное состояние для отслеживания
_execution_log = []
_interrupt_at = 3  # Прерываем после 3-го теста
_current_index = 0
_interrupt_sent = False


def simulate_interrupt_after(seconds):
    """
    Имитирует отправку сигнала прерывания через указанное время.
    """
    def _delayed_interrupt():
        global _interrupt_sent
        time.sleep(seconds)
        print(f"\n⚠️ [ИМИТАЦИЯ] Отправка сигнала прерывания")
        _interrupt_sent = True
        
        # В реальном тесте здесь был бы os.kill или keyboard interrupt
        # Но для теста мы просто устанавливаем флаг
    
    thread = threading.Thread(target=_delayed_interrupt)
    thread.daemon = True
    thread.start()
    return thread


@test("Тест 1 - первый")
def test_partial_1():
    """
    Первый тест в последовательности.
    """
    global _execution_log, _current_index
    _current_index += 1
    _execution_log.append(1)
    print(f"✅ Тест 1 выполнен (индекс {_current_index})")
    assert True


@test("Тест 2 - второй")
def test_partial_2():
    """
    Второй тест в последовательности.
    """
    global _execution_log, _current_index
    _current_index += 1
    _execution_log.append(2)
    print(f"✅ Тест 2 выполнен (индекс {_current_index})")
    assert True


@test("Тест 3 - третий (точка прерывания)")
def test_partial_3_interrupt_point():
    """
    Третий тест - здесь происходит прерывание.
    """
    global _execution_log, _current_index, _interrupt_sent
    _current_index += 1
    _execution_log.append(3)
    
    print(f"✅ Тест 3 выполнен (индекс {_current_index})")
    print("⏳ Запускаем имитацию прерывания...")
    
    # Запускаем имитацию прерывания через 0.5 секунды
    # В реальном тесте здесь был бы настоящий сигнал
    simulate_interrupt_after(0.5)
    
    # Долгая операция, во время которой придет прерывание
    for i in range(10):
        if _interrupt_sent:
            print(f"  ⚠️ Обнаружено прерывание на итерации {i}")
            # Имитируем реакцию на сигнал
            break
        print(f"  Работаем... итерация {i}")
        time.sleep(0.2)
    
    # Если прерывание было, тест может завершиться с ошибкой
    if _interrupt_sent:
        print("  ⚠️ Тест 3 завершается из-за прерывания")
        # Мы хотим, чтобы тест упал при прерывании
        assert not _interrupt_sent, "Тест был прерван сигналом"
    
    assert True


@test("Тест 4 - четвертый (не должен выполниться)")
def test_partial_4_should_not_run():
    """
    Четвертый тест НЕ должен выполниться при прерывании.
    """
    global _execution_log
    _execution_log.append(4)
    print("❌ Тест 4 ВЫПОЛНИЛСЯ, хотя не должен был!")
    assert False, "Этот тест не должен был запуститься"


@test("Тест 5 - пятый (не должен выполниться)")
def test_partial_5_should_not_run():
    """
    Пятый тест НЕ должен выполниться при прерывании.
    """
    global _execution_log
    _execution_log.append(5)
    print("❌ Тест 5 ВЫПОЛНИЛСЯ, хотя не должен был!")
    assert False, "Этот тест не должен был запуститься"


@test("Тест 6 - шестой (не должен выполниться)")
def test_partial_6_should_not_run():
    """
    Шестой тест НЕ должен выполниться при прерывании.
    """
    global _execution_log
    _execution_log.append(6)
    print("❌ Тест 6 ВЫПОЛНИЛСЯ, хотя не должен был!")
    assert False, "Этот тест не должен был запуститься"


@test("Проверка частичного выполнения")
def test_check_partial_execution():
    """
    Проверяет, что после прерывания выполнились только первые тесты.
    """
    global _execution_log, _interrupt_sent
    
    print(f"\n📋 Лог выполнения: {_execution_log}")
    print(f"🚩 Флаг прерывания: {_interrupt_sent}")
    
    # Если прерывание было отправлено
    if _interrupt_sent:
        # Должны выполниться только тесты 1, 2 и, возможно, 3
        assert 1 in _execution_log, "Тест 1 не выполнен"
        assert 2 in _execution_log, "Тест 2 не выполнен"
        # Тест 3 мог выполниться частично
        assert 3 in _execution_log, "Тест 3 должен был начаться"
        
        # Тесты 4-6 не должны выполниться
        assert 4 not in _execution_log, "Тест 4 выполнился после прерывания"
        assert 5 not in _execution_log, "Тест 5 выполнился после прерывания"
        assert 6 not in _execution_log, "Тест 6 выполнился после прерывания"
        
        print("✅ Проверка частичного выполнения пройдена")
    else:
        print("⚠️ Прерывание не было отправлено, пропускаем проверку")
    
    assert True


@test("Тест с ранним прерыванием")
def test_early_interrupt():
    """
    Тест с ранним прерыванием на первой итерации.
    """
    print("⏳ Тест с ранним прерыванием")
    
    # Имитируем прерывание сразу
    time.sleep(0.1)
    
    # Проверяем, что раннер корректно обработает ситуацию
    # Если тест будет прерван, он не дойдет до этого assert
    assert True


@test("Тест с проверкой состояния после прерывания")
def test_state_after_interrupt():
    """
    Проверяет состояние системы после прерывания.
    """
    global _execution_log
    
    print(f"\n🔍 Финальный анализ:")
    print(f"  Всего выполнено тестов: {len(_execution_log)}")
    print(f"  Выполненные тесты: {sorted(_execution_log)}")
    
    # Проверяем, что не было пропусков в последовательности
    if _execution_log:
        max_executed = max(_execution_log)
        for i in range(1, max_executed + 1):
            if i in _execution_log:
                print(f"  ✅ Тест {i} выполнен")
            else:
                print(f"  ❌ Тест {i} пропущен")
    
    assert True