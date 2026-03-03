# client/src/core/cache.py
"""
Система кэширования данных на клиенте
Хранит загруженные данные в памяти и предоставляет методы для доступа к ним
Поддерживает инвалидацию отдельных узлов и целых веток дерева
"""
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import threading


class DataCache:
    """
    Кэш для хранения загруженных данных
    
    Принцип работы:
    1. Данные хранятся в словаре _data с ключами специального формата
    2. Ключ формируется по шаблону: "тип:идентификатор:суффикс"
    3. Поддерживается инвалидация (удаление) отдельных записей и целых веток
    
    Форматы ключей:
    - "complex:{id}" - данные конкретного комплекса
    - "complex:{id}:buildings" - список корпусов комплекса
    - "building:{id}:floors" - список этажей корпуса
    - "floor:{id}:rooms" - список помещений этажа
    
    Также храним метаданные о времени загрузки и раскрытых узлах
    """
    
    # Константы для типов узлов
    TYPE_COMPLEX = "complex"
    TYPE_BUILDING = "building"
    TYPE_FLOOR = "floor"
    TYPE_ROOM = "room"
    
    # Суффиксы для списков дочерних элементов
    SUFFIX_BUILDINGS = "buildings"
    SUFFIX_FLOORS = "floors"
    SUFFIX_ROOMS = "rooms"
    
    def __init__(self):
        """Инициализация пустого кэша"""
        # Основное хранилище данных
        self._data: Dict[str, Any] = {}
        
        # Метаданные: время загрузки каждого ключа
        self._timestamps: Dict[str, datetime] = {}
        
        # Множество раскрытых узлов (для быстрого доступа при обновлении видимых)
        self._expanded_nodes: Set[str] = set()
        
        # Блокировка для потокобезопасности (на случай многопоточности в будущем)
        self._lock = threading.RLock()
        
        # Счётчики для статистики
        self._hits = 0  # количество успешных обращений к кэшу
        self._misses = 0  # количество промахов
        self._invalidations = 0  # количество инвалидаций
        
        print("✅ Cache: инициализирован")
    
    # ===== Базовые методы работы с ключами =====
    
    def _make_key(self, type_: str, id_: int, suffix: Optional[str] = None) -> str:
        """
        Создаёт ключ для доступа к данным в кэше
        
        Args:
            type_: тип узла (complex, building, floor, room)
            id_: идентификатор узла
            suffix: необязательный суффикс (например, "buildings")
            
        Returns:
            str: ключ в формате "type:id:suffix" или "type:id"
        """
        if suffix:
            return f"{type_}:{id_}:{suffix}"
        return f"{type_}:{id_}"
    
    def _parse_key(self, key: str) -> tuple:
        """
        Разбирает ключ на составляющие
        
        Args:
            key: ключ в формате "type:id:suffix" или "type:id"
            
        Returns:
            tuple: (type, id, suffix) где suffix может быть None
        """
        parts = key.split(':')
        if len(parts) == 2:
            return parts[0], int(parts[1]), None
        else:
            return parts[0], int(parts[1]), parts[2]
    
    # ===== Основные методы доступа к данным =====
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получить данные из кэша по ключу
        
        Args:
            key: ключ данных
            
        Returns:
            Any: данные или None, если ключ не найден
        """
        with self._lock:
            data = self._data.get(key)
            if data is not None:
                self._hits += 1
                # print(f"✅ Cache HIT: {key}")  # Раскомментировать для отладки
            else:
                self._misses += 1
                # print(f"❌ Cache MISS: {key}")  # Раскомментировать для отладки
            return data
    
    def set(self, key: str, value: Any) -> None:
        """
        Сохранить данные в кэш
        
        Args:
            key: ключ данных
            value: данные для сохранения
        """
        with self._lock:
            self._data[key] = value
            self._timestamps[key] = datetime.now()
            # print(f"💾 Cache SET: {key}")  # Раскомментировать для отладки
    
    def has(self, key: str) -> bool:
        """
        Проверить наличие данных в кэше
        
        Args:
            key: ключ данных
            
        Returns:
            bool: True если данные есть
        """
        with self._lock:
            return key in self._data
    
    def remove(self, key: str) -> bool:
        """
        Удалить конкретную запись из кэша
        
        Args:
            key: ключ данных
            
        Returns:
            bool: True если запись была удалена
        """
        with self._lock:
            if key in self._data:
                del self._data[key]
                if key in self._timestamps:
                    del self._timestamps[key]
                self._invalidations += 1
                # print(f"🗑️ Cache REMOVE: {key}")  # Раскомментировать для отладки
                return True
            return False
    
    # ===== Методы для работы с иерархическими данными =====
    
    def get_complex(self, complex_id: int) -> Optional[Any]:
        """Получить данные комплекса"""
        return self.get(self._make_key(self.TYPE_COMPLEX, complex_id))
    
    def set_complex(self, complex_id: int, data: Any) -> None:
        """Сохранить данные комплекса"""
        self.set(self._make_key(self.TYPE_COMPLEX, complex_id), data)
    
    def get_buildings(self, complex_id: int) -> Optional[Any]:
        """Получить список корпусов комплекса"""
        return self.get(self._make_key(self.TYPE_COMPLEX, complex_id, self.SUFFIX_BUILDINGS))
    
    def set_buildings(self, complex_id: int, buildings: Any) -> None:
        """Сохранить список корпусов комплекса"""
        self.set(self._make_key(self.TYPE_COMPLEX, complex_id, self.SUFFIX_BUILDINGS), buildings)
    
    def get_floors(self, building_id: int) -> Optional[Any]:
        """Получить список этажей корпуса"""
        return self.get(self._make_key(self.TYPE_BUILDING, building_id, self.SUFFIX_FLOORS))
    
    def set_floors(self, building_id: int, floors: Any) -> None:
        """Сохранить список этажей корпуса"""
        self.set(self._make_key(self.TYPE_BUILDING, building_id, self.SUFFIX_FLOORS), floors)
    
    def get_rooms(self, floor_id: int) -> Optional[Any]:
        """Получить список помещений этажа"""
        return self.get(self._make_key(self.TYPE_FLOOR, floor_id, self.SUFFIX_ROOMS))
    
    def set_rooms(self, floor_id: int, rooms: Any) -> None:
        """Сохранить список помещений этажа"""
        self.set(self._make_key(self.TYPE_FLOOR, floor_id, self.SUFFIX_ROOMS), rooms)
    
    # ===== Методы инвалидации =====
    
    def invalidate_node(self, node_type: str, node_id: int) -> None:
        """
        Инвалидировать (удалить) данные конкретного узла
        
        Args:
            node_type: тип узла
            node_id: идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self.remove(key)
            print(f"🔄 Cache: инвалидирован узел {node_type}:{node_id}")
    
    def invalidate_branch(self, node_type: str, node_id: int) -> None:
        """
        Инвалидировать ветку целиком - узел и всех его потомков
        
        Для каждого типа узла удаляем:
        - complex: сам комплекс + его корпуса + этажи корпусов + помещения этажей
        - building: сам корпус + его этажи + помещения этажей
        - floor: сам этаж + его помещения
        - room: только само помещение (нет детей)
        
        Args:
            node_type: тип узла
            node_id: идентификатор узла
        """
        with self._lock:
            # Находим все ключи, которые нужно удалить
            keys_to_remove = []
            
            if node_type == self.TYPE_COMPLEX:
                # Удаляем комплекс
                keys_to_remove.append(self._make_key(node_type, node_id))
                # Удаляем список его корпусов
                keys_to_remove.append(self._make_key(node_type, node_id, self.SUFFIX_BUILDINGS))
                
                # Ищем все корпуса этого комплекса в кэше
                prefix = f"{self.TYPE_BUILDING}:"
                for key in list(self._data.keys()):
                    if key.startswith(prefix):
                        # Получаем ID корпуса из ключа
                        try:
                            _, b_id, suffix = self._parse_key(key)
                            # Проверяем, что корпус принадлежит этому комплексу
                            # Для этого нужно знать complex_id корпуса, но у нас его нет в ключе
                            # Поэтому удаляем все корпуса, которые могли быть от этого комплекса
                            # Это безопасно, так как мы не перемешиваем данные разных комплексов
                            if suffix is None or suffix == self.SUFFIX_FLOORS:
                                keys_to_remove.append(key)
                                # Для каждого корпуса удаляем его этажи
                                floors_key = self._make_key(self.TYPE_BUILDING, b_id, self.SUFFIX_FLOORS)
                                if floors_key in self._data:
                                    keys_to_remove.append(floors_key)
                        except:
                            continue
            
            elif node_type == self.TYPE_BUILDING:
                # Удаляем корпус
                keys_to_remove.append(self._make_key(node_type, node_id))
                # Удаляем список его этажей
                keys_to_remove.append(self._make_key(node_type, node_id, self.SUFFIX_FLOORS))
                
                # Ищем все этажи этого корпуса в кэше
                prefix = f"{self.TYPE_FLOOR}:"
                for key in list(self._data.keys()):
                    if key.startswith(prefix):
                        try:
                            _, f_id, suffix = self._parse_key(key)
                            if suffix is None or suffix == self.SUFFIX_ROOMS:
                                keys_to_remove.append(key)
                                # Для каждого этажа удаляем его помещения
                                rooms_key = self._make_key(self.TYPE_FLOOR, f_id, self.SUFFIX_ROOMS)
                                if rooms_key in self._data:
                                    keys_to_remove.append(rooms_key)
                        except:
                            continue
            
            elif node_type == self.TYPE_FLOOR:
                # Удаляем этаж
                keys_to_remove.append(self._make_key(node_type, node_id))
                # Удаляем список его помещений
                keys_to_remove.append(self._make_key(node_type, node_id, self.SUFFIX_ROOMS))
                
                # Удаляем сами помещения (они не имеют детей)
                prefix = f"{self.TYPE_ROOM}:"
                for key in list(self._data.keys()):
                    if key.startswith(prefix):
                        try:
                            _, r_id, suffix = self._parse_key(key)
                            if suffix is None:  # само помещение
                                # Здесь сложно определить, какому этажу принадлежит помещение
                                # Поэтому удаляем все помещения - это безопасно
                                keys_to_remove.append(key)
                        except:
                            continue
            
            elif node_type == self.TYPE_ROOM:
                # Удаляем только само помещение
                keys_to_remove.append(self._make_key(node_type, node_id))
            
            # Удаляем все найденные ключи
            unique_keys = set(keys_to_remove)
            for key in unique_keys:
                self.remove(key)
            
            print(f"🔄 Cache: инвалидирована ветка {node_type}:{node_id} (удалено {len(unique_keys)} записей)")
    
    def invalidate_visible(self, expanded_nodes: List[tuple]) -> None:
        """
        Инвалидировать все раскрытые узлы (для обновления видимых)
        
        Args:
            expanded_nodes: список кортежей (тип_узла, id_узла) раскрытых узлов
        """
        with self._lock:
            count = 0
            for node_type, node_id in expanded_nodes:
                # Для раскрытых узлов инвалидируем всю ветку
                self.invalidate_branch(node_type, node_id)
                count += 1
            
            print(f"🔄 Cache: инвалидировано {count} раскрытых узлов")
    
    def clear(self) -> None:
        """Полностью очистить кэш"""
        with self._lock:
            self._data.clear()
            self._timestamps.clear()
            self._expanded_nodes.clear()
            self._hits = 0
            self._misses = 0
            self._invalidations += 1
            print("🧹 Cache: полная очистка")
    
    # ===== Методы для работы с раскрытыми узлами =====
    
    def mark_expanded(self, node_type: str, node_id: int) -> None:
        """
        Отметить узел как раскрытый
        
        Args:
            node_type: тип узла
            node_id: идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self._expanded_nodes.add(key)
    
    def mark_collapsed(self, node_type: str, node_id: int) -> None:
        """
        Отметить узел как свёрнутый
        
        Args:
            node_type: тип узла
            node_id: идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            self._expanded_nodes.discard(key)
    
    def get_expanded_nodes(self) -> List[tuple]:
        """
        Получить список всех раскрытых узлов
        
        Returns:
            List[tuple]: список кортежей (тип_узла, id_узла)
        """
        with self._lock:
            result = []
            for key in self._expanded_nodes:
                try:
                    type_, id_, _ = self._parse_key(key)
                    result.append((type_, id_))
                except:
                    continue
            return result
    
    def is_expanded(self, node_type: str, node_id: int) -> bool:
        """
        Проверить, раскрыт ли узел
        
        Args:
            node_type: тип узла
            node_id: идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            return key in self._expanded_nodes
    
    # ===== Методы для статистики и отладки =====
    
    def get_stats(self) -> dict:
        """
        Получить статистику использования кэша
        
        Returns:
            dict: словарь со статистикой
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
                'keys': list(self._data.keys())  # для отладки
            }
    
    def print_stats(self) -> None:
        """Вывести статистику в консоль"""
        stats = self.get_stats()
        print("\n=== Cache Statistics ===")
        print(f"📦 Записей в кэше: {stats['size']}")
        print(f"🎯 Попаданий: {stats['hits']}")
        print(f"❌ Промахов: {stats['misses']}")
        print(f"📊 Hit rate: {stats['hit_rate']}")
        print(f"🔄 Инвалидаций: {stats['invalidations']}")
        print(f"🔍 Раскрытых узлов: {stats['expanded_nodes']}")
        print("=======================\n")

    def is_expanded(self, node_type: str, node_id: int) -> bool:
        """
        Проверить, раскрыт ли узел
        
        Args:
            node_type: тип узла
            node_id: идентификатор узла
        """
        with self._lock:
            key = self._make_key(node_type, node_id)
            return key in self._expanded_nodes