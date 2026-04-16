# client/src/data/graph/load_state.py
"""
Отслеживание состояния загрузки данных для сущностей.

Разделяет ответственность за состояние загрузки от валидности данных.
Позволяет отслеживать:
- NOT_LOADED: дети не загружались
- LOADING: загрузка в процессе
- LOADED: дети загружены (даже если их 0)

Предотвращает гонки при параллельных запросах.
"""

# ===== ИМПОРТЫ =====
from enum import Enum, auto
from threading import RLock
from typing import Dict

from src.core.types import NodeType
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ПЕРЕЧИСЛЕНИЯ =====
class LoadState(Enum):
    """Состояние загрузки данных для сущности."""

    NOT_LOADED = auto()  # дети не загружались
    LOADING = auto()     # загрузка в процессе
    LOADED = auto()      # дети загружены (даже если пусто)


# ===== КЛАСС =====
class LoadStateIndex:
    """
    Индекс состояния загрузки данных.

    Отслеживает, загружались ли дети для каждого узла.
    Потокобезопасен через RLock.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self) -> None:
        """Инициализирует индекс состояния загрузки."""
        log.info("Инициализация LoadStateIndex")
        self._lock = RLock()

        # Состояние для каждого типа узла: {id: LoadState}
        self._states: Dict[NodeType, Dict[int, LoadState]] = {
            NodeType.COMPLEX: {},
            NodeType.BUILDING: {},
            NodeType.FLOOR: {},
            NodeType.ROOM: {},
            NodeType.COUNTERPARTY: {},
            NodeType.RESPONSIBLE_PERSON: {},
        }

        log.system(f"LoadStateIndex инициализирован: {len(self._states)} типов")

    def clear(self) -> None:
        """Полностью очищает индекс."""
        with self._lock:
            for node_type in self._states:
                self._states[node_type].clear()
            log.data("LoadStateIndex очищен")

    # ---- ПОЛУЧЕНИЕ СОСТОЯНИЯ ----
    def get_state(self, node_type: NodeType, node_id: int) -> LoadState:
        """Возвращает текущее состояние загрузки для узла."""
        with self._lock:
            return self._states[node_type].get(node_id, LoadState.NOT_LOADED)

    def is_loaded(self, node_type: NodeType, node_id: int) -> bool:
        """Проверяет, загружены ли дети."""
        with self._lock:
            return self._states[node_type].get(node_id, LoadState.NOT_LOADED) == LoadState.LOADED


    # ---- УСТАНОВКА СОСТОЯНИЯ ----
    def set_state(self, node_type: NodeType, node_id: int, state: LoadState) -> None:
        """Устанавливает состояние загрузки для узла."""
        with self._lock:
            self._states[node_type][node_id] = state
            log.debug(f"Состояние {node_type.value}#{node_id}: {state.name}")

    def mark_loading(self, node_type: NodeType, node_id: int) -> bool:
        """
        Помечает начало загрузки.

        Returns:
            True если загрузка начата, False если уже загружается или загружено
        """
        with self._lock:
            current = self._states[node_type].get(node_id, LoadState.NOT_LOADED)

            if current == LoadState.LOADING:
                log.debug(f"{node_type.value}#{node_id} уже загружается")
                return False

            if current == LoadState.LOADED:
                log.debug(f"{node_type.value}#{node_id} уже загружен")
                return False

            self._states[node_type][node_id] = LoadState.LOADING
            log.debug(f"Начало загрузки {node_type.value}#{node_id}")
            return True

    def mark_loaded(self, node_type: NodeType, node_id: int) -> None:
        """Помечает завершение загрузки (успех)."""
        with self._lock:
            self._states[node_type][node_id] = LoadState.LOADED
            log.debug(f"Завершена загрузка {node_type.value}#{node_id}")

    def mark_failed(self, node_type: NodeType, node_id: int) -> None:
        """Помечает ошибку загрузки (возвращаем в NOT_LOADED)."""
        with self._lock:
            self._states[node_type][node_id] = LoadState.NOT_LOADED
            log.debug(f"Ошибка загрузки {node_type.value}#{node_id}, сброс в NOT_LOADED")

    # ---- УПРАВЛЕНИЕ ----
    def reset(self, node_type: NodeType, node_id: int) -> None:
        """Сбрасывает состояние (при инвалидации данных)."""
        with self._lock:
            if node_id in self._states[node_type]:
                del self._states[node_type][node_id]
                log.debug(f"Сброшено состояние для {node_type.value}#{node_id}")

    def get_stats(self) -> Dict[str, int]:
        """Возвращает статистику состояний."""
        with self._lock:
            stats = {
                'not_loaded': 0,
                'loading': 0,
                'loaded': 0,
            }

            for node_type in self._states:
                for state in self._states[node_type].values():
                    if state == LoadState.NOT_LOADED:
                        stats['not_loaded'] += 1
                    elif state == LoadState.LOADING:
                        stats['loading'] += 1
                    elif state == LoadState.LOADED:
                        stats['loaded'] += 1

            return stats