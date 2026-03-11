"""
Тест 2: Перехват stderr.

Проверяет, что тестер корректно перехватывает и сохраняет
вывод в stderr во время выполнения теста.
"""

from utils.Tester.common.test_common import test
import sys


@test("Простой вывод в stderr")
def test_simple_stderr():
    """
    Тест с простым выводом в stderr.
    """
    print("Это сообщение в stdout", file=sys.stderr)
    print("Еще одно сообщение в stderr", file=sys.stderr)
    print("И третье", file=sys.stderr)
    
    assert True


@test("Смешанный вывод stdout и stderr")
def test_mixed_output():
    """
    Тест со смешанным выводом в оба потока.
    """
    print("Сообщение в stdout 1")
    print("Сообщение в stderr 1", file=sys.stderr)
    print("Сообщение в stdout 2")
    print("Сообщение в stderr 2", file=sys.stderr)
    print("Сообщение в stdout 3")
    
    assert True


@test("Вывод предупреждений в stderr")
def test_warning_output():
    """
    Тест с выводом предупреждений.
    """
    import warnings
    
    print("Начинаем обработку...")
    
    # Предупреждения обычно идут в stderr
    warnings.warn("Это предупреждение", UserWarning)
    
    print("Продолжаем...")
    
    # Кастомное предупреждение
    class TestWarning(Warning):
        pass
    
    warnings.warn("Тестовое предупреждение", TestWarning)
    
    print("Завершено")
    
    assert True


@test("Вывод ошибок в stderr")
def test_error_output():
    """
    Тест с выводом сообщений об ошибках.
    """
    import logging
    
    # Логирование ошибок часто идет в stderr
    logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
    logger = logging.getLogger(__name__)
    
    logger.error("Это сообщение об ошибке")
    logger.error("Еще одна ошибка", exc_info=True)
    
    # Но тест при этом проходит
    assert True


@test("Вывод traceback в stderr")
def test_traceback_stderr():
    """
    Тест с выводом traceback в stderr (без падения).
    """
    import traceback
    
    try:
        1 / 0
    except ZeroDivisionError:
        # Выводим traceback в stderr
        traceback.print_exc(file=sys.stderr)
    
    # Другой способ
    try:
        data = {"key": "value"}
        data["missing"]
    except KeyError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        traceback.print_tb(e.__traceback__, file=sys.stderr)
    
    assert True


@test("Вывод с подавлением исключений")
def test_suppress_exceptions():
    """
    Тест с подавлением исключений и выводом в stderr.
    """
    import contextlib
    
    with contextlib.suppress(ZeroDivisionError):
        print("Пытаемся поделить на ноль...", file=sys.stderr)
        1 / 0
        print("Это не выполнится")
    
    print("Продолжаем после подавления", file=sys.stderr)
    
    assert True


@test("Много вывода в stderr")
def test_large_stderr():
    """
    Тест с большим объемом вывода в stderr.
    """
    for i in range(50):
        print(f"Сообщение {i+1:2d}: " + "!" * (i % 40), file=sys.stderr)
    
    assert True


@test("Вывод с разными кодировками")
def test_unicode_stderr():
    """
    Тест с выводом Unicode символов в stderr.
    """
    # Русские буквы
    print("Привет, мир! Это тест.", file=sys.stderr)
    
    # Эмодзи
    print("Тест с эмодзи: 🧪 ✅ ❌ ⚠️ 🔧 📊", file=sys.stderr)
    
    # Специальные символы
    print("Спецсимволы: ♠ ♣ ♥ ♦ © ® ™", file=sys.stderr)
    
    # Китайские иероглифы
    print("Китайский: 你好，世界", file=sys.stderr)
    
    assert True