"""
Тест 2: Запуск большого количества тестов.

Проверяет производительность и корректность выполнения
при большом количестве тестов.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.discovery import TestDiscovery
from utils.Tester.core.runner import TestRunner
from utils.Tester.core.executor import TestExecutor
from utils.Tester.utils.isolation import ShutdownHandler
from pathlib import Path
import tempfile
import time
import random


def generate_performance_test_file(file_num: int, test_count: int) -> str:
    """
    Генерирует файл с тестами разной сложности.
    """
    lines = ['"""', f"Тесты производительности #{file_num}", '"""', '']
    lines.append('from utils.Tester.common.test_common import test')
    lines.append('import time')
    lines.append('')
    
    for i in range(test_count):
        test_name = f"test_perf_{file_num}_{i}"
        
        # Разные типы тестов для разнообразной нагрузки
        test_type = i % 5
        
        if test_type == 0:
            # Очень быстрый тест
            lines.append(f'@test("Быстрый тест {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    assert 1 + 1 == 2')
        
        elif test_type == 1:
            # Тест с циклом
            lines.append(f'@test("Цикл {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    result = 0')
            lines.append('    for i in range(1000):')
            lines.append('        result += i')
            lines.append('    assert result == 499500')
        
        elif test_type == 2:
            # Тест со списками
            lines.append(f'@test("Списки {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    data = [i * 2 for i in range(500)]')
            lines.append('    assert len(data) == 500')
            lines.append('    assert sum(data) == 500 * 499')
        
        elif test_type == 3:
            # Тест со словарями
            lines.append(f'@test("Словари {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    data = {f"key{i}": i for i in range(200)}')
            lines.append('    assert len(data) == 200')
            lines.append('    assert data["key42"] == 42')
        
        else:
            # Тест с небольшим sleep
            lines.append(f'@test("Sleep {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    time.sleep(0.001)')  # 1ms
            lines.append('    assert True')
        
        lines.append('')
    
    return '\n'.join(lines)


def generate_large_test_suite(temp_dir: Path, num_files: int, tests_per_file: int) -> Path:
    """
    Генерирует большой набор тестовых файлов для выполнения.
    """
    suite_dir = temp_dir / "large_exec_suite"
    suite_dir.mkdir(exist_ok=True)
    
    for file_num in range(num_files):
        # Распределяем по поддиректориям для равномерной нагрузки
        sub_dir_num = file_num % 10
        sub_dir = suite_dir / f"group_{sub_dir_num}"
        sub_dir.mkdir(exist_ok=True)
        
        file_path = sub_dir / f"test_exec_{file_num:04d}.py"
        content = generate_performance_test_file(file_num, tests_per_file)
        file_path.write_text(content)
        
        if file_num % 100 == 0:
            print(f"   Создано {file_num}/{num_files} файлов...")
    
    total_tests = num_files * tests_per_file
    print(f"\n📦 Сгенерировано {num_files} файлов с {tests_per_file} тестов = {total_tests} тестов")
    
    return suite_dir


@test("Запуск 100 быстрых тестов")
def test_execute_100_fast():
    """
    Проверяет выполнение 100 быстрых тестов.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Генерируем 10 файлов по 10 тестов = 100 тестов
        suite_dir = generate_large_test_suite(temp_path, 10, 10)
        
        # Обнаруживаем тесты
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        all_tests = root.get_all_tests()
        
        print(f"\n🚀 Запуск {len(all_tests)} тестов...")
        
        # Создаем компоненты
        runner = TestRunner(timeout=5)
        shutdown = ShutdownHandler()
        executor = TestExecutor(runner, shutdown)
        
        # Замеряем время выполнения
        start_time = time.time()
        
        session = executor.run_selected(all_tests, "100 Fast Tests")
        
        exec_time = time.time() - start_time
        
        print(f"⏱️  Время выполнения: {exec_time:.3f}с")
        print(f"📊 Тестов в секунду: {len(all_tests)/exec_time:.1f} тестов/с")
        
        assert session is not None
        assert session.total == 100
        assert session.passed == 100
        assert session.failed == 0
        
        assert True


@test("Запуск 500 тестов разной сложности")
def test_execute_500_mixed():
    """
    Проверяет выполнение 500 тестов разной сложности.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 50 файлов по 10 тестов = 500 тестов
        suite_dir = generate_large_test_suite(temp_path, 50, 10)
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        all_tests = root.get_all_tests()
        
        print(f"\n🚀 Запуск {len(all_tests)} тестов разной сложности...")
        
        runner = TestRunner(timeout=5)
        shutdown = ShutdownHandler()
        executor = TestExecutor(runner, shutdown)
        
        start_time = time.time()
        
        session = executor.run_selected(all_tests, "500 Mixed Tests")
        
        exec_time = time.time() - start_time
        
        print(f"⏱️  Время выполнения: {exec_time:.3f}с")
        print(f"📊 Тестов в секунду: {len(all_tests)/exec_time:.1f} тестов/с")
        
        assert session is not None
        assert session.total == 500
        
        # Не все тесты могут пройти из-за разных типов, но проверим статистику
        print(f"📊 Пройдено: {session.passed}, Провалено: {session.failed}")
        
        assert session.passed + session.failed == 500
        
        assert True


@test("Запуск 1000 тестов с падениями")
def test_execute_1000_with_failures():
    """
    Проверяет выполнение 1000 тестов, часть из которых падает.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        suite_dir = temp_path / "mixed_results"
        suite_dir.mkdir()
        
        # Создаем файлы с разным соотношением успешных/падающих тестов
        for file_num in range(50):  # 50 файлов
            file_path = suite_dir / f"test_mixed_{file_num:04d}.py"
            
            lines = ['"""', f"Смешанные результаты #{file_num}", '"""', '']
            lines.append('from utils.Tester.common.test_common import test')
            lines.append('')
            
            # 20 тестов в файле
            for i in range(20):
                test_name = f"test_mixed_{file_num}_{i}"
                
                # Каждый 5-й тест падает
                if i % 5 == 0:
                    lines.append(f'@test("Падающий тест {test_name}")')
                    lines.append(f'def {test_name}():')
                    lines.append('    assert False, "Преднамеренное падение"')
                else:
                    lines.append(f'@test("Успешный тест {test_name}")')
                    lines.append(f'def {test_name}():')
                    lines.append('    assert True')
                
                lines.append('')
            
            file_path.write_text('\n'.join(lines))
        
        # Всего 50 * 20 = 1000 тестов
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        all_tests = root.get_all_tests()
        
        print(f"\n🚀 Запуск {len(all_tests)} тестов (20% падающих)...")
        
        runner = TestRunner(timeout=5)
        shutdown = ShutdownHandler()
        executor = TestExecutor(runner, shutdown)
        
        start_time = time.time()
        
        session = executor.run_selected(all_tests, "1000 Mixed Tests")
        
        exec_time = time.time() - start_time
        
        print(f"⏱️  Время выполнения: {exec_time:.3f}с")
        print(f"📊 Пройдено: {session.passed}, Провалено: {session.failed}")
        
        # Должно быть примерно 80% успешных, 20% падающих
        assert session.total == 1000
        assert session.passed == 800  # 4/5 от 1000
        assert session.failed == 200  # 1/5 от 1000
        
        assert True


@test("Запуск с fail-fast при больших нагрузках")
def test_execute_fail_fast_large():
    """
    Проверяет режим fail-fast при большом количестве тестов.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        suite_dir = temp_path / "fail_fast"
        suite_dir.mkdir()
        
        # Создаем файлы с ранним падением
        file_path = suite_dir / "test_fail_fast.py"
        
        lines = ['"""', "Тесты с ранним падением", '"""', '']
        lines.append('from utils.Tester.common.test_common import test')
        lines.append('')
        
        # Первый тест успешный
        lines.append('@test("Первый успешный")')
        lines.append('def test_first():')
        lines.append('    assert True')
        lines.append('')
        
        # Второй тест падает
        lines.append('@test("Падающий тест")')
        lines.append('def test_fail():')
        lines.append('    assert False, "Раннее падение"')
        lines.append('')
        
        # Остальные 98 тестов (не должны выполниться при fail-fast)
        for i in range(98):
            lines.append(f'@test("Тест {i} после падения")')
            lines.append(f'def test_after_{i}():')
            lines.append('    assert True, "Этот тест не должен выполняться"')
            lines.append('')
        
        file_path.write_text('\n'.join(lines))
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        all_tests = root.get_all_tests()
        
        print(f"\n🚀 Запуск {len(all_tests)} тестов с fail-fast...")
        
        runner = TestRunner(timeout=5, fail_fast=True)
        shutdown = ShutdownHandler()
        executor = TestExecutor(runner, shutdown)
        
        start_time = time.time()
        
        session = executor.run_selected(all_tests, "Fail Fast Test")
        
        exec_time = time.time() - start_time
        
        print(f"⏱️  Время выполнения: {exec_time:.3f}с")
        print(f"📊 Выполнено тестов: {session.total}")
        print(f"📊 Пройдено: {session.passed}, Провалено: {session.failed}")
        
        # Должны выполниться только первые 2 теста
        assert session.total == 2
        assert session.passed == 1
        assert session.failed == 1
        
        assert True