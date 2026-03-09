# utils/Tester/core/discovery.py
"""
Модуль сканирования файловой системы и загрузки тестов.
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

# Вместо import logging
from utils.logger import get_logger

from ..common.test_common import is_test_function, create_test_function
from .models import TestNode, TestFunction

# Создаем логгер для этого модуля
logger = get_logger(__name__)


@dataclass
class LoadStats:
    """Статистика загрузки для отчетов"""
    loaded: int = 0
    failed: int = 0
    empty: int = 0
    
    def add(self, other: 'LoadStats') -> 'LoadStats':
        return LoadStats(
            loaded=self.loaded + other.loaded,
            failed=self.failed + other.failed,
            empty=self.empty + other.empty
        )


class TestDiscovery:
    """
    Обнаруживает и загружает тесты из файловой системы.
    """
    
    def __init__(self, tests_root: Path, project_root: Optional[Path] = None):
        self.tests_root = tests_root.resolve()
        
        if project_root:
            self.project_root = project_root.resolve()
        else:
            self.project_root = self.tests_root.parent
        
        self._root_node: Optional[TestNode] = None
        self._module_cache: Dict[Path, TestNode] = {}
        self._failed_files: Set[Path] = set()
        
        # Добавляем корень проекта в sys.path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
            logger.debug(f"Добавлен {self.project_root} в sys.path")
    
    def scan(self) -> TestNode:
        """Сканирует файловую систему и строит дерево тестов."""
        if self._root_node is None:
            logger.info(f"Сканирование {self.tests_root}")
            self._root_node = self._build_node(self.tests_root)
            logger.success(f"Найдено {self._count_nodes(self._root_node)} элементов")
        return self._root_node
    
    def _count_nodes(self, node: TestNode) -> int:
        """Подсчитывает количество узлов в дереве."""
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count
    
    def _build_node(self, path: Path) -> Optional[TestNode]:
        """Рекурсивно строит узел дерева."""
        if path.is_file():
            if path.name.startswith('test_') and path.suffix == '.py' and path.name != '__init__.py':
                logger.debug(f"Найден файл с тестами: {path.name}")
                from .models import create_file_node
                return create_file_node(
                    name=path.stem,
                    path=path,
                    tests=[]  # тесты пока не загружаем
                )
            return None
        
        # Директория
        children = []
        for item in sorted(path.iterdir()):
            if item.name.startswith('__') or item.name.startswith('.'):
                continue
            
            child_node = self._build_node(item)
            if child_node:
                children.append(child_node)
        
        if not children:
            return None
        
        from .models import create_directory_node, create_root_node
        
        if path == self.tests_root:
            return create_root_node(path, children)
        else:
            return create_directory_node(path.name, path, children)
    
    def load_tests_from_node(self, node: TestNode, recursive: bool = False) -> Tuple[TestNode, LoadStats]:
        """
        Загружает тесты из указанного узла.
        """
        try:
            if node.node_type == "file":
                return self._load_tests_from_file(node)
            elif node.node_type in ("directory", "root"):
                if not recursive:
                    raise ValueError(
                        f"Узел '{node.name}' - директория. Используйте recursive=True"
                    )
                return self._load_tests_from_directory(node)
            else:
                raise ValueError(f"Неизвестный тип узла: {node.node_type}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке узла {node.name}: {e}")
            return node, LoadStats()
    
    def _load_tests_from_file(self, node: TestNode) -> Tuple[TestNode, LoadStats]:
        """Загружает тесты из файлового узла."""
        stats = LoadStats()
        
        if node.path in self._module_cache:
            logger.debug(f"Загружено из кэша: {node.path.name}")
            return self._module_cache[node.path], stats
        
        logger.info(f"Загрузка тестов из {node.path.name}")
        
        try:
            tests = self._extract_tests_from_file(node.path)
            
            from .models import create_file_node
            loaded_node = create_file_node(node.name, node.path, tests)
            
            if tests:
                stats.loaded = 1
                logger.success(f"Загружено {len(tests)} тестов из {node.path.name}")
                self._failed_files.discard(node.path)
            else:
                stats.empty = 1
                logger.warning(f"Файл {node.path.name} не содержит тестов")
                self._failed_files.add(node.path)
            
            self._module_cache[node.path] = loaded_node
            return loaded_node, stats
            
        except Exception as e:
            stats.failed = 1
            logger.error(f"Не удалось загрузить файл {node.path.name}: {e}")
            self._failed_files.add(node.path)
            
            from .models import create_file_node
            empty_node = create_file_node(node.name, node.path, [])
            return empty_node, stats
    
    def _load_tests_from_directory(self, node: TestNode) -> Tuple[TestNode, LoadStats]:
        """Рекурсивно загружает тесты из директории."""
        logger.info(f"Рекурсивная загрузка тестов из {node.name}")
        
        total_stats = LoadStats()
        loaded_children = []
        
        for child in node.children:
            try:
                if child.node_type == "file":
                    loaded_child, child_stats = self._load_tests_from_file(child)
                else:
                    loaded_child, child_stats = self._load_tests_from_directory(child)
                
                loaded_children.append(loaded_child)
                total_stats = total_stats.add(child_stats)
            except Exception as e:
                logger.error(f"Ошибка при загрузке {child.path}: {e}")
                total_stats.failed += 1
        
        from .models import create_directory_node
        loaded_node = create_directory_node(node.name, node.path, loaded_children)
        
        if total_stats.failed > 0:
            logger.warning(f"Директория {node.name}: загружено {total_stats.loaded}, ошибок {total_stats.failed}")
        else:
            logger.success(f"Директория {node.name}: загружено {total_stats.loaded} файлов")
        
        return loaded_node, total_stats
    
    def _extract_tests_from_file(self, file_path: Path) -> List[TestFunction]:
        """Извлекает тесты из файла."""
        from ..utils.helpers import path_to_module
        
        module_name = path_to_module(file_path, self.project_root)
        
        try:
            if module_name in sys.modules:
                logger.debug(f"Перезагрузка модуля {module_name}")
                module = importlib.reload(sys.modules[module_name])
            else:
                logger.debug(f"Импорт модуля {module_name}")
                module = importlib.import_module(module_name)
            
            tests = []
            for name, obj in inspect.getmembers(module, is_test_function):
                try:
                    from ..common.test_common import create_test_function
                    test_func = create_test_function(obj)
                    tests.append(test_func)
                    logger.debug(f"Найден тест: {name}")
                except Exception as e:
                    logger.error(f"Ошибка при создании теста {name}: {e}")
            
            return tests
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке модуля {module_name}: {e}")
            return []
    
    def get_cached_node(self, path: Path) -> Optional[TestNode]:
        """Возвращает загруженный узел из кэша."""
        return self._module_cache.get(path)
    
    def is_file_loaded(self, path: Path) -> bool:
        """Проверяет, загружен ли файл в кэш."""
        return path in self._module_cache
    
    def get_failed_files(self) -> List[Path]:
        """Возвращает список файлов, которые не удалось загрузить."""
        return list(self._failed_files)
    
    def get_statistics(self) -> dict:
        """Возвращает статистику по тестам."""
        root = self.scan()
        
        def count_files(node: TestNode) -> int:
            if node.node_type == "file":
                return 1
            return sum(count_files(child) for child in node.children)
        
        def count_tests(node: TestNode) -> int:
            if node.node_type == "file":
                if node.path in self._module_cache:
                    return len(self._module_cache[node.path].tests)
                return 0
            return sum(count_tests(child) for child in node.children)
        
        def count_loaded(node: TestNode) -> int:
            if node.node_type == "file":
                return 1 if node.path in self._module_cache else 0
            return sum(count_loaded(child) for child in node.children)
        
        total_files = count_files(root)
        loaded_files = count_loaded(root)
        
        return {
            'total_files': total_files,
            'loaded_files': loaded_files,
            'failed_files': len(self._failed_files),
            'total_tests': count_tests(root),
            'cached_modules': len(self._module_cache),
            'failed_files_list': list(self._failed_files)
        }
    
    def reload(self) -> None:
        """Полная перезагрузка."""
        logger.info("Перезагрузка всех тестов")
        self._module_cache.clear()
        self._failed_files.clear()
        self._root_node = self._build_node(self.tests_root)
        logger.success("Перезагрузка завершена")