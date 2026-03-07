# client/src/core/cache.py
"""
Система кэширования данных на клиенте.
Хранит загруженные данные в памяти и предоставляет методы для доступа к ним.
Поддерживает инвалидацию отдельных узлов и целых веток дерева.
"""
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
import threading

from src.utils.logger import get_logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


class DataCache:
    """
    Кэш для хранения загруженных данных.
    
    Принцип работы:
    1. Данные хранятся в словаре _data с ключами специального формата
    2. Ключ формируется по шаблону: "тип:идентификатор:суффикс"
    3. Поддерживается инвалидация (удаление) отдельных записей и целых веток
    
    Форматы ключей:
    - "complex:{id}" - данные конкретного комплекса
    - "complex:{id}:buildings" - список корпусов комплекса
    - "building:{id}:floors" - список этажей корпуса
    - "floor:{id}:rooms" - список помещений этажа
    
    Также хранит метаданные о времени загрузки и раскрытых узлах.
    """
    
    # ===== Константы типов узлов =====
    TYPE_COMPLEX = "complex"
    """Тип узла: комплекс"""
    
    TYPE_BUILDING = "building"
    """Тип узла: корпус"""
    
    TYPE_FLOOR = "floor"
    """Тип узла: этаж"""
    
    TYPE_ROOM = "room"
    """Тип узла: помещение"""
    
    # ===== Суффиксы для списков дочерних элементов =====
    SUFFIX_BUILDINGS = "buildings"
    """Суффикс для списка корпусов"""
    
    SUFFIX_FLOORS = "floors"
    """Суффикс для списка этажей"""
    
    SUFFIX_ROOMS = "rooms"
    """Суффикс для списка помещений"""
    
    def __init__(self) -> None:
        """Инициализирует пустой кэш."""
        # Основное хранилище данных
        self._data: Dict[str, Any] = {}
        
        # Метаданные: время загрузки каждого ключа
        self._timestamps: Dict[str, datetime] = {}
        
        # Множество раскрытых узлов (для быстрого доступа при обновлении видимых)
        self._expanded_nodes: Set[str] = set()
        
        # Блокировка для потокобезопасности
        self._lock = threading.RLock()
        
        # Счётчики для статистики
        self._hits: int = 0
        """Количество успешных обращений к кэшу"""
        
        self._misses: int = 0
        """Количество промахов"""
        
        self._invalidations: int = 0
        """Количество инвалидаций"""
        
        log.success("Cache: инициализирован")
    
    # ===== Приватные методы работы с ключами =====
    
    def _make_key(self, type_: str, id_: int, suffix: Optional[str] = None) -> str:
        """
        Создаёт ключ для доступа к данным в кэше.
        
        Args:
            type_: Тип узла (complex, building, floor, room)
            id_: Идентификатор узла
            suffix: Необязательный суффикс (например, "buildings")
            
        Returns:
            str: Ключ в формате "type:id:suffix" или "type:id"
        """
        if suffix:
            return f"{type_}:{id_}:{suffix}"
        return f"{type_}:{id_}"
    
    def _parse_key(self, key: str) -> Tuple[str, int, Optional[str]]:
        """
        Разбирает ключ на составляющие.
        
        Args:
            key: Ключ в формате "type:id:suffix" или "type:id"
            
        Returns:
            Tuple[str, int, Optional[str]]: (type, id, suffix)
        """
        parts = key.split(':')
        if len(parts) == 2:
            return parts[0], int(parts[1]), None
        else:
            return parts[0], int(parts[1]), parts[2]
    
    # ===== Основные методы доступа к данным =====
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получает данные из кэша по ключу.
        
        Args:
            key: Ключ данных
            
        Returns:
            Any: Данные или None, если ключ не найден
        """
        with self._lock:
            data = self._data.get(key)
            if data is not None:
                self._hits += 1
                log.cache(f"HIT: {key}")
            else:
                self._misses += 1
                log.cache(f"MISS: {key}")
            return data
    
    def set(self, key: str, value: Any) -> None:
        """
        Сохраняет данные в кэш.
        
        Args:
            key: Ключ данных
            value: Данные для сохранения
        """
        with self._lock:
            self._data[key] = value
            self._timestamps[key] = datetime.now()
            log.cache(f"SET: {key}")
    
    def has(self, key: str) -> bool:
        """
        Проверяет наличие данных в кэше.
        
        Args:
            key: Ключ данных
            
        Returns:
            bool: True если данные есть
        """
        with self._lock:
            return key in self._data
    
    def remove(self, key: str) -> bool:
        """
        Удаляет конкретную запись из кэша.
        
        Args:
            key: Ключ данных
            
        Returns:
            bool: True если запись была удалена
        """
        with self._lock:
            if key in self._data:
                del self._data[key]
                if key in self._timestamps:
                    del self._timestamps[key]
                self._invalidations += 1
                log.cache(f"REMOVE: {key}")
                return True
            return False
    
    # ===== Методы для работы с иерархическими данными =====
    
    def get_complex(self, complex_id: int) -> Optional[Any]:
        """
        Получает данные комплекса.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            Optional[Any]: Данные комплекса или None
        """
        return self.get(self._make_key(self.TYPE_COMPLEX, complex_id))
    
    def set_complex(self, complex_id: int, data: Any) -> None:
        """
        Сохраняет данные комплекса.
        
        Args:
            complex_id: ID комплекса
            data: Данные для сохранения
        """
        self.set(self._make_key(self.TYPE_COMPLEX, complex_id), data)
    
    def get_buildings(self, complex_id: int) -> Optional[Any]:
        """
        Получает список корпусов комплекса.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            Optional[Any]: Список корпусов или None
        """
        return self.get(self._make_key(self.TYPE_COMPLEX, complex_id, self.SUFFIX_BUILDINGS))
    
    def set_buildings(self, complex_id: int, buildings: Any) -> None:
        """
        Сохраняет список корпусов комплекса.
        
        Args:
            complex_id: ID комплекса
            buildings: Список корпусов для сохранения
        """
        self.set(self._make_key(self.TYPE_COMPLEX, complex_id, self.SUFFIX_BUILDINGS), buildings)
    
    def get_floors(self, building_id: int) -> Optional[Any]:
        """
        Получает список этажей корпуса.
        
        Args:
            building_id: ID корпуса
            
        Returns:
            Optional[Any]: Список этажей или None
        """
        return self.get(self._make_key(self.TYPE_BUILDING, building_id, self.SUFFIX_FLOORS))
    
    def set_floors(self, building_id: int, floors: Any) -> None:
        """
        Сохраняет список этажей корпуса.
        
        Args:
            building_id: ID корпуса
            floors: Список этажей для сохранения
        """
        self.set(self._make_key(self.TYPE_BUILDING, building_id, self.SUFFIX_FLOORS), floors)
    
    def get_rooms(self, floor_id: int) -> Optional[Any]:
        """
        Получает список помещений этажа.
        
        Args:
            floor_id: ID этажа
            
        Returns:
            Optional[Any]: Список помещений или None
        """
        return self.get(self._make_key(self.TYPE_FLOOR, floor_id, self.SUFFIX_ROOMS))
    
    def set_rooms(self, floor_id: int, rooms: Any) -> None:
        """
        Сохраняет список помещений этажа.
        
        Args:
            floor_id: ID этажа
            rooms: Список помещений для сохранения
        """
        self.set(self._make_key(self.TYPE_FLOOR, floor_id, self.SUFFIX_ROOMS), rooms)
    
    # ===== Методы инвалидации =====
    
    def invalidate_node(self, node_type: str, node_id: int) -> None:
        """
        Инвалидирует (удаляет) данные конкретного узла.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self.remove(key)
            log.info(f"Инвалидирован узел {node_type}:{node_id}")
    
    def invalidate_branch(self, node_type: str, node_id: int) -> None:
        """
        Инвалидирует ветку целиком - узел и всех его потомков.
        
        Для каждого типа узла удаляет:
        - complex: сам комплекс + его корпуса + этажи корпусов + помещения этажей
        - building: сам корпус + его этажи + помещения этажей
        - floor: сам этаж + его помещения
        - room: только само помещение (нет детей)
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            keys_to_remove = self._collect_branch_keys(node_type, node_id)
            
            # Удаляем все найденные ключи
            unique_keys = set(keys_to_remove)
            for key in unique_keys:
                self.remove(key)
            
            log.info(f"Инвалидирована ветка {node_type}:{node_id} (удалено {len(unique_keys)} записей)")
    
    def _collect_branch_keys(self, node_type: str, node_id: int) -> List[str]:
        """
        Собирает все ключи, относящиеся к ветке узла.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            List[str]: Список ключей для удаления
        """
        keys_to_remove = []
        
        if node_type == self.TYPE_COMPLEX:
            keys_to_remove.extend(self._collect_complex_branch(node_id))
        elif node_type == self.TYPE_BUILDING:
            keys_to_remove.extend(self._collect_building_branch(node_id))
        elif node_type == self.TYPE_FLOOR:
            keys_to_remove.extend(self._collect_floor_branch(node_id))
        elif node_type == self.TYPE_ROOM:
            keys_to_remove.append(self._make_key(node_type, node_id))
        
        return keys_to_remove
    
    def _collect_complex_branch(self, complex_id: int) -> List[str]:
        """
        Собирает ключи для ветки комплекса.
        
        Args:
            complex_id: ID комплекса
            
        Returns:
            List[str]: Список ключей
        """
        keys = []
        
        # Удаляем комплекс
        keys.append(self._make_key(self.TYPE_COMPLEX, complex_id))
        keys.append(self._make_key(self.TYPE_COMPLEX, complex_id, self.SUFFIX_BUILDINGS))
        
        # Ищем все корпуса этого комплекса в кэше
        prefix = f"{self.TYPE_BUILDING}:"
        for key in list(self._data.keys()):
            if key.startswith(prefix):
                try:
                    _, b_id, suffix = self._parse_key(key)
                    if suffix is None or suffix == self.SUFFIX_FLOORS:
                        keys.append(key)
                        # Для каждого корпуса удаляем его этажи
                        floors_key = self._make_key(self.TYPE_BUILDING, b_id, self.SUFFIX_FLOORS)
                        if floors_key in self._data:
                            keys.append(floors_key)
                except (ValueError, IndexError):
                    continue
        
        return keys
    
    def _collect_building_branch(self, building_id: int) -> List[str]:
        """
        Собирает ключи для ветки корпуса.
        
        Args:
            building_id: ID корпуса
            
        Returns:
            List[str]: Список ключей
        """
        keys = []
        
        # Удаляем корпус
        keys.append(self._make_key(self.TYPE_BUILDING, building_id))
        keys.append(self._make_key(self.TYPE_BUILDING, building_id, self.SUFFIX_FLOORS))
        
        # Ищем все этажи этого корпуса в кэше
        prefix = f"{self.TYPE_FLOOR}:"
        for key in list(self._data.keys()):
            if key.startswith(prefix):
                try:
                    _, f_id, suffix = self._parse_key(key)
                    if suffix is None or suffix == self.SUFFIX_ROOMS:
                        keys.append(key)
                        # Для каждого этажа удаляем его помещения
                        rooms_key = self._make_key(self.TYPE_FLOOR, f_id, self.SUFFIX_ROOMS)
                        if rooms_key in self._data:
                            keys.append(rooms_key)
                except (ValueError, IndexError):
                    continue
        
        return keys
    
    def _collect_floor_branch(self, floor_id: int) -> List[str]:
        """
        Собирает ключи для ветки этажа.
        
        Args:
            floor_id: ID этажа
            
        Returns:
            List[str]: Список ключей
        """
        keys = []
        
        # Удаляем этаж
        keys.append(self._make_key(self.TYPE_FLOOR, floor_id))
        keys.append(self._make_key(self.TYPE_FLOOR, floor_id, self.SUFFIX_ROOMS))
        
        # Удаляем сами помещения (они не имеют детей)
        prefix = f"{self.TYPE_ROOM}:"
        for key in list(self._data.keys()):
            if key.startswith(prefix):
                try:
                    _, r_id, suffix = self._parse_key(key)
                    if suffix is None:  # само помещение
                        keys.append(key)
                except (ValueError, IndexError):
                    continue
        
        return keys
    
    def invalidate_visible(self, expanded_nodes: List[Tuple[str, int]]) -> None:
        """
        Инвалидирует все раскрытые узлы (для обновления видимых).
        
        Args:
            expanded_nodes: Список кортежей (тип_узла, id_узла) раскрытых узлов
        """
        with self._lock:
            count = 0
            for node_type, node_id in expanded_nodes:
                self.invalidate_branch(node_type, node_id)
                count += 1
            
            log.info(f"Инвалидировано {count} раскрытых узлов")
    
    def clear(self) -> None:
        """Полностью очищает кэш."""
        with self._lock:
            self._data.clear()
            self._timestamps.clear()
            self._expanded_nodes.clear()
            self._hits = 0
            self._misses = 0
            self._invalidations += 1
            log.info("Cache: полная очистка")
    
    # ===== Методы для работы с раскрытыми узлами =====
    
    def mark_expanded(self, node_type: str, node_id: int) -> None:
        """
        Отмечает узел как раскрытый.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self._expanded_nodes.add(key)
            log.debug(f"Узел отмечен как раскрытый: {key}")
    
    def mark_collapsed(self, node_type: str, node_id: int) -> None:
        """
        Отмечает узел как свёрнутый.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self._expanded_nodes.discard(key)
            log.debug(f"Узел отмечен как свёрнутый: {key}")
    
    def get_expanded_nodes(self) -> List[Tuple[str, int]]:
        """
        Получает список всех раскрытых узлов.
        
        Returns:
            List[Tuple[str, int]]: Список кортежей (тип_узла, id_узла)
        """
        with self._lock:
            result = []
            for key in self._expanded_nodes:
                try:
                    type_, id_, _ = self._parse_key(key)
                    result.append((type_, id_))
                except (ValueError, IndexError):
                    continue
            return result
    
    def is_expanded(self, node_type: str, node_id: int) -> bool:
        """
        Проверяет, раскрыт ли узел.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            
        Returns:
            bool: True если узел раскрыт
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            return key in self._expanded_nodes
    
    # ===== Методы для точечной инвалидации =====
    
    def remove_children_cache(self, node_type: str, node_id: int) -> None:
        """
        Удаляет только кэш дочерних элементов, сохраняя сам узел.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        with self._lock:
            key = None
            if node_type == self.TYPE_COMPLEX:
                key = self._make_key(node_type, node_id, self.SUFFIX_BUILDINGS)
            elif node_type == self.TYPE_BUILDING:
                key = self._make_key(node_type, node_id, self.SUFFIX_FLOORS)
            elif node_type == self.TYPE_FLOOR:
                key = self._make_key(node_type, node_id, self.SUFFIX_ROOMS)
            
            if key and key in self._data:
                del self._data[key]
                if key in self._timestamps:
                    del self._timestamps[key]
                log.cache(f"Удалены дети {node_type}:{node_id}")
    
    # ===== Методы для статистики и отладки =====
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получает статистику использования кэша.
        
        Returns:
            Dict[str, Any]: Словарь со статистикой
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._data),
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f"{hit_rate:.1f}%",
                'invalidations': self._invalidations,
                'expanded_nodes': len(self._expanded_nodes),
                'keys': list(self._data.keys())
            }
    
    def print_stats(self) -> None:
        """Выводит статистику в консоль."""
        stats = self.get_stats()
        log.info("\n=== Cache Statistics ===")
        log.info(f"📦 Записей в кэше: {stats['size']}")
        log.info(f"🎯 Попаданий: {stats['hits']}")
        log.info(f"❌ Промахов: {stats['misses']}")
        log.info(f"📊 Hit rate: {stats['hit_rate']}")
        log.info(f"🔄 Инвалидаций: {stats['invalidations']}")
        log.info(f"🔍 Раскрытых узлов: {stats['expanded_nodes']}")
        log.info("=" * 30)