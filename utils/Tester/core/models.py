# utils/Tester/core/models.py
"""
Структуры данных для представления тестов.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Set, Tuple
from pathlib import Path
import hashlib


class NodeType:
    """Типы узлов дерева"""
    DIRECTORY = "directory"
    FILE = "file"
    ROOT = "root"


@dataclass(frozen=True)
class TestFunction:
    """Отдельная тестовая функция"""
    name: str
    description: str
    func: Callable[[], None]
    module_path: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    markers: Set[str] = field(default_factory=set)
    expected_failure: bool = False
    timeout: Optional[int] = None
    
    def __post_init__(self):
        if not self.name.startswith('test_'):
            raise ValueError(f"Имя теста должно начинаться с 'test_': {self.name}")
    
    @property
    def id(self) -> str:
        return f"{self.module_path}::{self.name}"
    
    @property
    def full_name(self) -> str:
        return f"{self.module_path}.{self.name}"
    
    def __call__(self) -> None:
        return self.func()


@dataclass(frozen=True)
class TestNode:
    """
    Узел в дереве тестов.
    """
    name: str
    path: Path
    node_type: str  # directory/file/root
    
    # Дети и тесты
    children: Tuple['TestNode', ...] = field(default_factory=tuple)
    tests: Tuple[TestFunction, ...] = field(default_factory=tuple)
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.node_type not in [NodeType.DIRECTORY, NodeType.FILE, NodeType.ROOT]:
            raise ValueError(f"Неверный тип узла: {self.node_type}")
        
        # Разрешаем файлам быть без тестов (для ленивой загрузки)
        if self.node_type == NodeType.FILE:
            if self.children:
                raise ValueError(f"Файл {self.name} не может содержать детей")
            # Тесты могут быть пустыми - это нормально для ленивой загрузки
        
        elif self.node_type == NodeType.DIRECTORY:
            if self.tests:
                raise ValueError(f"Директория {self.name} не может содержать тесты напрямую")
    
    @property
    def is_directory(self) -> bool:
        return self.node_type in [NodeType.DIRECTORY, NodeType.ROOT]
    
    @property
    def is_file(self) -> bool:
        return self.node_type == NodeType.FILE
    
    @property
    def display_name(self) -> str:
        if self.node_type == NodeType.ROOT:
            return "📁 tests (корень)"
        elif self.node_type == NodeType.DIRECTORY:
            return f"📁 {self.name}"
        else:
            return f"📄 {self.name}"
    
    def get_module_path(self) -> str:
        """Возвращает путь в формате модуля Python"""
        if self.node_type == NodeType.ROOT:
            return ""
        # Временно заглушка
        return self.name
    
    def get_all_tests(self) -> List[TestFunction]:
        """Рекурсивно собирает все тесты"""
        if self.is_file:
            return list(self.tests)
        
        all_tests = []
        for child in self.children:
            all_tests.extend(child.get_all_tests())
        return all_tests


# Фабрики для создания узлов
def create_file_node(name: str, path: Path, tests: List[TestFunction] = None) -> TestNode:
    """Создает файловый узел"""
    return TestNode(
        name=name,
        path=path,
        node_type=NodeType.FILE,
        tests=tuple(tests or [])
    )


def create_directory_node(name: str, path: Path, children: List[TestNode]) -> TestNode:
    """Создает узел директории"""
    return TestNode(
        name=name,
        path=path,
        node_type=NodeType.DIRECTORY,
        children=tuple(children)
    )


def create_root_node(path: Path, children: List[TestNode]) -> TestNode:
    """Создает корневой узел"""
    return TestNode(
        name="tests",
        path=path,
        node_type=NodeType.ROOT,
        children=tuple(children)
    )