"""
Тест 3: Работа кеширования тестовых файлов.

Проверяет корректное кеширование загруженных тестовых файлов
и поведение при повторных загрузках.
"""

from utils.Tester.common.test_common import test
from utils.Tester.core.discovery import TestDiscovery
from pathlib import Path
import tempfile
import os
import time


def create_temp_test_file(content: str, filename: str) -> Path:
    """Создает временный файл с содержимым."""
    temp_dir = tempfile.mkdtemp()
    file_path = Path(temp_dir) / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path


@test("Кеширование при повторной загрузке")
def test_cache_repeated_load():
    """
    Проверяет, что повторная загрузка того же файла берется из кеша.
    """
    content = '''
from utils.Tester.common.test_common import test

load_counter = 0

@test("Тест с счетчиком")
def test_counter():
    global load_counter
    load_counter += 1
    assert True
'''
    
    file_path = create_temp_test_file(content, "test_cache.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    # Находим наш файл
    test_node = None
    for node in root.children:
        if node.name == "test_cache":
            test_node = node
            break
    
    assert test_node is not None
    
    # Первая загрузка
    print(f"\n📋 Первая загрузка:")
    loaded_node1, stats1 = discovery.load_tests_from_node(test_node)
    assert stats1.loaded == 1
    
    # Проверяем, что файл в кеше
    assert file_path in discovery._module_cache
    
    # Вторая загрузка (должна быть из кеша)
    print(f"\n📋 Вторая загрузка (из кеша):")
    loaded_node2, stats2 = discovery.load_tests_from_node(test_node)
    assert stats2.loaded == 0  # Из кеша, счетчик не увеличивается
    
    # Оба узла должны быть одним и тем же объектом
    assert loaded_node1 is loaded_node2
    
    print(f"   Первая загрузка: loaded={stats1.loaded}")
    print(f"   Вторая загрузка: loaded={stats2.loaded} (из кеша)")
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Инвалидация кеша при перезагрузке")
def test_cache_invalidation():
    """
    Проверяет, что кеш очищается при полной перезагрузке.
    """
    content = '''
from utils.Tester.common.test_common import test

@test("Тест")
def test_something():
    assert True
'''
    
    file_path = create_temp_test_file(content, "test_invalidate.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    # Находим наш файл
    test_node = None
    for node in root.children:
        if node.name == "test_invalidate":
            test_node = node
            break
    
    # Первая загрузка
    loaded_node1, stats1 = discovery.load_tests_from_node(test_node)
    assert stats1.loaded == 1
    assert file_path in discovery._module_cache
    
    print(f"\n📋 После первой загрузки:")
    print(f"   В кеше: {file_path in discovery._module_cache}")
    
    # Перезагружаем
    discovery.reload()
    
    print(f"\n📋 После перезагрузки:")
    print(f"   В кеше: {file_path in discovery._module_cache}")
    
    # Кеш должен быть пуст
    assert file_path not in discovery._module_cache
    
    # Вторая загрузка (должна загрузить заново)
    loaded_node2, stats2 = discovery.load_tests_from_node(test_node)
    assert stats2.loaded == 1
    
    print(f"   Повторная загрузка: loaded={stats2.loaded}")
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Кеширование разных файлов")
def test_cache_multiple_files():
    """
    Проверяет кеширование нескольких разных файлов.
    """
    # Создаем два тестовых файла
    content1 = '''
from utils.Tester.common.test_common import test

@test("Тест из файла 1")
def test_file1():
    assert True
'''
    
    content2 = '''
from utils.Tester.common.test_common import test

@test("Тест из файла 2")
def test_file2():
    assert True
    
@test("Еще тест из файла 2")
def test_file2_another():
    assert True
'''
    
    file_path1 = create_temp_test_file(content1, "test_file1.py")
    file_path2 = create_temp_test_file(content2, "test_file2.py")
    
    tests_root = file_path1.parent  # Оба в одной директории
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    # Находим узлы
    node1 = None
    node2 = None
    for node in root.children:
        if node.name == "test_file1":
            node1 = node
        elif node.name == "test_file2":
            node2 = node
    
    # Загружаем первый файл
    loaded1, stats1 = discovery.load_tests_from_node(node1)
    assert stats1.loaded == 1
    
    # Загружаем второй файл
    loaded2, stats2 = discovery.load_tests_from_node(node2)
    assert stats2.loaded == 1
    
    print(f"\n📋 Кеширование двух файлов:")
    print(f"   Файл1 в кеше: {file_path1 in discovery._module_cache}")
    print(f"   Файл2 в кеше: {file_path2 in discovery._module_cache}")
    print(f"   Размер кеша: {len(discovery._module_cache)}")
    
    # Оба должны быть в кеше
    assert file_path1 in discovery._module_cache
    assert file_path2 in discovery._module_cache
    assert len(discovery._module_cache) == 2
    
    # Повторная загрузка (из кеша)
    loaded1_again, stats1_again = discovery.load_tests_from_node(node1)
    loaded2_again, stats2_again = discovery.load_tests_from_node(node2)
    
    assert stats1_again.loaded == 0
    assert stats2_again.loaded == 0
    assert loaded1 is loaded1_again
    assert loaded2 is loaded2_again
    
    print(f"   Повторная загрузка: из кеша")
    
    # Очистка
    os.unlink(file_path1)
    os.unlink(file_path2)
    os.rmdir(file_path1.parent)
    
    assert True


@test("Кеширование после изменения файла")
def test_cache_after_modification():
    """
    Проверяет поведение кеша при изменении файла на диске.
    """
    content_initial = '''
from utils.Tester.common.test_common import test

@test("Первая версия")
def test_v1():
    assert True
'''
    
    file_path = create_temp_test_file(content_initial, "test_modify.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    # Находим узел
    test_node = None
    for node in root.children:
        if node.name == "test_modify":
            test_node = node
            break
    
    # Первая загрузка
    loaded1, stats1 = discovery.load_tests_from_node(test_node)
    assert stats1.loaded == 1
    assert len(loaded1.tests) == 1
    assert loaded1.tests[0].name == "test_v1"
    
    print(f"\n📋 Первая загрузка: тест 'test_v1'")
    
    # Изменяем файл
    content_modified = '''
from utils.Tester.common.test_common import test

@test("Вторая версия")
def test_v2():
    assert True

@test("Новый тест")
def test_new():
    assert 2 + 2 == 4
'''
    
    time.sleep(0.1)  # Небольшая пауза, чтобы время модификации изменилось
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content_modified)
    
    # Повторная загрузка (все еще из кеша, если не очистили)
    loaded2, stats2 = discovery.load_tests_from_node(test_node)
    
    print(f"\n📋 После изменения файла (без очистки кеша):")
    print(f"   loaded={stats2.loaded} (0 = из кеша)")
    print(f"   Тестов: {len(loaded2.tests)}")
    
    # Должна быть загрузка из кеша (старая версия)
    assert stats2.loaded == 0
    assert len(loaded2.tests) == 1
    assert loaded2.tests[0].name == "test_v1"
    
    # Очищаем кеш вручную
    discovery._module_cache.clear()
    discovery._failed_files.clear()
    
    # Загрузка после очистки кеша
    loaded3, stats3 = discovery.load_tests_from_node(test_node)
    
    print(f"\n📋 После очистки кеша:")
    print(f"   loaded={stats3.loaded}")
    print(f"   Тестов: {len(loaded3.tests)}")
    
    # Должна загрузиться новая версия
    assert stats3.loaded == 1
    assert len(loaded3.tests) == 2
    assert loaded3.tests[0].name == "test_v2"
    assert loaded3.tests[1].name == "test_new"
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Получение закешированного узла")
def test_get_cached_node():
    """
    Проверяет метод get_cached_node.
    """
    content = '''
from utils.Tester.common.test_common import test

@test("Тест для кеша")
def test_cached():
    assert True
'''
    
    file_path = create_temp_test_file(content, "test_get_cache.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    # Сначала кеш пуст
    assert discovery.get_cached_node(file_path) is None
    
    # Находим узел
    test_node = None
    for node in root.children:
        if node.name == "test_get_cache":
            test_node = node
            break
    
    # Загружаем
    discovery.load_tests_from_node(test_node)
    
    # Теперь должен быть в кеше
    cached = discovery.get_cached_node(file_path)
    assert cached is not None
    assert len(cached.tests) == 1
    assert cached.tests[0].name == "test_cached"
    
    print(f"\n📋 get_cached_node:")
    print(f"   До загрузки: None")
    print(f"   После загрузки: {cached.name} с {len(cached.tests)} тестом")
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True


@test("Проверка загрузки файла")
def test_is_file_loaded():
    """
    Проверяет метод is_file_loaded.
    """
    content = '''
from utils.Tester.common.test_common import test

@test("Тест")
def test_something():
    assert True
'''
    
    file_path = create_temp_test_file(content, "test_loaded.py")
    tests_root = file_path.parent
    project_root = Path.cwd()
    
    discovery = TestDiscovery(tests_root, project_root)
    root = discovery.scan()
    
    # Сначала не загружен
    assert not discovery.is_file_loaded(file_path)
    
    # Находим узел
    test_node = None
    for node in root.children:
        if node.name == "test_loaded":
            test_node = node
            break
    
    # Загружаем
    discovery.load_tests_from_node(test_node)
    
    # Теперь должен быть загружен
    assert discovery.is_file_loaded(file_path)
    
    print(f"\n📋 is_file_loaded:")
    print(f"   До загрузки: False")
    print(f"   После загрузки: True")
    
    # Очистка
    os.unlink(file_path)
    os.rmdir(file_path.parent)
    
    assert True