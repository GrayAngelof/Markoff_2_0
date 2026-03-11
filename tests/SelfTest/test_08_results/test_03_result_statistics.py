"""
Тест 3: Статистика результатов.

Проверяет корректный подсчет статистики по результатам тестов.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.runner import TestSession, TestResult, TestOutput
from utils.Tester.core.models import TestFunction
import random


def create_test_func(name: str) -> TestFunction:
    """Создает тестовую функцию."""
    def dummy():
        pass
    return TestFunction(
        name=name,
        description="",
        func=dummy,
        module_path="test.stats",
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


@test("Подсчет базовой статистики")
def test_basic_statistics():
    """
    Проверяет базовый подсчет количества тестов.
    """
    session = TestSession(name="Basic Stats")
    
    # Добавляем 10 тестов: 7 успешных, 3 падающих
    for i in range(7):
        session.add_result(create_result(f"pass_{i}", True, 0.1))
    
    for i in range(3):
        session.add_result(create_result(f"fail_{i}", False, 0.15))
    
    session.finish()
    
    # Проверяем статистику
    assert session.total == 10
    assert session.passed == 7
    assert session.failed == 3
    assert session.success_rate == 70.0
    
    # Проверяем получение упавших тестов
    failed = session.get_failed_tests()
    assert len(failed) == 3
    assert all(not r.success for r in failed)
    
    print(f"📊 Статистика:")
    print(f"   Всего: {session.total}")
    print(f"   ✅ Пройдено: {session.passed}")
    print(f"   ❌ Провалено: {session.failed}")
    print(f"   📈 Успешность: {session.success_rate}%")
    
    assert True


@test("Подсчет с разными пропорциями")
def test_various_proportions():
    """
    Проверяет подсчет статистики при разных пропорциях.
    """
    proportions = [
        (10, 0, 100.0),   # Все успешные
        (0, 10, 0.0),     # Все падающие
        (5, 5, 50.0),     # Поровну
        (8, 2, 80.0),     # 80% успешных
        (2, 8, 20.0),     # 20% успешных
        (1, 0, 100.0),    # Один успешный
        (0, 1, 0.0),      # Один падающий
    ]
    
    for passed, failed, expected_rate in proportions:
        session = TestSession(name=f"Stats {passed}/{failed}")
        
        for i in range(passed):
            session.add_result(create_result(f"pass_{i}", True))
        for i in range(failed):
            session.add_result(create_result(f"fail_{i}", False))
        
        session.finish()
        
        assert session.total == passed + failed
        assert session.passed == passed
        assert session.failed == failed
        assert abs(session.success_rate - expected_rate) < 0.001
        
        print(f"   {passed}/{failed} -> {session.success_rate:.1f}%")
    
    assert True


@test("Группировка ошибок по типам")
def test_error_grouping():
    """
    Проверяет группировку ошибок по типам.
    """
    session = TestSession(name="Error Groups")
    
    # Создаем ошибки разных типов
    error_patterns = [
        ("AssertionError", "assert failed", 3),
        ("ValueError", "invalid value", 2),
        ("TypeError", "bad type", 4),
        ("KeyError", "missing key", 1),
        ("TimeoutError", "timeout", 2),
    ]
    
    for err_type, err_msg, count in error_patterns:
        for i in range(count):
            test_func = create_test_func(f"{err_type}_{i}")
            result = TestResult(
                test=test_func,
                success=False,
                duration=0.1,
                output=TestOutput(),
                error=f"{err_type}: {err_msg} #{i}"
            )
            session.add_result(result)
    
    session.finish()
    
    # Получаем группы ошибок
    groups = session.group_errors()
    
    # Проверяем количество групп
    assert len(groups) == len(error_patterns)
    
    # Проверяем каждую группу
    for err_type, _, count in error_patterns:
        group = next((g for g in groups if g.error_type == err_type), None)
        assert group is not None, f"Группа {err_type} не найдена"
        assert group.count == count
        assert len(group.tests) == count
        assert len(group.examples) > 0
    
    print(f"\n📊 Группировка ошибок:")
    for group in groups:
        print(f"   • {group.error_type}: {group.count} тестов")
        if group.examples:
            print(f"     Пример: {group.examples[0]}")
    
    assert True


@test("Пустая сессия")
def test_empty_session_stats():
    """
    Проверяет статистику пустой сессии.
    """
    session = TestSession(name="Empty Session")
    session.finish()
    
    assert session.total == 0
    assert session.passed == 0
    assert session.failed == 0
    assert session.success_rate == 0.0
    assert session.get_failed_tests() == []
    assert session.group_errors() == []
    
    print("✅ Пустая сессия: статистика корректна")
    assert True


@test("Статистика с разными длительностями")
def test_duration_statistics():
    """
    Проверяет статистику с разными длительностями тестов.
    """
    session = TestSession(name="Duration Stats")
    
    durations = [0.1, 0.2, 0.3, 0.4, 0.5, 1.0, 1.5, 2.0]
    
    for i, d in enumerate(durations):
        success = i % 2 == 0
        session.add_result(create_result(f"test_{i}", success, d))
    
    session.finish()
    
    # Проверяем общее время
    expected_total = sum(durations)
    assert abs(session.total_time - expected_total) < 0.01
    
    # Проверяем длительность сессии (должна быть меньше суммы)
    assert session.duration < session.total_time
    
    print(f"⏱️  Суммарное время тестов: {session.total_time:.2f}s")
    print(f"⏱️  Время сессии: {session.duration:.2f}s")
    
    assert True