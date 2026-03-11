"""
Тест 1: Обнаружение большого количества тестов.

Проверяет производительность и корректность обнаружения
при большом количестве тестовых файлов и функций.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.discovery import TestDiscovery
from pathlib import Path
import tempfile
import os
import time
import random
import string


def generate_test_file(file_num: int, test_count: int) -> str:
    """
    Генерирует содержимое тестового файла с указанным количеством тестов.
    """
    lines = ['"""', f"Автоматически сгенерированный тестовый файл #{file_num}", '"""', '']
    lines.append('from utils.Tester.common.test_common import test')
    lines.append('import time')
    lines.append('')
    
    # Добавляем вспомогательные функции
    lines.append('def helper_function(x):')
    lines.append('    return x * 2')
    lines.append('')
    
    # Генерируем тесты
    for i in range(test_count):
        test_name = f"test_file{file_num}_{i}"
        
        # Разные типы тестов
        if i % 3 == 0:
            # Простой тест
            lines.append(f'@test("Тест {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    assert True')
        elif i % 3 == 1:
            # Тест с вычислениями
            lines.append(f'@test("Тест с вычислениями {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    result = sum(range(100))')
            lines.append('    assert result == 4950')
        else:
            # Тест с helper
            lines.append(f'@test("Тест с helper {test_name}")')
            lines.append(f'def {test_name}():')
            lines.append('    x = 21')
            lines.append('    assert helper_function(x) == 42')
        
        lines.append('')
    
    return '\n'.join(lines)


def generate_large_test_suite(temp_dir: Path, num_files: int, tests_per_file: int) -> Path:
    """
    Генерирует большой набор тестовых файлов.
    
    Returns:
        Path: Путь к корневой директории с тестами
    """
    suite_dir = temp_dir / "large_test_suite"
    suite_dir.mkdir(exist_ok=True)
    
    # Создаем вложенную структуру для дополнительной сложности
    categories = ['core', 'utils', 'api', 'models', 'services']
    
    total_tests = 0
    
    for file_num in range(num_files):
        # Распределяем файлы по категориям
        category = random.choice(categories)
        cat_dir = suite_dir / category
        cat_dir.mkdir(exist_ok=True)
        
        # Создаем поддиректории для некоторых файлов
        if file_num % 5 == 0:
            sub_dir = cat_dir / f"sub_{file_num % 3}"
            sub_dir.mkdir(exist_ok=True)
            file_path = sub_dir / f"test_stress_{file_num:04d}.py"
        else:
            file_path = cat_dir / f"test_stress_{file_num:04d}.py"
        
        content = generate_test_file(file_num, tests_per_file)
        file_path.write_text(content)
        total_tests += tests_per_file
        
        if file_num % 20 == 0:
            print(f"   Создано {file_num}/{num_files} файлов...")
    
    print(f"\n📦 Сгенерировано {num_files} файлов с ~{tests_per_file} тестов в каждом")
    print(f"📊 Всего тестов: {total_tests}")
    
    return suite_dir


@test("Обнаружение 100 файлов с 10 тестами в каждом")
def test_discovery_100x10():
    """
    Проверяет обнаружение 100 файлов по 10 тестов (1000 тестов).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print("\n🚀 Генерация 100 файлов с 10 тестами...")
        suite_dir = generate_large_test_suite(temp_path, 100, 10)
        
        # Замеряем время обнаружения
        start_time = time.time()
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        
        scan_time = time.time() - start_time
        print(f"\n⏱️  Время сканирования: {scan_time:.3f}с")
        
        # Проверяем структуру
        all_tests = root.get_all_tests()
        
        print(f"📊 Найдено файлов: {len(root.children)}")
        print(f"📊 Найдено тестов: {len(all_tests)}")
        
        # Должно быть около 1000 тестов (может немного отличаться из-за структуры)
        assert len(all_tests) >= 900
        assert len(all_tests) <= 1100
        assert scan_time < 5.0  # Должно сканироваться быстро
        
        # Проверяем, что все тесты имеют правильные имена
        for test_func in all_tests[:10]:  # Проверяем первые 10
            assert test_func.name.startswith('test_file')
            assert test_func.description
        
        assert True


@test("Обнаружение 500 файлов с 5 тестами в каждом")
def test_discovery_500x5():
    """
    Проверяет обнаружение 500 файлов по 5 тестов (2500 тестов).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print("\n🚀 Генерация 500 файлов с 5 тестами...")
        suite_dir = generate_large_test_suite(temp_path, 500, 5)
        
        start_time = time.time()
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        
        scan_time = time.time() - start_time
        print(f"\n⏱️  Время сканирования: {scan_time:.3f}с")
        
        all_tests = root.get_all_tests()
        
        print(f"📊 Найдено тестов: {len(all_tests)}")
        
        assert len(all_tests) >= 2400
        assert len(all_tests) <= 2600
        assert scan_time < 10.0  # Должно сканироваться за разумное время
        
        assert True


@test("Обнаружение с глубокой вложенностью")
def test_discovery_deep_nesting():
    """
    Проверяет обнаружение тестов в глубокой вложенности директорий.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        suite_dir = temp_path / "deep_nesting"
        
        # Создаем глубокую структуру
        current_dir = suite_dir
        for level in range(10):
            current_dir = current_dir / f"level_{level}"
            current_dir.mkdir(parents=True, exist_ok=True)
            
            # Добавляем несколько тестовых файлов на каждом уровне
            for i in range(3):
                file_path = current_dir / f"test_level{level}_{i}.py"
                content = generate_test_file(level * 10 + i, 2)
                file_path.write_text(content)
        
        print("\n🚀 Создана структура с глубиной 10 уровней")
        
        start_time = time.time()
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        
        scan_time = time.time() - start_time
        print(f"⏱️  Время сканирования: {scan_time:.3f}с")
        
        all_tests = root.get_all_tests()
        
        # Должно быть 10 уровней * 3 файла * 2 теста = 60 тестов
        print(f"📊 Найдено тестов: {len(all_tests)}")
        
        assert len(all_tests) == 60
        assert scan_time < 3.0
        
        assert True


@test("Обнаружение с максимальной нагрузкой")
def test_discovery_max_load():
    """
    Проверяет обнаружение при максимальной нагрузке (1000 файлов).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print("\n🚀 Генерация 1000 файлов с 2 тестами в каждом...")
        suite_dir = generate_large_test_suite(temp_path, 1000, 2)
        
        start_time = time.time()
        
        discovery = TestDiscovery(suite_dir)
        root = discovery.scan()
        
        scan_time = time.time() - start_time
        print(f"\n⏱️  Время сканирования: {scan_time:.3f}с")
        
        all_tests = root.get_all_tests()
        
        print(f"📊 Найдено тестов: {len(all_tests)}")
        
        assert len(all_tests) >= 1900
        assert len(all_tests) <= 2100
        assert scan_time < 15.0  # Должно быть приемлемо
        
        # Проверяем использование памяти
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        print(f"📊 Использование памяти: {memory_mb:.1f} MB")
        assert memory_mb < 500  # Не должно превышать 500MB
        
        assert True