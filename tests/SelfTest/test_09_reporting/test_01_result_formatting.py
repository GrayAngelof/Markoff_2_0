"""
Тест 1: Форматирование результата теста.

Проверяет, что отдельный результат теста правильно форматируется
для отображения в разных режимах.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestResult, TestOutput
from utils.Tester.core.models import TestFunction
from utils.Tester.ui.reporter import TestReporter, ReportConfig


def create_test_func(name: str, desc: str = "") -> TestFunction:
    """Создает тестовую функцию."""
    def dummy():
        pass
    return TestFunction(
        name=name,
        description=desc,
        func=dummy,
        module_path="test.reporting",
        file_path=None,
        line_number=42,
        markers={"smoke", "fast"}
    )


@test("Форматирование успешного результата")
def test_success_formatting():
    """
    Проверяет форматирование успешного результата теста.
    """
    # Создаем успешный результат
    test_func = create_test_func("test_success", "Это успешный тест")
    
    result = TestResult(
        test=test_func,
        success=True,
        duration=0.123,
        output=TestOutput(stdout="All good!\nSecond line", stderr=""),
        error=None
    )
    
    # Создаем репортер без цветов для теста
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    # Форматируем результат
    formatted = reporter.format_result(result)
    
    print("\n📋 Успешный результат (без цветов):")
    print("-" * 40)
    print(formatted)
    print("-" * 40)
    
    # Проверяем наличие ключевых элементов
    assert "test_success" in formatted
    assert "✓" in formatted or "[PASS]" in formatted
    assert "123ms" in formatted or "0.12s" in formatted
    assert "Это успешный тест" in formatted
    assert "All good!" in formatted
    
    # С цветами
    reporter_color = TestReporter(ReportConfig(color=True, use_emoji=True))
    formatted_color = reporter_color.format_result(result)
    
    print("\n🎨 С цветами и эмодзи:")
    print("-" * 40)
    # В консоли цвета будут видны, но в логе мы их не показываем
    assert "✅" in formatted_color or "✓" in formatted_color
    
    assert True


@test("Форматирование падающего результата")
def test_failure_formatting():
    """
    Проверяет форматирование падающего результата теста.
    """
    test_func = create_test_func("test_failure", "Это падающий тест")
    
    result = TestResult(
        test=test_func,
        success=False,
        duration=0.045,
        output=TestOutput(stdout="Before failure", stderr="Error happened"),
        error="AssertionError: Expected 42, got 41",
        traceback="  File \"test.py\", line 42, in test_failure\n    assert x == y"
    )
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    # Без traceback
    formatted = reporter.format_result(result)
    
    print("\n📋 Падающий результат (без traceback):")
    print("-" * 40)
    print(formatted)
    print("-" * 40)
    
    assert "test_failure" in formatted
    assert "✗" in formatted or "[FAIL]" in formatted
    assert "AssertionError: Expected 42, got 41" in formatted
    assert "Before failure" in formatted
    assert "Error happened" in formatted
    
    # С traceback
    reporter.config.show_traceback = True
    formatted_with_tb = reporter.format_result(result)
    
    print("\n📋 С traceback:")
    print("-" * 40)
    print(formatted_with_tb)
    print("-" * 40)
    
    assert "assert x == y" in formatted_with_tb
    
    assert True


@test("Форматирование с разными уровнями детализации")
def test_verbosity_levels():
    """
    Проверяет форматирование с разными уровнями детализации.
    """
    test_func = create_test_func("test_verbose", "Тест для проверки verbosity")
    
    # Результат с большим выводом
    long_output = "\n".join([f"Line {i}: x={i*10}" for i in range(50)])
    
    result = TestResult(
        test=test_func,
        success=True,
        duration=0.321,
        output=TestOutput(stdout=long_output, stderr="Warning: deprecated"),
        error=None
    )
    
    # Минимальный уровень (только заголовок)
    reporter_min = TestReporter(ReportConfig(
        color=False, 
        use_emoji=False,
        show_output=False,
        max_output_lines=5
    ))
    
    formatted_min = reporter_min.format_result(result)
    
    print("\n📋 Минимальный вывод:")
    print("-" * 40)
    print(formatted_min)
    print("-" * 40)
    
    assert "test_verbose" in formatted_min
    assert "Line" not in formatted_min  # Вывода нет
    assert "Warning" not in formatted_min
    
    # Средний уровень (с выводом, но обрезанным)
    reporter_medium = TestReporter(ReportConfig(
        color=False,
        use_emoji=False,
        show_output=True,
        max_output_lines=10
    ))
    
    formatted_medium = reporter_medium.format_result(result)
    
    print("\n📋 Средний вывод (обрезанный):")
    print("-" * 40)
    print(formatted_medium[:500] + "...")
    print("-" * 40)
    
    assert "Line 0" in formatted_medium
    assert "Line 9" in formatted_medium
    assert "Line 20" not in formatted_medium  # Должно быть обрезано
    assert "Warning" in formatted_medium
    
    # Полный уровень
    reporter_full = TestReporter(ReportConfig(
        color=False,
        use_emoji=False,
        show_output=True,
        max_output_lines=100
    ))
    
    formatted_full = reporter_full.format_result(result)
    lines = formatted_full.split('\n')
    
    print(f"\n📋 Полный вывод ({len(lines)} строк)")
    
    assert len([l for l in lines if "Line" in l]) >= 40
    
    assert True


@test("Форматирование с разными типами ошибок")
def test_error_types_formatting():
    """
    Проверяет форматирование разных типов ошибок.
    """
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    error_types = [
        ("AssertionError", "assert x == y failed"),
        ("ValueError", "invalid literal for int()"),
        ("TypeError", "unsupported operand type(s)"),
        ("KeyError", "'missing_key'"),
        ("IndexError", "list index out of range"),
        ("TimeoutError", "test timed out after 5s"),
        ("ZeroDivisionError", "division by zero"),
        ("ImportError", "No module named 'xyz'"),
    ]
    
    for err_type, err_msg in error_types:
        test_func = create_test_func(f"test_{err_type.lower()}")
        
        result = TestResult(
            test=test_func,
            success=False,
            duration=0.05,
            output=TestOutput(),
            error=f"{err_type}: {err_msg}"
        )
        
        formatted = reporter.format_result(result)
        
        print(f"\n📋 {err_type}:")
        print(f"   {formatted.split(chr(10))[1]}")  # Вторая строка с ошибкой
        
        assert err_type in formatted
        assert err_msg in formatted
    
    assert True


@test("Форматирование без вывода")
def test_no_output_formatting():
    """
    Проверяет форматирование результата без вывода.
    """
    test_func = create_test_func("test_no_output")
    
    result = TestResult(
        test=test_func,
        success=True,
        duration=0.001,
        output=TestOutput(),
        error=None
    )
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    formatted = reporter.format_result(result)
    
    print("\n📋 Результат без вывода:")
    print("-" * 40)
    print(formatted)
    print("-" * 40)
    
    assert "test_no_output" in formatted
    assert "Output" not in formatted
    assert "STDERR" not in formatted
    
    assert True