"""
Тест 2: Сбор результатов тестов.

Проверяет, что результаты тестов правильно собираются
и хранятся в сессии.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestSession, TestResult, TestOutput
from utils.Tester.core.models import TestFunction
import time


# Вспомогательная функция для создания тестовой функции
def create_test_func(name: str, desc: str = "") -> TestFunction:
    """Создает тестовую функцию для тестирования."""
    def dummy():
        pass
    
    return TestFunction(
        name=name,
        description=desc,
        func=dummy,
        module_path="test.results",
        file_path=None,
        line_number=42
    )


@test("Добавление одного результата")
def test_single_result():
    """
    Проверяет добавление одного результата в сессию.
    """
    session = TestSession(name="Single Result Test")
    
    # Создаем результат
    test_func = create_test_func("test_single", "Single test")
    result = TestResult(
        test=test_func,
        success=True,
        duration=0.1,
        output=TestOutput(stdout="OK", stderr=""),
        error=None
    )
    
    # Добавляем результат
    session.add_result(result)
    
    # Проверяем
    assert session.total == 1
    assert session.passed == 1
    assert session.failed == 0
    assert session.results[0] == result
    
    session.finish()
    print(f"✅ Один результат добавлен: {result.brief}")
    assert True


@test("Добавление нескольких результатов")
def test_multiple_results():
    """
    Проверяет добавление нескольких результатов в сессию.
    """
    session = TestSession(name="Multiple Results Test")
    results_count = 5
    
    for i in range(results_count):
        test_func = create_test_func(f"test_{i}", f"Test #{i}")
        
        # Чередуем успешные и падающие
        success = (i % 2 == 0)
        error = None if success else f"Error in test {i}"
        
        result = TestResult(
            test=test_func,
            success=success,
            duration=0.1 * (i + 1),
            output=TestOutput(stdout=f"Output {i}", stderr=""),
            error=error
        )
        
        session.add_result(result)
        print(f"   Добавлен: {result.brief}")
    
    # Проверяем общее количество
    assert session.total == results_count
    
    # Проверяем количество успешных (0,2,4 - 3 штуки)
    assert session.passed == 3
    assert session.failed == 2
    
    session.finish()
    print(f"\n✅ Итого в сессии:")
    print(f"   Всего: {session.total}")
    print(f"   Пройдено: {session.passed}")
    print(f"   Провалено: {session.failed}")
    
    assert True


@test("Добавление результатов с разными типами ошибок")
def test_error_types():
    """
    Проверяет добавление результатов с разными типами ошибок.
    """
    session = TestSession(name="Error Types Test")
    
    error_types = [
        ("AssertionError", "assert x == y failed"),
        ("ValueError", "invalid value"),
        ("TypeError", "unsupported type"),
        ("KeyError", "missing key"),
        ("IndexError", "list index out of range"),
        ("TimeoutError", "test timed out"),
        ("ZeroDivisionError", "division by zero"),
        ("RuntimeError", "runtime error"),
    ]
    
    for i, (err_type, err_msg) in enumerate(error_types):
        test_func = create_test_func(f"test_error_{i}", f"Test with {err_type}")
        
        result = TestResult(
            test=test_func,
            success=False,
            duration=0.05,
            output=TestOutput(stdout="", stderr="error output"),
            error=f"{err_type}: {err_msg}",
            traceback=f"Traceback: {err_type} at line 42"
        )
        
        session.add_result(result)
        
        # Проверяем свойства результата
        assert not result.success
        assert result.error_type == err_type
        assert result.has_error
        print(f"   Добавлен: {result.status_emoji} {err_type}")
    
    assert session.total == len(error_types)
    assert session.passed == 0
    assert session.failed == len(error_types)
    
    # Проверяем группировку ошибок
    error_groups = session.group_errors()
    assert len(error_groups) == len(error_types)
    
    print(f"\n✅ Группы ошибок:")
    for group in error_groups:
        print(f"   • {group.error_type}: {group.count} тестов")
    
    session.finish()
    assert True


@test("Проверка свойств результатов")
def test_result_properties():
    """
    Проверяет корректность свойств объектов TestResult.
    """
    test_func = create_test_func("test_properties", "Testing properties")
    
    # Успешный результат
    success_result = TestResult(
        test=test_func,
        success=True,
        duration=0.42,
        output=TestOutput(stdout="success", stderr=""),
        error=None
    )
    
    assert success_result.status_emoji == "✅"
    assert success_result.status_text == "PASSED"
    assert "✅" in success_result.brief
    assert "0.42" in success_result.brief or "420ms" in success_result.brief
    
    # Падающий результат
    fail_result = TestResult(
        test=test_func,
        success=False,
        duration=0.18,
        output=TestOutput(stdout="", stderr="error"),
        error="ValueError: something went wrong"
    )
    
    assert fail_result.status_emoji == "❌"
    assert fail_result.status_text == "FAILED"
    assert fail_result.error_type == "ValueError"
    
    # Результат с выводом
    output_result = TestResult(
        test=test_func,
        success=True,
        duration=0.05,
        output=TestOutput(stdout="line1\nline2\nline3", stderr="warning"),
        error=None
    )
    
    assert output_result.output.has_output
    assert len(output_result.output.lines) == 4  # 3 stdout + 1 stderr
    
    print(f"✅ Успешный: {success_result.brief}")
    print(f"✅ Падающий: {fail_result.brief}")
    print(f"✅ С выводом: {output_result.brief}")
    
    assert True