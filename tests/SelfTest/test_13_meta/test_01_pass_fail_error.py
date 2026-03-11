"""
Тест 1: Классификация PASS / FAIL / ERROR.

Проверяет корректную классификацию результатов тестов
и обработку различных типов завершения.
"""

from utils.Tester.common.test_common import test, TestHandler
from utils.Tester.core.runner import TestRunner, TestResult
from utils.Tester.core.models import TestFunction
import time


def create_test_func(name: str, body: str) -> TestFunction:
    """
    Создает тестовую функцию с заданным телом.
    """
    namespace = {}
    exec(f"def {name}():\n    {body}", namespace)
    func = namespace[name]
    
    return TestFunction(
        name=name,
        description=f"Test {name}",
        func=func,
        module_path="test.meta",
        file_path=None,
        line_number=42
    )


@test("Классификация успешного теста (PASS)")
def test_classify_pass():
    """
    Проверяет, что успешный тест классифицируется как PASS.
    """
    runner = TestRunner()
    
    # Создаем успешный тест
    test_func = create_test_func("test_pass", "assert True")
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Результат PASS:")
    print(f"   success: {result.success}")
    print(f"   error: {result.error}")
    print(f"   status: {result.status_text}")
    
    assert result.success is True
    assert result.error is None
    assert result.status_text == "PASSED"
    assert result.status_emoji == "✅"
    
    assert True


@test("Классификация падающего теста (FAIL)")
def test_classify_fail():
    """
    Проверяет, что тест с AssertionError классифицируется как FAIL.
    """
    runner = TestRunner()
    
    # Создаем падающий тест
    test_func = create_test_func("test_fail", "assert False, 'This test should fail'")
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Результат FAIL:")
    print(f"   success: {result.success}")
    print(f"   error: {result.error}")
    print(f"   status: {result.status_text}")
    
    assert result.success is False
    assert result.error is not None
    assert "AssertionError" in result.error
    assert "This test should fail" in result.error
    assert result.status_text == "FAILED"
    assert result.status_emoji == "❌"
    
    assert True


@test("Классификация теста с ошибкой (ERROR)")
def test_classify_error():
    """
    Проверяет, что тест с исключением (не AssertionError) классифицируется как ERROR.
    """
    runner = TestRunner()
    
    # Создаем тест с исключением
    test_func = create_test_func("test_error", "raise ValueError('Test exception')")
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Результат ERROR:")
    print(f"   success: {result.success}")
    print(f"   error: {result.error}")
    print(f"   status: {result.status_text}")
    
    assert result.success is False
    assert result.error is not None
    assert "ValueError" in result.error
    assert "Test exception" in result.error
    assert result.status_text == "FAILED"  # В нашей классификации FAIL = ERROR
    assert result.status_emoji == "❌"
    
    assert True


@test("Классификация ожидаемого падения (XPASS/XFAIL)")
def test_classify_expected():
    """
    Проверяет обработку expected_failure.
    """
    runner = TestRunner()
    
    # Тест с expected_failure=True, который падает (должен быть PASS)
    test_func_fail = create_test_func("test_expected_fail", "assert False")
    # Добавляем атрибут expected_failure
    test_func_fail.__dict__['expected_failure'] = True
    
    result_fail = runner.run_test(test_func_fail)
    
    print(f"\n📋 Ожидаемое падение (XFAIL):")
    print(f"   success: {result_fail.success}")
    print(f"   error: {result_fail.error}")
    
    assert result_fail.success is True  # Ожидаемое падение считается успехом
    assert "[EXPECTED FAILURE]" in result_fail.error
    
    # Тест с expected_failure=True, который проходит (должен быть FAIL)
    test_func_pass = create_test_func("test_expected_pass", "assert True")
    test_func_pass.__dict__['expected_failure'] = True
    
    result_pass = runner.run_test(test_func_pass)
    
    print(f"\n📋 Неожиданный успех (XPASS):")
    print(f"   success: {result_pass.success}")
    print(f"   error: {result_pass.error}")
    
    assert result_pass.success is False  # Неожиданный успех считается ошибкой
    assert "expected to fail but passed" in result_pass.error
    
    assert True


@test("Классификация теста с таймаутом")
def test_classify_timeout():
    """
    Проверяет классификацию теста, превысившего таймаут.
    """
    runner = TestRunner(timeout=1)
    
    # Создаем медленный тест
    test_func = create_test_func("test_slow", "import time; time.sleep(3)")
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Результат TIMEOUT:")
    print(f"   success: {result.success}")
    print(f"   error: {result.error}")
    
    assert result.success is False
    assert "Timeout" in result.error or "timeout" in result.error.lower()
    
    assert True


@test("Классификация в сессии со смешанными результатами")
def test_session_classification():
    """
    Проверяет классификацию в контексте полной сессии.
    """
    from utils.Tester.core.runner import TestSession
    
    session = TestSession(name="Classification Test")
    
    # Создаем разные типы результатов
    test_func_pass = create_test_func("test_pass", "assert True")
    test_func_fail = create_test_func("test_fail", "assert False")
    test_func_error = create_test_func("test_error", "raise ValueError('error')")
    
    runner = TestRunner()
    
    results = [
        runner.run_test(test_func_pass),
        runner.run_test(test_func_fail),
        runner.run_test(test_func_error),
    ]
    
    for result in results:
        session.add_result(result)
    
    session.finish()
    
    print(f"\n📋 Сессия со смешанными результатами:")
    print(f"   Всего: {session.total}")
    print(f"   PASS: {session.passed}")
    print(f"   FAIL: {session.failed}")
    
    assert session.total == 3
    assert session.passed == 1
    assert session.failed == 2
    
    # Проверяем, что можем получить упавшие тесты
    failed = session.get_failed_tests()
    assert len(failed) == 2
    
    # Проверяем группировку ошибок
    groups = session.group_errors()
    assert len(groups) >= 2  # AssertionError и ValueError
    
    for group in groups:
        print(f"   • {group.error_type}: {group.count}")
    
    assert True