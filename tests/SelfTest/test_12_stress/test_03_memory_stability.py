"""
Тест 3: Стабильность использования памяти.

Проверяет, что тестер не накапливает память при выполнении
большого количества тестов и корректно освобождает ресурсы.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.discovery import TestDiscovery
from utils.Tester.core.runner import TestRunner
from utils.Tester.core.executor import TestExecutor
from utils.Tester.utils.isolation import ShutdownHandler
from pathlib import Path
import tempfile
import time
import gc
import os


def generate_memory_test_file(file_num: int, test_count: int) -> str:
    """
    Генерирует файл с тестами, создающими нагрузку на память.
    """
    lines = ['"""', f"Тесты памяти #{file_num}", '"""', '']
    lines.append('from utils.Tester.common.test_common import test')
    lines.append('import gc')
    lines.append('')
    
    for i in range(test_count):
        test_name = f"test_mem_{file_num}_{i}"
        
        if i % 3 == 0:
            # Тест, создающий большие структуры данных
            lines.append(f'@test("Большие данные {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    data = [i for i in range(10000)]')
            lines.append('    assert len(data) == 10000')
            lines.append('    # Явно удаляем')
            lines.append('    del data')
            lines.append('    gc.collect()')
        
        elif i % 3 == 1:
            # Тест со словарями
            lines.append(f'@test("Большие словари {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    data = {f"key{i}": i for i in range(5000)}')
            lines.append('    assert len(data) == 5000')
            lines.append('    del data')
        
        else:
            # Тест со строками
            lines.append(f'@test("Большие строки {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    text = "x" * 100000')
            lines.append('    assert len(text) == 100000')
            lines.append('    del text')
        
        lines.append('')
    
    return '\n'.join(lines)


def get_memory_usage() -> float:
    """
    Возвращает использование памяти в MB.
    """
    import psutil
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


@test("Мониторинг памяти при загрузке 500 файлов")
def test_memory_discovery():
    """
    Проверяет использование памяти при обнаружении большого количества файлов.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        suite_dir = temp_path / "memory_discovery"
        suite_dir.mkdir()
        
        # Создаем 500 файлов
        print("\n🚀 Генерация 500 файлов для теста памяти...")
        
        for file_num in range(500):
            file_path = suite_dir / f"test_mem_{file_num:04d}.py"
            content = generate_memory_test_file(file_num, 5)  # 5 тестов в файле
            file_path.write_text(content)
            
            if file_num % 100 == 0:
                print(f"   Создано {file_num}/500 файлов...")
        
        # Замеряем память до загрузки
        gc.collect()
        memory_before = get_memory_usage()
        print(f"\n📊 Память до загрузки: {memory_before:.1f} MB")
        
        # Загружаем все тесты
        start_time = time.time()
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        
        # Загружаем все файлы рекурсивно
        loaded_node, stats = discovery.load_tests_from_node(root, recursive=True)
        
        load_time = time.time() - start_time
        
        # Замеряем память после загрузки
        memory_after = get_memory_usage()
        memory_increase = memory_after - memory_before
        
        print(f"⏱️  Время загрузки: {load_time:.3f}с")
        print(f"📊 Память после загрузки: {memory_after:.1f} MB")
        print(f"📈 Прирост памяти: {memory_increase:.1f} MB")
        
        all_tests = loaded_node.get_all_tests()
        print(f"📊 Загружено тестов: {len(all_tests)}")
        
        # Проверяем, что память не выросла катастрофически
        # На 500 файлов по 5 тестов разумно ~100-200 MB
        assert memory_increase < 300, f"Слишком большой прирост памяти: {memory_increase:.1f} MB"
        
        # Очищаем
        del discovery
        del loaded_node
        gc.collect()
        
        # Память после очистки
        memory_after_cleanup = get_memory_usage()
        print(f"📊 Память после очистки: {memory_after_cleanup:.1f} MB")
        
        # Должна освободиться
        assert memory_after_cleanup < memory_after
        
        assert True


@test("Утечки памяти при выполнении тестов")
def test_memory_execution_leaks():
    """
    Проверяет, что нет утечек памяти при многократном выполнении тестов.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        suite_dir = temp_path / "memory_exec"
        suite_dir.mkdir()
        
        # Создаем файл с тестами
        file_path = suite_dir / "test_memory_leak.py"
        content = generate_memory_test_file(0, 20)  # 20 тестов
        file_path.write_text(content)
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        
        # Загружаем тесты
        for node in root.children:
            if node.name == "test_memory_leak":
                loaded_node, _ = discovery.load_tests_from_node(node)
                tests = list(loaded_node.tests)
                break
        
        print(f"\n🚀 Запуск тестов для проверки утечек памяти...")
        
        # Многократно выполняем тесты
        memory_readings = []
        
        for iteration in range(10):
            # Создаем новые компоненты для каждой итерации
            runner = TestRunner(timeout=5)
            shutdown = ShutdownHandler()
            executor = TestExecutor(runner, shutdown)
            
            # Запускаем тесты
            session = executor.run_selected(tests, f"Iteration {iteration}")
            
            # Замеряем память
            gc.collect()
            memory = get_memory_usage()
            memory_readings.append(memory)
            
            print(f"   Итерация {iteration+1}: {memory:.1f} MB")
            
            # Явно удаляем компоненты
            del runner
            del shutdown
            del executor
            del session
            gc.collect()
        
        print(f"\n📊 Замеры памяти по итерациям:")
        for i, m in enumerate(memory_readings):
            print(f"   {i+1}: {m:.1f} MB")
        
        # Проверяем, что память не растет линейно
        # Последний замер не должен быть значительно больше первого
        first = memory_readings[0]
        last = memory_readings[-1]
        increase = last - first
        
        print(f"📈 Рост памяти: {increase:.1f} MB")
        
        # Допустимый рост (может быть небольшой из-за кеширования)
        assert increase < 50, f"Память растет: {increase:.1f} MB за 10 итераций"
        
        assert True


@test("Стабильность при длительном выполнении")
def test_long_running_stability():
    """
    Проверяет стабильность при длительном выполнении множества тестов.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        suite_dir = temp_path / "long_run"
        suite_dir.mkdir()
        
        # Создаем 100 файлов с тестами
        print("\n🚀 Генерация 100 файлов для длительного теста...")
        
        for file_num in range(100):
            file_path = suite_dir / f"test_long_{file_num:04d}.py"
            content = generate_memory_test_file(file_num, 10)  # 10 тестов в файле
            file_path.write_text(content)
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        
        # Загружаем все тесты
        loaded_node, _ = discovery.load_tests_from_node(root, recursive=True)
        all_tests = loaded_node.get_all_tests()
        
        print(f"📊 Всего тестов: {len(all_tests)}")
        
        # Замеряем память до начала
        gc.collect()
        memory_before = get_memory_usage()
        print(f"📊 Память до выполнения: {memory_before:.1f} MB")
        
        # Выполняем тесты несколько раз
        memory_points = [memory_before]
        execution_times = []
        
        for run in range(5):
            print(f"\n🚀 Запуск #{run+1}...")
            
            runner = TestRunner(timeout=5)
            shutdown = ShutdownHandler()
            executor = TestExecutor(runner, shutdown)
            
            start_time = time.time()
            session = executor.run_selected(all_tests, f"Long Run {run}")
            exec_time = time.time() - start_time
            execution_times.append(exec_time)
            
            print(f"⏱️  Время выполнения: {exec_time:.3f}с")
            
            # Замеряем память после выполнения
            gc.collect()
            memory = get_memory_usage()
            memory_points.append(memory)
            print(f"📊 Память после запуска: {memory:.1f} MB")
            
            # Проверяем результаты
            assert session.total == len(all_tests)
            print(f"📊 Пройдено: {session.passed}, Провалено: {session.failed}")
            
            # Очищаем
            del runner
            del shutdown
            del executor
            del session
            gc.collect()
        
        print(f"\n📈 Тренд памяти:")
        for i, m in enumerate(memory_points):
            change = m - memory_points[0]
            print(f"   {i}: {m:.1f} MB ({change:+.1f} MB)")
        
        # Проверяем, что время выполнения стабильно
        avg_time = sum(execution_times) / len(execution_times)
        print(f"\n⏱️  Среднее время: {avg_time:.3f}с")
        
        for i, t in enumerate(execution_times):
            deviation = abs(t - avg_time) / avg_time * 100
            print(f"   Запуск {i+1}: {t:.3f}с (отклонение {deviation:.1f}%)")
            assert deviation < 30  # Отклонение не более 30%
        
        # Память не должна сильно вырасти
        final_increase = memory_points[-1] - memory_points[0]
        print(f"\n📈 Общий рост памяти: {final_increase:.1f} MB")
        assert final_increase < 100
        
        assert True


@test("Очистка ресурсов после выполнения")
def test_resource_cleanup():
    """
    Проверяет, что все ресурсы корректно освобождаются после выполнения.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        suite_dir = temp_path / "cleanup"
        suite_dir.mkdir()
        
        # Создаем тестовые файлы
        for i in range(50):
            file_path = suite_dir / f"test_cleanup_{i:04d}.py"
            content = generate_memory_test_file(i, 10)
            file_path.write_text(content)
        
        # Замеряем память до
        gc.collect()
        memory_before = get_memory_usage()
        print(f"\n📊 Память до: {memory_before:.1f} MB")
        
        # Создаем компоненты
        discovery = TestDiscovery(suite_dir)
        runner = TestRunner(timeout=5)
        shutdown = ShutdownHandler()
        executor = TestExecutor(runner, shutdown)
        
        # Загружаем и выполняем тесты
        root = discovery.scan()
        loaded_node, _ = discovery.load_tests_from_node(root, recursive=True)
        all_tests = loaded_node.get_all_tests()
        
        print(f"📊 Загружено тестов: {len(all_tests)}")
        
        session = executor.run_selected(all_tests, "Cleanup Test")
        
        # Замеряем память во время выполнения
        memory_during = get_memory_usage()
        print(f"📊 Память во время: {memory_during:.1f} MB")
        
        # Удаляем все ссылки
        del discovery
        del runner
        del shutdown
        del executor
        del loaded_node
        del session
        del all_tests
        
        # Принудительная сборка мусора
        gc.collect()
        
        # Замеряем память после
        memory_after = get_memory_usage()
        print(f"📊 Память после очистки: {memory_after:.1f} MB")
        
        # Память должна вернуться к уровню до (или близко)
        memory_increase = memory_after - memory_before
        print(f"📈 Остаточный рост: {memory_increase:.1f} MB")
        
        # Допускаем небольшой остаточный рост из-за кеширования
        assert memory_increase < 20
        
        assert True