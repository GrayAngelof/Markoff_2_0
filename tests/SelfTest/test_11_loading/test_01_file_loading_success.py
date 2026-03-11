"""
Тест 1: Успешная загрузка тестового файла.

Проверяет корректную загрузку тестового файла с разными типами тестов.
"""

from utils.Tester.common.test_common import test, TestHandler
from utils.Tester.core.discovery import TestDiscovery
from utils.Tester.core.models import TestFunction
from pathlib import Path
import tempfile
import os


def create_temp_test_file(content: str, filename: str = "test_temp.py") -> Path:
    """
    Создает временный файл с тестовым содержимым.
    """
    temp_dir = tempfile.mkdtemp()
    file_path = Path(temp_dir) / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path


@test("Загрузка файла с одним тестом")
def test_load_single_test():
    """
    Проверяет загрузку файла с одной тестовой функцией.
    """
    content = '''
from utils.Tester.common.test_common import test

@test("Простой тест")
def test_simple():
    assert 1 + 1 == 2
'''
    
    file_path = create_temp_test_file(content, "test_simple.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    # Создаем discovery и загружаем тесты
    discovery = TestDiscovery(tests_root, project_root)
    
    # Сканируем
    root = discovery.scan()
    
    # Находим наш файл
    test_files = [f for f in root.get_all_tests() if f.name == "test_simple"]
    
    # Загружаем тесты из файла
    for node in root.children:
        if node.name == "test_simple":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Загрузка файла с одним тестом:")
            print(f"   Статус: loaded={stats.loaded}, failed={stats.failed}")
            print(f"   Тестов в файле: {len(loaded_node.tests)}")
            
            assert stats.loaded == 1
            assert stats.failed == 0
            assert len(loaded_node.tests) == 1
            assert loaded_node.tests[0].name == "test_simple"
            assert loaded_node.tests[0].description == "Простой тест"
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Загрузка файла с несколькими тестами")
def test_load_multiple_tests():
    """
    Проверяет загрузку файла с несколькими тестовыми функциями.
    """
    content = '''
from utils.Tester.common.test_common import test

@test("Первый тест")
def test_first():
    assert True

@test("Второй тест")
def test_second():
    assert 2 * 2 == 4

@test("Третий тест", markers={"slow"})
def test_third():
    import time
    time.sleep(0.01)
    assert "hello".upper() == "HELLO"
'''
    
    file_path = create_temp_test_file(content, "test_multiple.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    for node in root.children:
        if node.name == "test_multiple":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Загрузка файла с 3 тестами:")
            print(f"   Загружено: {stats.loaded}")
            print(f"   Тесты: {[t.name for t in loaded_node.tests]}")
            
            assert stats.loaded == 1
            assert len(loaded_node.tests) == 3
            assert loaded_node.tests[0].name == "test_first"
            assert loaded_node.tests[1].name == "test_second"
            assert loaded_node.tests[2].name == "test_third"
            assert "slow" in loaded_node.tests[2].markers
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Загрузка файла с тестами в классе")
def test_load_class_tests():
    """
    Проверяет загрузку тестов, определенных внутри классов.
    """
    content = '''
from utils.Tester.common.test_common import test

class TestMath:
    @test("Сложение")
    def test_addition(self):
        assert 1 + 1 == 2
    
    @test("Умножение")
    def test_multiplication(self):
        assert 2 * 3 == 6

class TestString:
    @test("Верхний регистр")
    def test_upper(self):
        assert "hello".upper() == "HELLO"
    
    @test("Нижний регистр")
    def test_lower(self):
        assert "HELLO".lower() == "hello"
'''
    
    file_path = create_temp_test_file(content, "test_class.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    for node in root.children:
        if node.name == "test_class":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            test_names = [t.name for t in loaded_node.tests]
            
            print(f"\n📋 Загрузка тестов из классов:")
            print(f"   Тесты: {test_names}")
            
            assert len(loaded_node.tests) == 4
            assert "test_addition" in test_names
            assert "test_multiplication" in test_names
            assert "test_upper" in test_names
            assert "test_lower" in test_names
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Загрузка файла с маркерами")
def test_load_with_markers():
    """
    Проверяет загрузку тестов с различными маркерами.
    """
    content = '''
from utils.Tester.common.test_common import test, TestMarker

@test("Быстрый тест", markers={"smoke", "fast"})
def test_fast():
    assert True

@test("Медленный тест", markers={"slow", "integration"})
def test_slow():
    assert True

@test("Сетевой тест", markers={"network"})
def test_network():
    assert True

@test("Смешанные маркеры", markers={TestMarker.SMOKE, "database"})
def test_mixed():
    assert True
'''
    
    file_path = create_temp_test_file(content, "test_markers.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    for node in root.children:
        if node.name == "test_markers":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Загрузка тестов с маркерами:")
            
            for test in loaded_node.tests:
                print(f"   {test.name}: {test.markers}")
            
            assert len(loaded_node.tests) == 4
            
            # Проверяем маркеры
            markers_dict = {t.name: t.markers for t in loaded_node.tests}
            
            assert "smoke" in markers_dict["test_fast"]
            assert "fast" in markers_dict["test_fast"]
            assert "slow" in markers_dict["test_slow"]
            assert "integration" in markers_dict["test_slow"]
            assert "network" in markers_dict["test_network"]
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Загрузка файла с ожидаемыми падениями")
def test_load_expected_failures():
    """
    Проверяет загрузку тестов с expected_failure.
    """
    content = '''
from utils.Tester.common.test_common import test

@test("Обычный тест")
def test_normal():
    assert True

@test("Ожидаемое падение", expected_failure=True)
def test_expected_fail():
    assert False

@test("Еще одно ожидаемое", expected_failure=True)
def test_another_fail():
    raise ValueError("This is expected")
'''
    
    file_path = create_temp_test_file(content, "test_expected.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    for node in root.children:
        if node.name == "test_expected":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Загрузка тестов с expected_failure:")
            
            for test in loaded_node.tests:
                expected = getattr(test, 'expected_failure', False)
                print(f"   {test.name}: expected_failure={expected}")
            
            assert len(loaded_node.tests) == 3
            
            # Проверяем expected_failure
            assert not getattr(loaded_node.tests[0], 'expected_failure', False)
            assert getattr(loaded_node.tests[1], 'expected_failure', False)
            assert getattr(loaded_node.tests[2], 'expected_failure', False)
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True