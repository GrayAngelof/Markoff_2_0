"""
Тест 2: Форматирование отчета сессии.

Проверяет, что итоговый отчет тестовой сессии правильно форматируется
со всей статистикой и деталями.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestSession, TestResult, TestOutput
from utils.Tester.core.models import TestFunction
from utils.Tester.ui.reporter import TestReporter, ReportConfig
import time


def create_test_func(name: str, module: str = "test.module") -> TestFunction:
    """Создает тестовую функцию."""
    def dummy():
        pass
    return TestFunction(
        name=name,
        description=f"Description for {name}",
        func=dummy,
        module_path=module,
        file_path=None,
        line_number=42
    )


def create_result(name: str, success: bool, duration: float = 0.1, 
                 output: str = "", error: str = None) -> TestResult:
    """Создает результат теста."""
    test_func = create_test_func(name)
    return TestResult(
        test=test_func,
        success=success,
        duration=duration,
        output=TestOutput(stdout=output, stderr=""),
        error=error
    )


@test("Форматирование отчета успешной сессии")
def test_success_session_report():
    """
    Проверяет форматирование отчета сессии, где все тесты успешны.
    """
    session = TestSession(name="All Passed")
    
    # Добавляем 5 успешных тестов
    for i in range(5):
        session.add_result(create_result(
            f"test_pass_{i}", 
            True, 
            0.1 + i*0.05,
            f"Output from test {i}"
        ))
    
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    report = reporter.format_session(session)
    
    print("\n📋 ОТЧЕТ УСПЕШНОЙ СЕССИИ:")
    print("=" * 60)
    print(report)
    print("=" * 60)
    
    # Проверяем наличие ключевых элементов
    assert "All Passed" in report
    assert "5 tests" in report or "5/5" in report
    assert "Passed: 5" in report
    assert "Failed: 0" in report
    assert "100.0%" in report or "100%" in report
    
    # Проверяем наличие всех тестов
    for i in range(5):
        assert f"test_pass_{i}" in report
    
    # Не должно быть секции с ошибками
    assert "FAILED TESTS" not in report.upper()
    
    assert True


@test("Форматирование отчета с падениями")
def test_failed_session_report():
    """
    Проверяет форматирование отчета сессии с падающими тестами.
    """
    session = TestSession(name="Mixed Results")
    
    # Добавляем смесь успешных и падающих тестов
    session.add_result(create_result("test_pass_1", True, 0.1, "OK"))
    session.add_result(create_result("test_fail_1", False, 0.2, "", 
                                     "AssertionError: 1 != 2"))
    session.add_result(create_result("test_pass_2", True, 0.15, "Good"))
    session.add_result(create_result("test_fail_2", False, 0.25, "", 
                                     "ValueError: bad value"))
    session.add_result(create_result("test_fail_3", False, 0.3, "", 
                                     "TypeError: unsupported type"))
    session.add_result(create_result("test_pass_3", True, 0.12, "Done"))
    
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False, max_failures=5))
    report = reporter.format_session(session)
    
    print("\n📋 ОТЧЕТ СО СМЕШАННЫМИ РЕЗУЛЬТАТАМИ:")
    print("=" * 60)
    print(report)
    print("=" * 60)
    
    # Проверяем статистику
    assert "Mixed Results" in report
    assert "Passed: 3" in report
    assert "Failed: 3" in report
    assert "50.0%" in report or "50%" in report
    
    # Должна быть секция с ошибками
    assert "FAILED TESTS" in report.upper()
    assert "AssertionError" in report
    assert "ValueError" in report
    assert "TypeError" in report
    
    assert True


@test("Форматирование отчета с группировкой ошибок")
def test_error_grouping_report():
    """
    Проверяет группировку ошибок в отчете.
    """
    session = TestSession(name="Error Groups")
    
    # Создаем несколько ошибок одного типа
    for i in range(3):
        session.add_result(create_result(
            f"test_assert_{i}", False, 0.1, "",
            f"AssertionError: value mismatch in test {i}"
        ))
    
    # Другой тип ошибки
    for i in range(2):
        session.add_result(create_result(
            f"test_value_{i}", False, 0.15, "",
            f"ValueError: invalid data in test {i}"
        ))
    
    # Еще один тип
    session.add_result(create_result(
        "test_type", False, 0.2, "",
        "TypeError: cannot concatenate str and int"
    ))
    
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False, verbose=True))
    report = reporter.format_session(session)
    
    print("\n📋 ОТЧЕТ С ГРУППИРОВКОЙ ОШИБОК:")
    print("=" * 60)
    print(report)
    print("=" * 60)
    
    # Проверяем наличие групп
    assert "Error Summary" in report
    assert "AssertionError: 3 tests" in report
    assert "ValueError: 2 tests" in report
    assert "TypeError: 1 tests" in report
    
    assert True


@test("Форматирование разных форматов отчета")
def test_report_formats():
    """
    Проверяет разные форматы отчета (text, json).
    """
    session = TestSession(name="Format Test")
    
    session.add_result(create_result("test_json_1", True, 0.1, "output 1"))
    session.add_result(create_result("test_json_2", False, 0.2, "output 2", 
                                     "AssertionError: failed"))
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    # Text формат
    text_report = reporter.to_text(session)
    
    print("\n📋 TEXT FORMAT:")
    print("-" * 40)
    print(text_report[:500] + "...")
    
    assert "Format Test" in text_report
    assert "test_json_1" in text_report
    assert "test_json_2" in text_report
    
    # JSON формат
    json_report = reporter.to_json(session)
    
    print("\n📋 JSON FORMAT:")
    print("-" * 40)
    import json
    print(json.dumps(json_report, indent=2)[:500] + "...")
    
    assert json_report['name'] == "Format Test"
    assert json_report['summary']['total'] == 2
    assert json_report['summary']['passed'] == 1
    assert json_report['summary']['failed'] == 1
    assert len(json_report['results']) == 2
    
    assert True


@test("Форматирование пустого отчета")
def test_empty_session_report():
    """
    Проверяет форматирование отчета пустой сессии.
    """
    session = TestSession(name="Empty Session")
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    report = reporter.format_session(session)
    
    print("\n📋 ПУСТОЙ ОТЧЕТ:")
    print("=" * 60)
    print(report)
    print("=" * 60)
    
    assert "Empty Session" in report
    assert "0/0" in report or "0 tests" in report
    assert "Passed: 0" in report
    assert "Failed: 0" in report
    
    assert True


@test("Форматирование с ограничением количества ошибок")
def test_failure_limit():
    """
    Проверяет ограничение количества показываемых ошибок.
    """
    session = TestSession(name="Many Failures")
    
    # Добавляем много падающих тестов
    for i in range(20):
        session.add_result(create_result(
            f"test_fail_{i}", False, 0.1, "",
            f"Error in test {i}"
        ))
    
    session.finish()
    
    # С лимитом 5 ошибок
    reporter = TestReporter(ReportConfig(
        color=False, 
        use_emoji=False,
        max_failures=5
    ))
    
    report = reporter.format_session(session)
    
    print("\n📋 ОТЧЕТ С ЛИМИТОМ ОШИБОК (5):")
    print("=" * 60)
    print(report)
    print("=" * 60)
    
    # Должны быть показаны только первые 5 ошибок
    for i in range(5):
        assert f"test_fail_{i}" in report
    
    for i in range(5, 20):
        assert f"test_fail_{i}" not in report
    
    assert "... and 15 more failures" in report
    
    assert True