"""
Тест 2: Целостность собранных результатов.

Проверяет, что все данные тестов корректно сохраняются
и не теряются в процессе выполнения.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestRunner, TestSession, TestOutput
from utils.Tester.core.models import TestFunction
from utils.Tester.ui.reporter import TestReporter, ReportConfig
import io
import sys


def create_verbose_test_func(name: str, stdout: str, stderr: str = "") -> TestFunction:
    """
    Создает тестовую функцию с заданным выводом.
    """
    def _func():
        if stdout:
            print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)
        return True
    
    return TestFunction(
        name=name,
        description=f"Test with output",
        func=_func,
        module_path="test.integrity",
        file_path=None,
        line_number=42
    )


@test("Целостность вывода stdout")
def test_stdout_integrity():
    """
    Проверяет, что stdout сохраняется полностью и без искажений.
    """
    runner = TestRunner()
    
    # Тест с многострочным выводом
    expected_stdout = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    
    def test_with_output():
        print("Line 1")
        print("Line 2")
        print("Line 3")
        print("Line 4")
        print("Line 5")
    
    test_func = TestFunction(
        name="test_output",
        description="",
        func=test_with_output,
        module_path="test.integrity",
        file_path=None,
        line_number=42
    )
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Проверка целостности stdout:")
    print(f"   Ожидалось: {repr(expected_stdout)}")
    print(f"   Получено:  {repr(result.output.stdout)}")
    
    assert result.output.stdout == expected_stdout
    assert result.output.stderr == ""
    
    assert True


@test("Целостность вывода stderr")
def test_stderr_integrity():
    """
    Проверяет, что stderr сохраняется полностью и без искажений.
    """
    runner = TestRunner()
    
    expected_stderr = "Error: something went wrong\nWarning: deprecated"
    
    def test_with_error():
        import sys
        print("Error: something went wrong", file=sys.stderr)
        print("Warning: deprecated", file=sys.stderr)
    
    test_func = TestFunction(
        name="test_stderr",
        description="",
        func=test_with_error,
        module_path="test.integrity",
        file_path=None,
        line_number=42
    )
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Проверка целостности stderr:")
    print(f"   Ожидалось: {repr(expected_stderr)}")
    print(f"   Получено:  {repr(result.output.stderr)}")
    
    assert result.output.stderr == expected_stderr
    assert result.output.stdout == ""
    
    assert True


@test("Целостность смешанного вывода")
def test_mixed_output_integrity():
    """
    Проверяет, что stdout и stderr не перемешиваются.
    """
    runner = TestRunner()
    
    expected_stdout = "stdout line 1\nstdout line 2"
    expected_stderr = "stderr line 1\nstderr line 2"
    
    def test_mixed():
        import sys
        print("stdout line 1")
        print("stderr line 1", file=sys.stderr)
        print("stdout line 2")
        print("stderr line 2", file=sys.stderr)
    
    test_func = TestFunction(
        name="test_mixed",
        description="",
        func=test_mixed,
        module_path="test.integrity",
        file_path=None,
        line_number=42
    )
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Проверка разделения потоков:")
    print(f"   stdout: {repr(result.output.stdout)}")
    print(f"   stderr: {repr(result.output.stderr)}")
    
    assert result.output.stdout == expected_stdout
    assert result.output.stderr == expected_stderr
    
    # Проверяем, что строки не перепутаны
    assert "stderr" not in result.output.stdout
    assert "stdout" not in result.output.stderr
    
    assert True


@test("Целостность метаданных теста")
def test_metadata_integrity():
    """
    Проверяет, что все метаданные теста сохраняются в результате.
    """
    runner = TestRunner()
    
    def sample_test():
        assert True
    
    test_func = TestFunction(
        name="test_metadata",
        description="This is a test description",
        func=sample_test,
        module_path="test.module.path",
        file_path=None,
        line_number=123,
        markers={"smoke", "fast", "unit"}
    )
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Проверка метаданных:")
    print(f"   name: {result.test.name}")
    print(f"   description: {result.test.description}")
    print(f"   module: {result.test.module_path}")
    print(f"   line: {result.test.line_number}")
    print(f"   markers: {result.test.markers}")
    
    assert result.test.name == "test_metadata"
    assert result.test.description == "This is a test description"
    assert result.test.module_path == "test.module.path"
    assert result.test.line_number == 123
    assert "smoke" in result.test.markers
    assert "fast" in result.test.markers
    assert "unit" in result.test.markers
    
    assert True


@test("Целостность traceback")
def test_traceback_integrity():
    """
    Проверяет, что traceback сохраняется полностью.
    """
    runner = TestRunner()
    
    def level1():
        level2()
    
    def level2():
        level3()
    
    def level3():
        raise ValueError("Test exception with traceback")
    
    test_func = TestFunction(
        name="test_traceback",
        description="",
        func=level1,
        module_path="test.integrity",
        file_path=None,
        line_number=42
    )
    
    result = runner.run_test(test_func)
    
    print(f"\n📋 Проверка traceback:")
    print(f"   error: {result.error}")
    print(f"   traceback: {result.traceback[:200]}...")
    
    assert result.error is not None
    assert "ValueError" in result.error
    assert result.traceback is not None
    assert "level3" in result.traceback
    assert "level2" in result.traceback
    assert "level1" in result.traceback
    
    assert True


@test("Целостность длительности выполнения")
def test_duration_integrity():
    """
    Проверяет, что длительность выполнения сохраняется корректно.
    """
    runner = TestRunner()
    import time
    
    def test_with_delay():
        time.sleep(0.1)
    
    test_func = TestFunction(
        name="test_duration",
        description="",
        func=test_with_delay,
        module_path="test.integrity",
        file_path=None,
        line_number=42
    )
    
    start = time.time()
    result = runner.run_test(test_func)
    end = time.time()
    
    print(f"\n📋 Проверка длительности:")
    print(f"   Измерено тестером: {result.duration:.3f}s")
    print(f"   Реальное время: {end - start:.3f}s")
    
    assert result.duration > 0.05
    assert result.duration < 0.2
    assert abs(result.duration - (end - start)) < 0.05
    
    assert True


@test("Целостность результатов в сессии")
def test_session_integrity():
    """
    Проверяет, что все результаты в сессии сохраняют целостность.
    """
    from utils.Tester.core.runner import TestSession
    
    session = TestSession(name="Integrity Test")
    
    # Создаем несколько тестов с разным выводом
    outputs = [
        ("test1", "Output 1", ""),
        ("test2", "", "Error 2"),
        ("test3", "Mixed\noutput", "Mixed\nerror"),
    ]
    
    for name, stdout, stderr in outputs:
        def make_func(stdout, stderr):
            def _func():
                if stdout:
                    print(stdout)
                if stderr:
                    import sys
                    print(stderr, file=sys.stderr)
                return True
            return _func
        
        test_func = TestFunction(
            name=name,
            description="",
            func=make_func(stdout, stderr),
            module_path="test.session",
            file_path=None,
            line_number=42
        )
        
        runner = TestRunner()
        result = runner.run_test(test_func)
        session.add_result(result)
    
    session.finish()
    
    print(f"\n📋 Проверка целостности сессии:")
    print(f"   Всего тестов: {session.total}")
    
    for i, result in enumerate(session.results):
        print(f"\n   Тест {i+1}: {result.test.name}")
        print(f"     stdout: {repr(result.output.stdout)}")
        print(f"     stderr: {repr(result.output.stderr)}")
        
        assert result.test.name == outputs[i][0]
        assert result.output.stdout == outputs[i][1]
        assert result.output.stderr == outputs[i][2]
    
    assert True