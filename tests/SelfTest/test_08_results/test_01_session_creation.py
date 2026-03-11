"""
Тест 1: Создание сессии тестирования.

Проверяет, что сессия тестирования правильно создается
и содержит корректные метаданные.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestSession, TestResult
from utils.Tester.core.models import TestFunction
from datetime import datetime
import time


@test("Создание пустой сессии")
def test_empty_session():
    """
    Проверяет создание пустой сессии.
    """
    # Создаем сессию
    session = TestSession(name="Empty Test Session")
    
    # Проверяем базовые атрибуты
    assert session.name == "Empty Test Session"
    assert session.total == 0
    assert session.passed == 0
    assert session.failed == 0
    assert session.results == []
    assert session.start_time is not None
    assert session.end_time is None
    
    print(f"✅ Пустая сессия создана: {session.name}")
    print(f"   Время старта: {session.start_time}")
    
    # Завершаем сессию
    session.finish()
    assert session.end_time is not None
    print(f"   Время завершения: {session.end_time}")
    print(f"   Длительность: {session.duration:.3f}s")
    
    assert True


@test("Создание сессии с именем")
def test_session_naming():
    """
    Проверяет различные варианты именования сессий.
    """
    names = [
        "All Tests",
        "Client Tests",
        "Backend Tests",
        "Integration Tests",
        "Unit Tests",
        "Test Session #42",
        "Сессия с русским названием",
        "Session with emoji 🧪"
    ]
    
    for name in names:
        session = TestSession(name=name)
        assert session.name == name
        print(f"✅ Сессия: '{name}'")
        session.finish()
    
    assert True


@test("Создание сессии с результатами")
def test_session_with_results():
    """
    Проверяет создание сессии с предварительными результатами.
    """
    from ..core.models import TestFunction
    
    # Создаем тестовую функцию
    def dummy_func():
        pass
    
    test_func = TestFunction(
        name="test_dummy",
        description="Dummy test",
        func=dummy_func,
        module_path="test.module",
        file_path=None,
        line_number=42
    )
    
    # Создаем результат
    from ..core.runner import TestOutput
    result = TestResult(
        test=test_func,
        success=True,
        duration=0.123,
        output=TestOutput(stdout="test output", stderr=""),
        error=None
    )
    
    # Создаем сессию и добавляем результат
    session = TestSession(name="Test with Results")
    session.add_result(result)
    
    assert session.total == 1
    assert session.passed == 1
    assert session.failed == 0
    assert len(session.results) == 1
    assert session.results[0] == result
    
    print(f"✅ Сессия с результатом:")
    print(f"   Всего: {session.total}")
    print(f"   Пройдено: {session.passed}")
    print(f"   Провалено: {session.failed}")
    
    session.finish()
    assert True


@test("Проверка временных меток сессии")
def test_session_timestamps():
    """
    Проверяет корректность временных меток сессии.
    """
    start_before = datetime.now()
    
    # Создаем сессию
    session = TestSession(name="Timestamp Test")
    start_after = datetime.now()
    
    # Проверяем, что start_time между start_before и start_after
    assert start_before <= session.start_time <= start_after
    
    # Небольшая задержка
    time.sleep(0.1)
    
    # Завершаем сессию
    end_before = datetime.now()
    session.finish()
    end_after = datetime.now()
    
    # Проверяем, что end_time между end_before и end_after
    assert end_before <= session.end_time <= end_after
    
    # Проверяем, что duration положительный
    assert session.duration > 0
    assert session.duration < 1.0  # Должно быть меньше секунды
    
    print(f"✅ Временные метки корректны:")
    print(f"   Start: {session.start_time}")
    print(f"   End:   {session.end_time}")
    print(f"   Duration: {session.duration:.3f}s")
    
    assert True