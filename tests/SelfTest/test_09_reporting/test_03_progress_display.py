"""
Тест 3: Отображение прогресса.

Проверяет корректность отображения прогресса выполнения тестов
в реальном времени.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestResult, TestOutput, TestSession
from utils.Tester.core.models import TestFunction
from utils.Tester.ui.reporter import TestReporter, ReportConfig, print_progress
from utils.Tester.core.executor import ProgressInfo
import io
import sys


def create_test_func(name: str) -> TestFunction:
    """Создает тестовую функцию."""
    def dummy():
        pass
    return TestFunction(
        name=name,
        description="",
        func=dummy,
        module_path="test.progress",
        file_path=None,
        line_number=42
    )


def create_result(name: str, success: bool, duration: float = 0.1) -> TestResult:
    """Создает результат теста."""
    test_func = create_test_func(name)
    return TestResult(
        test=test_func,
        success=success,
        duration=duration,
        output=TestOutput(),
        error=None if success else f"Error in {name}"
    )


@test("Форматирование строки прогресса")
def test_progress_line_format():
    """
    Проверяет формат строки прогресса для одного теста.
    """
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    # Успешный тест
    success_result = create_result("test_success", True, 0.123)
    progress_line = reporter.format_progress(success_result, 5, 10)
    
    print(f"\n📋 Прогресс (успех): {progress_line}")
    
    assert "5/10" in progress_line
    assert "test_success" in progress_line
    assert "✓" in progress_line or "[PASS]" in progress_line
    assert "123ms" in progress_line or "0.12s" in progress_line
    
    # Падающий тест
    fail_result = create_result("test_fail", False, 0.045)
    progress_line = reporter.format_progress(fail_result, 6, 10)
    
    print(f"📋 Прогресс (падение): {progress_line}")
    
    assert "6/10" in progress_line
    assert "test_fail" in progress_line
    assert "✗" in progress_line or "[FAIL]" in progress_line
    
    assert True


@test("Отображение прогресса с эмодзи и цветами")
def test_progress_with_emoji():
    """
    Проверяет отображение прогресса с эмодзи и цветами.
    """
    # Перехватываем stdout для проверки
    captured_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured_output
    
    try:
        reporter = TestReporter(ReportConfig(color=True, use_emoji=True))
        
        result = create_result("test_color", True, 0.1)
        print_progress(3, 10, result, reporter)
        
        output = captured_output.getvalue()
        
        print("\n📋 Прогресс с цветами (в консоли):")
        print(output)
        
        # Проверяем наличие эмодзи
        assert "✅" in output or "✓" in output
        
    finally:
        sys.stdout = original_stdout
    
    assert True


@test("Последовательное отображение прогресса")
def test_sequential_progress():
    """
    Проверяет последовательное отображение прогресса для нескольких тестов.
    """
    # Перехватываем stdout
    captured = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured
    
    try:
        reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
        
        # Имитируем выполнение 5 тестов
        results = [
            create_result("test_1", True, 0.1),
            create_result("test_2", True, 0.15),
            create_result("test_3", False, 0.2),
            create_result("test_4", True, 0.12),
            create_result("test_5", True, 0.18),
        ]
        
        for i, result in enumerate(results, 1):
            print_progress(i, len(results), result, reporter)
            # Добавляем перевод строки для разделения в выводе
            print()  # В реальности это делает раннер
        
        output = captured.getvalue()
        
        print("\n📋 Последовательный прогресс:")
        print("-" * 40)
        print(output)
        print("-" * 40)
        
        # Проверяем, что все тесты упомянуты
        for i in range(1, 6):
            assert f"{i}/5" in output
            assert f"test_{i}" in output
        
        # Проверяем, что падающий тест отмечен
        assert "✗" in output or "[FAIL]" in output
        assert "Error in test_3" in output
        
    finally:
        sys.stdout = original_stdout
    
    assert True


@test("Прогресс с разными длительностями")
def test_progress_durations():
    """
    Проверяет отображение разных длительностей в прогрессе.
    """
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    durations = [0.001, 0.01, 0.1, 0.5, 1.0, 1.5, 2.0]
    
    print("\n📋 Прогресс с разными длительностями:")
    
    for i, d in enumerate(durations):
        result = create_result(f"test_dur_{i}", True, d)
        line = reporter.format_progress(result, i+1, len(durations))
        print(f"   {line}")
        
        # Проверяем форматирование времени
        if d < 0.001:
            assert "µs" in line
        elif d < 1:
            assert "ms" in line
        else:
            assert "s" in line
    
    assert True


@test("Прогресс в callback'е executor'а")
def test_progress_callback():
    """
    Проверяет работу callback'а прогресса в executor'е.
    """
    from utils.Tester.core.executor import ProgressInfo
    from utils.Tester.core.runner import TestRunner
    from utils.Tester.utils.isolation import ShutdownHandler
    
    # Создаем компоненты
    runner = TestRunner()
    shutdown = ShutdownHandler()
    
    # Создаем executor с callback'ом
    from utils.Tester.core.executor import TestExecutor
    
    progress_updates = []
    
    def progress_callback(info: ProgressInfo):
        progress_updates.append({
            'current': info.current,
            'total': info.total,
            'success': info.result.success,
            'name': info.result.test.name
        })
        print(f"   Callback: {info.current}/{info.total} - {info.result.test.name}")
    
    executor = TestExecutor(runner, shutdown)
    executor.set_progress_callback(progress_callback)
    
    # Создаем тестовые функции
    test_funcs = []
    for i in range(3):
        def make_func(i):
            def _func():
                pass
            return _func
        
        func = create_test_func(f"callback_test_{i}").func
        test_funcs.append(create_test_func(f"callback_test_{i}"))
    
    # Запускаем тесты
    session = executor.run_selected(test_funcs, "Callback Test")
    
    print(f"\n📋 Получено обновлений прогресса: {len(progress_updates)}")
    
    # Должно быть 3 обновления (по одному на тест)
    assert len(progress_updates) == 3
    
    # Проверяем содержимое
    for i, update in enumerate(progress_updates):
        assert update['current'] == i + 1
        assert update['total'] == 3
        assert f"callback_test_{i}" in update['name']
    
    assert True


@test("Прогресс при большом количестве тестов")
def test_many_tests_progress():
    """
    Проверяет отображение прогресса при большом количестве тестов.
    """
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    # Имитируем 100 тестов
    total = 100
    
    print("\n📋 Прогресс при 100 тестах (первые 5 и последние 5):")
    
    for i in [1, 2, 3, 4, 5, 96, 97, 98, 99, 100]:
        result = create_result(f"test_{i}", i % 10 != 0, 0.1)  # Каждый 10-й падает
        line = reporter.format_progress(result, i, total)
        
        if i <= 5 or i >= 96:
            print(f"   {line}")
        
        # Проверяем формат
        assert f"{i}/{total}" in line
    
    assert True


@test("Прогресс с подробной информацией об ошибке")
def test_progress_with_error_detail():
    """
    Проверяет, что при падении теста в прогрессе показывается детальная ошибка.
    """
    # Перехватываем stdout
    captured = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured
    
    try:
        reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
        
        # Успешный тест
        success = create_result("test_ok", True, 0.1)
        print_progress(1, 3, success, reporter)
        print()
        
        # Падающий тест
        fail = create_result("test_bad", False, 0.2)
        fail.error = "ValueError: something went wrong"
        print_progress(2, 3, fail, reporter)
        print()
        
        # Еще один успешный
        success2 = create_result("test_ok2", True, 0.15)
        print_progress(3, 3, success2, reporter)
        
        output = captured.getvalue()
        
        print("\n📋 Прогресс с деталями ошибки:")
        print("-" * 40)
        print(output)
        print("-" * 40)
        
        # Проверяем, что детали ошибки показаны
        assert "ValueError: something went wrong" in output
        
    finally:
        sys.stdout = original_stdout
    
    assert True