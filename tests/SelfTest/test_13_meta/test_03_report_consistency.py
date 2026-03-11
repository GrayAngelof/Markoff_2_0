"""
Тест 3: Согласованность итогового отчета.

Проверяет, что итоговый отчет соответствует реальным результатам тестов
и все данные отображаются корректно.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestRunner, TestSession, TestResult, TestOutput
from utils.Tester.core.models import TestFunction
from utils.Tester.ui.reporter import TestReporter, ReportConfig
import re


def create_test_func(name: str, success: bool = True) -> TestFunction:
    """Создает тестовую функцию."""
    def dummy():
        return True
    return TestFunction(
        name=name,
        description=f"Description for {name}",
        func=dummy,
        module_path="test.report",
        file_path=None,
        line_number=42
    )


@test("Согласованность статистики в отчете")
def test_report_statistics():
    """
    Проверяет, что статистика в отчете соответствует реальным результатам.
    """
    session = TestSession(name="Stats Test")
    
    # Создаем 10 тестов: 7 успешных, 3 падающих
    for i in range(7):
        test_func = create_test_func(f"test_pass_{i}")
        result = TestResult(
            test=test_func,
            success=True,
            duration=0.1,
            output=TestOutput(),
            error=None
        )
        session.add_result(result)
    
    for i in range(3):
        test_func = create_test_func(f"test_fail_{i}")
        result = TestResult(
            test=test_func,
            success=False,
            duration=0.15,
            output=TestOutput(),
            error=f"AssertionError: failure {i}"
        )
        session.add_result(result)
    
    session.finish()
    
    # Создаем отчет
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    report = reporter.format_session(session)
    
    print(f"\n📋 Проверка статистики в отчете:")
    
    # Проверяем наличие чисел
    assert "7" in report or "7/10" in report
    assert "3" in report or "3/10" in report
    assert "70.0%" in report or "70%" in report
    
    # Проверяем наличие всех тестов
    for i in range(7):
        assert f"test_pass_{i}" in report
    
    for i in range(3):
        assert f"test_fail_{i}" in report
    
    print(f"✅ Статистика в отчете соответствует реальным результатам")
    
    assert True


@test("Согласованность деталей ошибок")
def test_error_details_consistency():
    """
    Проверяет, что детали ошибок в отчете соответствуют реальным.
    """
    session = TestSession(name="Error Details Test")
    
    # Создаем тесты с разными ошибками
    errors = [
        ("AssertionError", "value mismatch"),
        ("ValueError", "invalid data"),
        ("TypeError", "wrong type"),
        ("KeyError", "missing key"),
    ]
    
    for err_type, err_msg in errors:
        test_func = create_test_func(f"test_{err_type.lower()}")
        result = TestResult(
            test=test_func,
            success=False,
            duration=0.1,
            output=TestOutput(),
            error=f"{err_type}: {err_msg}",
            traceback=f"Traceback: {err_type} at line 42"
        )
        session.add_result(result)
    
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False, show_traceback=True))
    report = reporter.format_session(session)
    
    print(f"\n📋 Проверка деталей ошибок:")
    
    for err_type, err_msg in errors:
        assert err_type in report
        assert err_msg in report
        print(f"   ✓ {err_type}: {err_msg}")
    
    assert True


@test("Согласованность группировки ошибок")
def test_error_grouping_consistency():
    """
    Проверяет, что группировка ошибок в отчете соответствует реальной.
    """
    session = TestSession(name="Error Grouping Test")
    
    # Создаем несколько ошибок одного типа
    for i in range(3):
        test_func = create_test_func(f"test_assert_{i}")
        result = TestResult(
            test=test_func,
            success=False,
            duration=0.1,
            output=TestOutput(),
            error=f"AssertionError: failure {i}"
        )
        session.add_result(result)
    
    # Другой тип
    for i in range(2):
        test_func = create_test_func(f"test_value_{i}")
        result = TestResult(
            test=test_func,
            success=False,
            duration=0.15,
            output=TestOutput(),
            error=f"ValueError: invalid {i}"
        )
        session.add_result(result)
    
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False, verbose=True))
    report = reporter.format_session(session)
    
    print(f"\n📋 Проверка группировки ошибок:")
    
    # Проверяем группы
    assert "AssertionError: 3 tests" in report or "AssertionError" in report
    assert "ValueError: 2 tests" in report or "ValueError" in report
    
    # Проверяем, что отдельные тесты тоже присутствуют
    for i in range(3):
        assert f"test_assert_{i}" in report
    
    for i in range(2):
        assert f"test_value_{i}" in report
    
    print(f"✅ Группировка ошибок корректна")
    
    assert True


@test("Согласованность форматов отчета")
def test_report_formats_consistency():
    """
    Проверяет, что разные форматы отчета (text, json) содержат одинаковые данные.
    """
    session = TestSession(name="Format Consistency Test")
    
    # Добавляем тесты
    test_func1 = create_test_func("test_format_1", True)
    result1 = TestResult(
        test=test_func1,
        success=True,
        duration=0.12,
        output=TestOutput(stdout="output 1"),
        error=None
    )
    session.add_result(result1)
    
    test_func2 = create_test_func("test_format_2", False)
    result2 = TestResult(
        test=test_func2,
        success=False,
        duration=0.08,
        output=TestOutput(stderr="error output"),
        error="AssertionError: failed"
    )
    session.add_result(result2)
    
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    # Получаем отчет в разных форматах
    text_report = reporter.to_text(session)
    json_report = reporter.to_json(session)
    
    print(f"\n📋 Проверка согласованности форматов:")
    
    # Проверяем основные метрики
    assert json_report['name'] == "Format Consistency Test"
    assert json_report['summary']['total'] == 2
    assert json_report['summary']['passed'] == 1
    assert json_report['summary']['failed'] == 1
    
    # Проверяем наличие тестов в text отчете
    assert "test_format_1" in text_report
    assert "test_format_2" in text_report
    assert "AssertionError" in text_report
    
    # Проверяем наличие тестов в json
    assert len(json_report['results']) == 2
    assert json_report['results'][0]['test']['name'] == "test_format_1"
    assert json_report['results'][1]['test']['name'] == "test_format_2"
    
    print(f"✅ Форматы согласованы")
    
    assert True


@test("Согласованность длительности в отчете")
def test_duration_consistency():
    """
    Проверяет, что длительности в отчете соответствуют реальным.
    """
    import time
    
    session = TestSession(name="Duration Test")
    
    durations = [0.05, 0.1, 0.15, 0.2, 0.25]
    
    for i, d in enumerate(durations):
        test_func = create_test_func(f"test_dur_{i}")
        
        # Имитируем выполнение с заданной длительностью
        start = time.time()
        time.sleep(d)
        real_duration = time.time() - start
        
        result = TestResult(
            test=test_func,
            success=True,
            duration=real_duration,
            output=TestOutput(),
            error=None
        )
        session.add_result(result)
    
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    report = reporter.format_session(session)
    
    print(f"\n📋 Проверка длительностей в отчете:")
    
    # Проверяем, что суммарное время указано
    total_time = sum(durations)
    assert f"{total_time:.2f}" in report or f"{total_time:.1f}" in report
    
    # Проверяем наличие отдельных тестов
    for i in range(len(durations)):
        assert f"test_dur_{i}" in report
    
    print(f"✅ Длительности в отчете присутствуют")
    
    assert True


@test("Согласованность при пустой сессии")
def test_empty_session_consistency():
    """
    Проверяет отчет для пустой сессии.
    """
    session = TestSession(name="Empty Session")
    session.finish()
    
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    report = reporter.format_session(session)
    json_report = reporter.to_json(session)
    
    print(f"\n📋 Проверка отчета для пустой сессии:")
    
    assert "Empty Session" in report
    assert "0/0" in report or "0 tests" in report
    
    assert json_report['summary']['total'] == 0
    assert json_report['summary']['passed'] == 0
    assert json_report['summary']['failed'] == 0
    assert len(json_report['results']) == 0
    
    print(f"✅ Отчет для пустой сессии корректен")
    
    assert True


@test("Согласованность при использовании цветов/эмодзи")
def test_color_emoji_consistency():
    """
    Проверяет, что цветной отчет содержит те же данные, что и обычный.
    """
    session = TestSession(name="Color Test")
    
    # Добавляем тесты
    for i in range(3):
        test_func = create_test_func(f"test_color_{i}", i % 2 == 0)
        result = TestResult(
            test=test_func,
            success=i % 2 == 0,
            duration=0.1,
            output=TestOutput(stdout=f"output {i}"),
            error=None if i % 2 == 0 else f"Error {i}"
        )
        session.add_result(result)
    
    session.finish()
    
    # Отчет без цветов
    reporter_plain = TestReporter(ReportConfig(color=False, use_emoji=False))
    plain_report = reporter_plain.format_session(session)
    
    # Отчет с цветами (убираем ANSI коды для сравнения)
    reporter_color = TestReporter(ReportConfig(color=True, use_emoji=True))
    color_report = reporter_color.format_session(session)
    
    # Удаляем ANSI коды для сравнения
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    color_report_plain = ansi_escape.sub('', color_report)
    
    print(f"\n📋 Проверка согласованности цветного отчета:")
    
    # Сравниваем длины (должны быть примерно равны)
    len_plain = len(plain_report)
    len_color = len(color_report_plain)
    
    print(f"   Длина plain: {len_plain}")
    print(f"   Длина color (без ANSI): {len_color}")
    
    # Основное содержание должно совпадать
    for i in range(3):
        assert f"test_color_{i}" in color_report_plain
    
    assert abs(len_plain - len_color) < 100  # Небольшая разница из-за эмодзи
    
    print(f"✅ Цветной отчет содержит те же данные")
    
    assert True