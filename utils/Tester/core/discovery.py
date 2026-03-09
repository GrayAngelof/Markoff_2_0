# utils/Tester/core/discovery.py
"""
Модуль сканирования файловой системы и загрузки тестов.
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging
from dataclasses import dataclass  # <-- ЭТО БЫЛО ПРОПУЩЕНО

from ..common.test_common import is_test_function, create_test_function
from .models import TestNode, TestFunction

# Импортируем утилиты
from ..utils.helpers import (
    is_test_file,
    path_to_module,
    find_files,
    generate_test_id,
    load_json_config
)

logger = logging.getLogger(__name__)


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
    Обнаруживает и загружает тесты с использованием утилит.
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
        
        # Загружаем конфиг, если есть
        self._config = load_json_config(self.project_root / "config" / "tester_config.json")
    
    def scan(self) -> TestNode:
        """Сканирует файловую систему и строит дерево тестов."""
        if self._root_node is None:
            logger.info(f"Сканирование {self.tests_root}")
            self._root_node = self._build_node(self.tests_root)
            logger.info(f"Найдено {self._count_nodes(self._root_node)} элементов")
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
            if is_test_file(path):
                logger.debug(f"Найден файл с тестами: {path.name}")
                return TestNode(
                    name=path.stem,
                    path=path,
                    node_type="file",
                    tests=()  # тесты пока не загружаем
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
        
        node_type = "root" if path == self.tests_root else "directory"
        node_name = "tests" if path == self.tests_root else path.name
        
        return TestNode(
            name=node_name,
            path=path,
            node_type=node_type,
            children=tuple(children)
        )
    
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
            logger.error(f"Ошибка при загрузке узла {node.name}: {e}", exc_info=True)
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
            
            loaded_node = TestNode(
                name=node.name,
                path=node.path,
                node_type="file",
                tests=tuple(tests)
            )
            
            if tests:
                stats.loaded = 1
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
            
            empty_node = TestNode(
                name=node.name,
                path=node.path,
                node_type="file",
                tests=()
            )
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
        
        loaded_node = TestNode(
            name=node.name,
            path=node.path,
            node_type=node.node_type,
            children=tuple(loaded_children)
        )
        
        return loaded_node, total_stats
    
    def _extract_tests_from_file(self, file_path: Path) -> List[TestFunction]:
        """Извлекает тесты из файла."""
        module_name = path_to_module(file_path, self.project_root)
        
        try:
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            
            tests = []
            for name, obj in inspect.getmembers(module, is_test_function):
                try:
                    test_func = create_test_function(obj)
                    tests.append(test_func)
                    logger.debug(f"Найден тест: {name}")
                except Exception as e:
                    logger.error(f"Ошибка при создании теста {name}: {e}")
            
            return tests
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке модуля {module_name}: {e}")
            return []
    
    def get_test_by_id(self, test_id: str) -> Optional[TestFunction]:
        """Находит тест по его ID."""
        from ..utils.helpers import parse_test_id
        
        try:
            module_path, test_name = parse_test_id(test_id)
        except ValueError:
            logger.error(f"Неверный формат test_id: {test_id}")
            return None
        
        rel_path = module_path.replace('.', '/') + '.py'
        file_path = self.project_root / rel_path
        
        if not file_path.exists():
            logger.error(f"Файл не найден: {file_path}")
            return None
        
        loaded_node = self._module_cache.get(file_path)
        if not loaded_node:
            # Пытаемся загрузить
            temp_node = TestNode(
                name=file_path.stem,
                path=file_path,
                node_type="file",
                tests=()
            )
            loaded_node, _ = self._load_tests_from_file(temp_node)
        
        for test in loaded_node.tests:
            if test.name == test_name:
                return test
        
        logger.error(f"Тест {test_name} не найден в {module_path}")
        return None
    
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
    
    def reload(self):
        """Полная перезагрузка."""
        logger.info("Перезагрузка всех тестов")
        self._module_cache.clear()
        self._failed_files.clear()
        self._root_node = self._build_node(self.tests_root)
        
    def get_cached_node(self, path: Path) -> Optional[TestNode]:
        """
        Публичный метод для получения загруженного узла из кэша.
        
        Args:
            path: Путь к файлу
        
        Returns:
            Optional[TestNode]: Загруженный узел или None
        """
        return self._module_cache.get(path)
    
    def is_file_loaded(self, path: Path) -> bool:
        """
        Проверяет, загружен ли файл в кэш.
        
        Args:
            path: Путь к файлу
        
        Returns:
            bool: True если файл загружен
        """
        return path in self._module_cache
    
    def get_failed_files(self) -> List[Path]:
        """
        Возвращает список файлов, которые не удалось загрузить.
        
        Returns:
            List[Path]: Список проблемных файлов
        """
        return list(self._failed_files)