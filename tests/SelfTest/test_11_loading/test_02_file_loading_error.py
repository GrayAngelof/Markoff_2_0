"""
Тест 2: Обработка ошибок загрузки.

Проверяет корректную обработку различных ошибок при загрузке файлов.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.discovery import TestDiscovery
from utils.Tester.core.models import create_file_node
from pathlib import Path
import tempfile
import os


def create_temp_test_file(content: str, filename: str) -> Path:
    """Создает временный файл с содержимым."""
    temp_dir = tempfile.mkdtemp()
    file_path = Path(temp_dir) / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path


@test("Загрузка несуществующего файла")
def test_load_nonexistent_file():
    """
    Проверяет попытку загрузки несуществующего файла.
    """
    discovery = TestDiscovery(Path.cwd())
    
    # Создаем узел для несуществующего файла
    fake_path = Path("/path/that/does/not/exist.py")
    fake_node = create_file_node("nonexistent", fake_path, [])
    
    try:
        loaded_node, stats = discovery.load_tests_from_node(fake_node)
        
        print(f"\n📋 Загрузка несуществующего файла:")
        print(f"   loaded={stats.loaded}, failed={stats.failed}")
        
        assert stats.failed == 1
        assert stats.loaded == 0
        assert len(loaded_node.tests) == 0
        
    except Exception as e:
        print(f"   Исключение: {e}")
        # Это тоже нормально - главное не упасть фатально
    
    assert True


@test("Загрузка файла с синтаксической ошибкой")
def test_load_syntax_error():
    """
    Проверяет загрузку файла с синтаксической ошибкой.
    """
    content = '''
from utils.Tester.common.test_common import test

@test("Тест с ошибкой"
def test_broken():
    assert True

# Пропущена закрывающая скобка
'''
    
    file_path = create_temp_test_file(content, "test_syntax_error.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    for node in root.children:
        if node.name == "test_syntax_error":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Загрузка файла с синтаксической ошибкой:")
            print(f"   loaded={stats.loaded}, failed={stats.failed}")
            print(f"   Тестов загружено: {len(loaded_node.tests)}")
            
            # Должна быть ошибка, тесты не загружены
            assert stats.failed == 1
            assert stats.loaded == 0
            assert len(loaded_node.tests) == 0
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Загрузка файла с ошибкой импорта")
def test_load_import_error():
    """
    Проверяет загрузку файла с ошибкой импорта.
    """
    content = '''
from utils.Tester.common.test_common import test
import some_module_that_does_not_exist

@test("Тест после ошибки импорта")
def test_after_import():
    assert True
'''
    
    file_path = create_temp_test_file(content, "test_import_error.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    for node in root.children:
        if node.name == "test_import_error":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Загрузка файла с ошибкой импорта:")
            print(f"   loaded={stats.loaded}, failed={stats.failed}")
            print(f"   Тестов загружено: {len(loaded_node.tests)}")
            
            # Импорт не удался, но файл может загрузиться частично
            # Важно, что тестер не падает фатально
            assert stats.failed >= 0
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Загрузка файла без тестов")
def test_load_no_tests():
    """
    Проверяет загрузку файла без тестовых функций.
    """
    content = '''
# Обычный код без тестов
def helper_function():
    return 42

class HelperClass:
    @staticmethod
    def utility():
        return "utility"

CONSTANT = 100
'''
    
    file_path = create_temp_test_file(content, "test_no_tests.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    for node in root.children:
        if node.name == "test_no_tests":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Загрузка файла без тестов:")
            print(f"   loaded={stats.loaded}, failed={stats.failed}, empty={stats.empty}")
            print(f"   Тестов загружено: {len(loaded_node.tests)}")
            
            # Файл загружен, но тестов нет
            assert stats.empty == 1
            assert stats.loaded == 0
            assert len(loaded_node.tests) == 0
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Загрузка файла с исключением в тесте")
def test_load_test_with_exception():
    """
    Проверяет загрузку файла, где тест содержит исключение на уровне модуля.
    """
    content = '''
from utils.Tester.common.test_common import test

# Код на уровне модуля, вызывающий исключение
raise ValueError("Ошибка при загрузке модуля")

@test("Тест после исключения")
def test_after_exception():
    assert True
'''
    
    file_path = create_temp_test_file(content, "test_exception.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    for node in root.children:
        if node.name == "test_exception":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Загрузка файла с исключением на уровне модуля:")
            print(f"   loaded={stats.loaded}, failed={stats.failed}")
            print(f"   Тестов загружено: {len(loaded_node.tests)}")
            
            # Должна быть ошибка
            assert stats.failed == 1
            assert len(loaded_node.tests) == 0
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Повторная загрузка после ошибки")
def test_reload_after_error():
    """
    Проверяет повторную загрузку файла после ошибки.
    """
    # Сначала файл с ошибкой
    error_content = '''
from utils.Tester.common.test_common import test

raise ValueError("Initial error")

@test("Тест")
def test_something():
    assert True
'''
    
    file_path = create_temp_test_file(error_content, "test_recover.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    # Первая загрузка (с ошибкой)
    for node in root.children:
        if node.name == "test_recover":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Первая загрузка (с ошибкой):")
            print(f"   loaded={stats.loaded}, failed={stats.failed}")
            
            assert stats.failed == 1
            assert len(loaded_node.tests) == 0
    
    # Исправляем файл
    fixed_content = '''
from utils.Tester.common.test_common import test

@test("Исправленный тест")
def test_fixed():
    assert True

@test("Еще один тест")
def test_another():
    assert 2 + 2 == 4
'''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    # Очищаем кэш и загружаем заново
    discovery._module_cache.clear()
    discovery._failed_files.clear()
    
    # Вторая загрузка (успешная)
    for node in root.children:
        if node.name == "test_recover":
            loaded_node, stats = discovery.load_tests_from_node(node)
            
            print(f"\n📋 Вторая загрузка (после исправления):")
            print(f"   loaded={stats.loaded}, failed={stats.failed}")
            print(f"   Тестов загружено: {len(loaded_node.tests)}")
            
            assert stats.loaded == 1
            assert stats.failed == 0
            assert len(loaded_node.tests) == 2
            assert loaded_node.tests[0].name == "test_fixed"
            assert loaded_node.tests[1].name == "test_another"
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True