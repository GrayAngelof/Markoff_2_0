# utils/Tester/ui/navigation.py
"""
Навигация по дереву тестов и пагинация.
Чистые компоненты с четкими интерфейсами и обработкой ошибок.
"""

from typing import List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
import logging
from pathlib import Path

from ..core.models import TestNode, TestFunction
from ..core.discovery import TestDiscovery

logger = logging.getLogger(__name__)


class NavigationError(Exception):
    """Базовое исключение для ошибок навигации"""
    pass


class FileLoadError(NavigationError):
    """Ошибка загрузки файла с тестами"""
    pass


class IndexError(NavigationError):
    """Ошибка индекса элемента"""
    pass


@dataclass
class LoadResult:
    """Результат загрузки файла с тестами"""
    success: bool
    node: Optional[TestNode] = None
    tests_count: int = 0
    error_message: Optional[str] = None
    error_details: Optional[str] = None
    
    @property
    def has_tests(self) -> bool:
        return self.tests_count > 0
    
    @property
    def failed(self) -> bool:
        return not self.success


class PaginatedList:
    """
    Пагинированный список с поддержкой глобальных и локальных индексов.
    """
    
    def __init__(self, items: List[Any], page_size: int = 10):
        """
        Args:
            items: Список элементов
            page_size: Количество элементов на странице
        """
        self.items = items
        self.page_size = page_size
        self.current_page = 0
        self._validate()
    
    def _validate(self):
        """Валидация параметров"""
        if self.page_size <= 0:
            raise ValueError(f"page_size должен быть > 0, получено {self.page_size}")
    
    @property
    def total_pages(self) -> int:
        """Общее количество страниц"""
        return (len(self.items) + self.page_size - 1) // self.page_size if self.items else 1
    
    @property
    def current_page_items(self) -> List[Any]:
        """Элементы текущей страницы"""
        if not self.items:
            return []
        start = self.current_page * self.page_size
        end = min(start + self.page_size, len(self.items))
        return self.items[start:end]
    
    @property
    def global_start_index(self) -> int:
        """Глобальный индекс первого элемента на текущей странице (1-based)"""
        return self.current_page * self.page_size + 1
    
    @property
    def global_end_index(self) -> int:
        """Глобальный индекс последнего элемента на текущей странице (1-based)"""
        return min(self.global_start_index + self.page_size - 1, len(self.items))
    
    def next_page(self) -> bool:
        """
        Переход на следующую страницу.
        
        Returns:
            bool: True если переход выполнен, False если уже последняя страница
        """
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            return True
        return False
    
    def prev_page(self) -> bool:
        """
        Переход на предыдущую страницу.
        
        Returns:
            bool: True если переход выполнен, False если уже первая страница
        """
        if self.current_page > 0:
            self.current_page -= 1
            return True
        return False
    
    def go_to_page(self, page: int) -> bool:
        """
        Переход на указанную страницу.
        
        Args:
            page: Номер страницы (0-based)
        
        Returns:
            bool: True если переход выполнен
        """
        if 0 <= page < self.total_pages:
            self.current_page = page
            return True
        return False
    
    def get_by_global_index(self, index: int) -> Optional[Any]:
        """
        Получение элемента по глобальному индексу (1-based).
        
        Args:
            index: Глобальный индекс (от 1 до len(items))
        
        Returns:
            Optional[Any]: Элемент или None если индекс вне диапазона
        """
        if 1 <= index <= len(self.items):
            return self.items[index - 1]
        return None
    
    def get_by_local_index(self, index: int) -> Optional[Any]:
        """
        Получение элемента по локальному индексу на текущей странице (1-based).
        
        Args:
            index: Локальный индекс на странице (от 1 до page_size)
        
        Returns:
            Optional[Any]: Элемент или None если индекс вне диапазона
        """
        if 1 <= index <= len(self.current_page_items):
            return self.current_page_items[index - 1]
        return None
    
    def global_to_local(self, global_index: int) -> Optional[int]:
        """
        Преобразует глобальный индекс в локальный на текущей странице.
        
        Args:
            global_index: Глобальный индекс (1-based)
        
        Returns:
            Optional[int]: Локальный индекс или None если элемент не на текущей странице
        """
        if self.global_start_index <= global_index <= self.global_end_index:
            return global_index - self.global_start_index + 1
        return None
    
    def get_display_range(self) -> str:
        """
        Возвращает строку вида "1-10/50" для отображения.
        """
        if not self.items:
            return "0/0"
        return f"{self.global_start_index}-{self.global_end_index}/{len(self.items)}"
    
    def reset(self):
        """Сброс к первой странице"""
        self.current_page = 0


class NavigationStack:
    """
    Стек навигации по дереву тестов с защитой от некорректных переходов.
    """
    
    def __init__(self, root: TestNode):
        """
        Args:
            root: Корневой узел дерева тестов
        """
        if root is None:
            raise ValueError("root не может быть None")
        
        self.root = root
        self.stack: List[TestNode] = [root]
    
    @property
    def current(self) -> TestNode:
        """Текущий узел"""
        return self.stack[-1]
    
    @property
    def depth(self) -> int:
        """Глубина текущей позиции (1 = корень)"""
        return len(self.stack)
    
    def push(self, node: TestNode) -> bool:
        """
        Переход в дочерний узел.
        
        Args:
            node: Дочерний узел для перехода
        
        Returns:
            bool: True если переход выполнен, False если узел не является дочерним
        
        Raises:
            NavigationError: При попытке перехода в None
        """
        if node is None:
            raise NavigationError("Нельзя перейти в None узел")
        
        if node not in self.current.children:
            logger.warning(f"Попытка перехода в {node.name}, который не является дочерним {self.current.name}")
            return False
        
        self.stack.append(node)
        logger.debug(f"Переход: {self.current.name} -> {node.name}")
        return True
    
    def pop(self) -> Optional[TestNode]:
        """
        Возврат на уровень выше.
        
        Returns:
            Optional[TestNode]: Предыдущий узел или None если уже в корне
        """
        if len(self.stack) <= 1:
            logger.debug("Попытка выхода из корня")
            return None
        
        popped = self.stack.pop()
        logger.debug(f"Возврат: {popped.name} -> {self.current.name}")
        return popped
    
    def can_go_back(self) -> bool:
        """Можно ли вернуться назад"""
        return len(self.stack) > 1
    
    def reset(self):
        """Сброс к корню"""
        self.stack = [self.root]
        logger.debug("Сброс навигации к корню")
    
    def get_path_parts(self) -> List[str]:
        """
        Возвращает части пути (без корня).
        
        Returns:
            List[str]: Список имен узлов от корня до текущего
        """
        return [node.name for node in self.stack[1:]]  # Пропускаем корень
    
    def get_path_string(self, separator: str = ".") -> str:
        """
        Возвращает путь в виде строки.
        
        Args:
            separator: Разделитель между частями пути
        
        Returns:
            str: Путь в виде "client.core.bus"
        """
        return separator.join(self.get_path_parts())
    
    def find_node_by_path(self, path_parts: List[str]) -> Optional[TestNode]:
        """
        Находит узел по пути от корня.
        
        Args:
            path_parts: Список частей пути ['client', 'core', 'bus']
        
        Returns:
            Optional[TestNode]: Найденный узел или None
        """
        current = self.root
        for part in path_parts:
            found = False
            for child in current.children:
                if child.name == part:
                    current = child
                    found = True
                    break
            if not found:
                return None
        return current


class FileTestsManager:
    """
    Управление тестами в текущем файле с четкой обработкой ошибок.
    Полностью независим от UI.
    """
    
    def __init__(self, discovery: TestDiscovery):
        """
        Args:
            discovery: Экземпляр TestDiscovery для загрузки тестов
        """
        self.discovery = discovery
        self.current_file_node: Optional[TestNode] = None
        self.tests_list: Optional[PaginatedList] = None
        self._last_load_result: Optional[LoadResult] = None
    
    @property
    def has_file(self) -> bool:
        """Есть ли загруженный файл"""
        return self.current_file_node is not None
    
    @property
    def has_tests(self) -> bool:
        """Есть ли тесты в текущем файле"""
        return self.tests_list is not None and len(self.tests_list.items) > 0
    
    @property
    def tests_count(self) -> int:
        """Количество тестов в текущем файле"""
        if self.tests_list:
            return len(self.tests_list.items)
        return 0
    
    @property
    def last_error(self) -> Optional[str]:
        """Последняя ошибка загрузки"""
        if self._last_load_result and self._last_load_result.error_message:
            return self._last_load_result.error_message
        return None
    
    def get_cached_node(self, path: Path) -> Optional[TestNode]:
        """
        Получает загруженный узел из кэша.
        
        Args:
            path: Путь к файлу
        
        Returns:
            Optional[TestNode]: Загруженный узел или None
        """
        return self.discovery.get_cached_node(path)
    
    def load_file(self, node: TestNode) -> LoadResult:
        """
        Загружает тесты из файла.
        
        Args:
            node: Узел файла для загрузки
        
        Returns:
            LoadResult: Результат загрузки с деталями
        
        Raises:
            FileLoadError: При критических ошибках (передается для обработки наверх)
        """
        logger.info(f"Загрузка тестов из {node.path.name}")
        
        # Сброс предыдущего состояния
        self._last_load_result = None
        
        # Проверка типа узла
        if node.node_type != "file":
            error_msg = f"Узел {node.name} не является файлом"
            logger.error(error_msg)
            result = LoadResult(
                success=False,
                error_message=error_msg
            )
            self._last_load_result = result
            return result
        
        # 1. Проверка кэша
        cached = self.get_cached_node(node.path)
        if cached is not None:
            logger.debug(f"Загружено из кэша: {node.path.name}")
            self.current_file_node = cached
            self.tests_list = PaginatedList(list(cached.tests))
            
            result = LoadResult(
                success=True,
                node=cached,
                tests_count=len(cached.tests)
            )
            self._last_load_result = result
            return result
        
        # 2. Загрузка из файла
        try:
            loaded_node, stats = self.discovery.load_tests_from_node(node)
            
            if loaded_node is None:
                error_msg = f"Не удалось загрузить {node.path.name}"
                logger.error(error_msg)
                result = LoadResult(
                    success=False,
                    error_message=error_msg
                )
                self._last_load_result = result
                return result
            
            # Обновляем состояние
            self.current_file_node = loaded_node
            self.tests_list = PaginatedList(list(loaded_node.tests))
            
            # Формируем результат
            if stats.failed > 0:
                warning_msg = f"Загружено с ошибками: {node.path.name}"
                logger.warning(warning_msg)
                result = LoadResult(
                    success=True,
                    node=loaded_node,
                    tests_count=len(loaded_node.tests),
                    error_message=warning_msg,
                    error_details=f"Загружено: {stats.loaded}, ошибок: {stats.failed}"
                )
            elif stats.empty > 0:
                warning_msg = f"Файл не содержит тестов: {node.path.name}"
                logger.warning(warning_msg)
                result = LoadResult(
                    success=True,
                    node=loaded_node,
                    tests_count=0,
                    error_message=warning_msg
                )
            else:
                logger.info(f"Успешно загружено {len(loaded_node.tests)} тестов")
                result = LoadResult(
                    success=True,
                    node=loaded_node,
                    tests_count=len(loaded_node.tests)
                )
            
            self._last_load_result = result
            return result
            
        except Exception as e:
            error_msg = f"Ошибка при загрузке {node.path.name}: {e}"
            logger.error(error_msg, exc_info=True)
            
            result = LoadResult(
                success=False,
                error_message=error_msg,
                error_details=str(e)
            )
            self._last_load_result = result
            return result
    
    def get_test_by_global_index(self, index: int) -> Optional[TestFunction]:
        """
        Возвращает тест по глобальному индексу.
        
        Args:
            index: Глобальный индекс (1-based, от 1 до общего количества тестов)
        
        Returns:
            Optional[TestFunction]: Тест или None
        """
        if not self.tests_list:
            return None
        return self.tests_list.get_by_global_index(index)
    
    def get_test_by_local_index(self, index: int) -> Optional[TestFunction]:
        """
        Возвращает тест по локальному индексу на текущей странице.
        
        Args:
            index: Локальный индекс на странице (1-based)
        
        Returns:
            Optional[TestFunction]: Тест или None
        """
        if not self.tests_list:
            return None
        return self.tests_list.get_by_local_index(index)
    
    def next_page(self) -> bool:
        """
        Переход на следующую страницу тестов.
        
        Returns:
            bool: True если переход выполнен
        """
        if not self.tests_list:
            return False
        return self.tests_list.next_page()
    
    def prev_page(self) -> bool:
        """
        Переход на предыдущую страницу тестов.
        
        Returns:
            bool: True если переход выполнен
        """
        if not self.tests_list:
            return False
        return self.tests_list.prev_page()
    
    def go_to_page(self, page: int) -> bool:
        """
        Переход на указанную страницу тестов.
        
        Args:
            page: Номер страницы (0-based)
        
        Returns:
            bool: True если переход выполнен
        """
        if not self.tests_list:
            return False
        return self.tests_list.go_to_page(page)
    
    def get_display_info(self) -> dict:
        """
        Возвращает информацию для отображения в UI.
        
        Returns:
            dict: Словарь с информацией о текущем состоянии
        """
        info = {
            'has_file': self.has_file,
            'has_tests': self.has_tests,
            'tests_count': self.tests_count,
            'file_name': self.current_file_node.name if self.current_file_node else None,
        }
        
        if self.tests_list:
            info.update({
                'current_page': self.tests_list.current_page + 1,  # 1-based для UI
                'total_pages': self.tests_list.total_pages,
                'page_range': self.tests_list.get_display_range(),
                'global_start': self.tests_list.global_start_index,
                'global_end': self.tests_list.global_end_index,
            })
        
        if self._last_load_result and not self._last_load_result.success:
            info['error'] = self._last_load_result.error_message
        
        return info
    
    def clear(self):
        """Очищает текущий файл"""
        self.current_file_node = None
        self.tests_list = None
        self._last_load_result = None
        logger.debug("Файловый менеджер очищен")