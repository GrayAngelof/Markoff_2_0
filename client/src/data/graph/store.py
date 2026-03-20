# client/src/data/graph/store.py
"""
Хранилище сущностей — только хранение, никакой логики связей.

Это второй по базовости компонент Data слоя (после schema.py).
Store отвечает только за одну вещь: положить объект по ключу (тип+ID)
и достать его обратно. Никаких связей, никакой валидности, никакой бизнес-логики.

Принципы:
    - Каждая сущность хранится ровно один раз
    - Доступ O(1) через словарь
    - Потокобезопасность через RLock
    - Сохранение временных меток для отслеживания актуальности

Зависимости:
    - threading — для RLock
    - datetime — для временных меток
    - core.types.NodeType — типы узлов
    - utils.logger — логирование

Потребители:
    - entity_graph.py (фасад) — через публичные методы
    - Никто не должен импортировать store напрямую!

ВАЖНО:
    Store не знает о существовании моделей. Он работает с Any.
    Валидация типов — ответственность вызывающего кода.
"""

from threading import RLock
from datetime import datetime
from typing import Dict, Optional, Any, List, Final

from core.types import NodeType
from utils.logger import get_logger


# ============================================
# КОНСТАНТЫ
# ============================================

# Единый логгер для модуля (один экземпляр на весь store)
log = get_logger(__name__)

# Все типы, которые могут храниться в графе
# Final защищает от случайного изменения
_STORED_TYPES: Final[list[NodeType]] = [
    NodeType.COMPLEX,
    NodeType.BUILDING,
    NodeType.FLOOR,
    NodeType.ROOM,
    NodeType.COUNTERPARTY,
    NodeType.RESPONSIBLE_PERSON,
]

# Сообщения для логирования
_LOG_PUT = "💾 PUT: {type}#{id}"
_LOG_GET_HIT = "📖 GET HIT: {type}#{id}"
_LOG_GET_MISS = "📖 GET MISS: {type}#{id}"
_LOG_REMOVE = "🗑️ REMOVE: {type}#{id}"
_LOG_CLEAR = "🧹 Store очищен: {count} типов"


# ============================================
# ИНИЦИАЛИЗАЦИЯ ХРАНИЛИЩ
# ============================================

def _create_empty_stores() -> Dict[NodeType, Dict[int, Any]]:
    """
    Создаёт словарь пустых хранилищ для всех типов.
    
    Returns:
        Dict[NodeType, Dict[int, Any]]: Словарь {тип: {id: объект}}
    """
    return {node_type: {} for node_type in _STORED_TYPES}


def _create_empty_timestamps() -> Dict[NodeType, Dict[int, datetime]]:
    """
    Создаёт словарь пустых хранилищ временных меток.
    
    Returns:
        Dict[NodeType, Dict[int, datetime]]: Словарь {тип: {id: datetime}}
    """
    return {node_type: {} for node_type in _STORED_TYPES}


# ============================================
# КЛАСС STORE
# ============================================

class EntityStore:
    """
    Потокобезопасное хранилище сущностей.
    
    Единственная ответственность: хранить объекты и выдавать их по запросу.
    Никакой логики связей, валидации или бизнес-правил.
    
    Особенности:
        - Все операции защищены RLock для многопоточности
        - Временные метки для каждого объекта (когда был добавлен/обновлён)
        - Полная типизация входных/выходных данных
    
    Пример:
        >>> store = EntityStore()
        >>> store.put(NodeType.COMPLEX, 42, complex_obj)
        >>> result = store.get(NodeType.COMPLEX, 42)
        >>> assert result is complex_obj
    """
    
    def __init__(self) -> None:
        """Инициализирует пустое хранилище."""
        self._lock = RLock()
        self._entities: Dict[NodeType, Dict[int, Any]] = _create_empty_stores()
        self._timestamps: Dict[NodeType, Dict[int, datetime]] = _create_empty_timestamps()
        
        log.success(f"EntityStore инициализирован: {len(_STORED_TYPES)} типов")
    
    # ============================================
    # ОСНОВНЫЕ ОПЕРАЦИИ
    # ============================================
    
    def put(self, node_type: NodeType, entity_id: int, entity: Any) -> None:
        """
        Сохраняет сущность в хранилище.
        
        Args:
            node_type: Тип сущности (должен быть в _STORED_TYPES)
            entity_id: Уникальный идентификатор сущности
            entity: Объект для сохранения
            
        Raises:
            KeyError: Если node_type не поддерживается
            
        Note:
            Если сущность с таким ID уже существует, она будет перезаписана.
            Временная метка обновится на текущее время.
        """
        with self._lock:
            # Проверяем, что тип поддерживается
            if node_type not in self._entities:
                log.error(f"❌ PUT: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            # Сохраняем объект
            self._entities[node_type][entity_id] = entity
            self._timestamps[node_type][entity_id] = datetime.now()
            
            log.cache(_LOG_PUT.format(type=node_type.value, id=entity_id))
    
    def get(self, node_type: NodeType, entity_id: int) -> Optional[Any]:
        """
        Получает сущность из хранилища.
        
        Args:
            node_type: Тип сущности
            entity_id: Идентификатор сущности
            
        Returns:
            Optional[Any]: Объект или None, если не найден
            
        Raises:
            KeyError: Если node_type не поддерживается
        """
        with self._lock:
            if node_type not in self._entities:
                log.error(f"❌ GET: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            entity = self._entities[node_type].get(entity_id)
            
            if entity is not None:
                log.cache(_LOG_GET_HIT.format(type=node_type.value, id=entity_id))
            else:
                log.cache(_LOG_GET_MISS.format(type=node_type.value, id=entity_id))
            
            return entity
    
    def get_all(self, node_type: NodeType) -> List[Any]:
        """
        Возвращает все сущности указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            List[Any]: Список всех объектов данного типа (порядок не гарантирован)
            
        Raises:
            KeyError: Если node_type не поддерживается
        """
        with self._lock:
            if node_type not in self._entities:
                log.error(f"❌ GET_ALL: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            return list(self._entities[node_type].values())
    
    def get_all_ids(self, node_type: NodeType) -> List[int]:
        """
        Возвращает все ID сущностей указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            List[int]: Список всех ID данного типа
            
        Raises:
            KeyError: Если node_type не поддерживается
        """
        with self._lock:
            if node_type not in self._entities:
                log.error(f"❌ GET_ALL_IDS: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            return list(self._entities[node_type].keys())
    
    def remove(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Удаляет сущность из хранилища.
        
        Args:
            node_type: Тип сущности
            entity_id: Идентификатор сущности
            
        Returns:
            bool: True если сущность была удалена, False если не существовала
            
        Raises:
            KeyError: Если node_type не поддерживается
        """
        with self._lock:
            if node_type not in self._entities:
                log.error(f"❌ REMOVE: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            if entity_id in self._entities[node_type]:
                del self._entities[node_type][entity_id]
                if entity_id in self._timestamps[node_type]:
                    del self._timestamps[node_type][entity_id]
                
                log.cache(_LOG_REMOVE.format(type=node_type.value, id=entity_id))
                return True
            
            return False
    
    def has(self, node_type: NodeType, entity_id: int) -> bool:
        """
        Проверяет наличие сущности в хранилище.
        
        Args:
            node_type: Тип сущности
            entity_id: Идентификатор сущности
            
        Returns:
            bool: True если сущность существует
            
        Raises:
            KeyError: Если node_type не поддерживается
        """
        with self._lock:
            if node_type not in self._entities:
                log.error(f"❌ HAS: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            return entity_id in self._entities[node_type]
    
    def get_timestamp(self, node_type: NodeType, entity_id: int) -> Optional[datetime]:
        """
        Возвращает временную метку последнего обновления сущности.
        
        Args:
            node_type: Тип сущности
            entity_id: Идентификатор сущности
            
        Returns:
            Optional[datetime]: Время последнего put или None, если сущность не найдена
            
        Raises:
            KeyError: Если node_type не поддерживается
        """
        with self._lock:
            if node_type not in self._timestamps:
                log.error(f"❌ GET_TIMESTAMP: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            return self._timestamps[node_type].get(entity_id)
    
    # ============================================
    # ОПЕРАЦИИ УПРАВЛЕНИЯ
    # ============================================
    
    def clear(self) -> None:
        """Полностью очищает хранилище (все типы, все объекты)."""
        with self._lock:
            for node_type in self._entities:
                self._entities[node_type].clear()
                self._timestamps[node_type].clear()
            
            log.cache(_LOG_CLEAR.format(count=len(self._entities)))
    
    def size(self) -> int:
        """
        Возвращает общее количество сущностей во всех хранилищах.
        
        Returns:
            int: Сумма объектов всех типов
        """
        with self._lock:
            total = 0
            for store in self._entities.values():
                total += len(store)
            return total
    
    def size_by_type(self, node_type: NodeType) -> int:
        """
        Возвращает количество сущностей указанного типа.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            int: Количество объектов данного типа
            
        Raises:
            KeyError: Если node_type не поддерживается
        """
        with self._lock:
            if node_type not in self._entities:
                log.error(f"❌ SIZE_BY_TYPE: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            return len(self._entities[node_type])
    
    def get_all_timestamps(self, node_type: NodeType) -> Dict[int, datetime]:
        """
        Возвращает все временные метки для указанного типа.
        
        Используется для отладки и мониторинга.
        
        Args:
            node_type: Тип сущности
            
        Returns:
            Dict[int, datetime]: Словарь {id: timestamp}
        """
        with self._lock:
            if node_type not in self._timestamps:
                log.error(f"❌ GET_ALL_TIMESTAMPS: неподдерживаемый тип {node_type}")
                raise KeyError(f"Тип {node_type} не поддерживается хранилищем")
            
            return self._timestamps[node_type].copy()