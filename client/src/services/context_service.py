# client/src/services/context_service.py
"""
ContextService — сбор контекста для UI.

Отвечает за:
- Получение имён родителей для узла
- Загрузку связанных данных (владельцы, контакты)
- Формирование готового словаря для отображения

НЕ отвечает за:
- Бизнес-логику (это контроллеры)
- Хранение данных (это EntityGraph)
- Загрузку данных (это DataLoader)
"""

# ===== ИМПОРТЫ =====
from typing import Any, Dict, List, Optional, Tuple

from src.core import NodeIdentifier, NodeType
from src.data import (
    BuildingRepository,
    ComplexRepository,
    FloorRepository,
    RoomRepository,
)
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class ContextService:
    """
    Сервис для сбора контекста узла.

    Используется контроллерами для получения имён родителей
    и связанных данных перед отправкой в UI.
    """

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(
        self,
        complex_repo: ComplexRepository,
        building_repo: BuildingRepository,
        floor_repo: FloorRepository,
        room_repo: RoomRepository,
    ) -> None:
        """Инициализирует сервис контекста."""
        log.info("Инициализация ContextService")
        self._complex_repo = complex_repo
        self._building_repo = building_repo
        self._floor_repo = floor_repo
        self._room_repo = room_repo

        log.system("ContextService инициализирован")

    # ---- ПУБЛИЧНОЕ API ----
    def get_context(self, node: NodeIdentifier) -> Dict[str, Any]:
        """
        Возвращает контекст для узла.

        Returns:
            Словарь с ключами:
            - complex_name: имя комплекса (если есть)
            - building_name: имя корпуса (если есть)
            - floor_num: номер этажа (если есть)
            - owner: объект владельца (если есть)
            - responsible_persons: список ответственных лиц (если есть)
        """
        context: Dict[str, Any] = {}

        ancestors = self._get_ancestors(node)

        for anc_type, anc_id in ancestors:
            if anc_type == NodeType.COMPLEX:
                try:
                    complex_obj = self._complex_repo.get(anc_id)
                    context['complex_name'] = complex_obj.name
                except Exception as e:
                    log.warning(f"Не удалось получить комплекс {anc_id}: {e}")

            elif anc_type == NodeType.BUILDING:
                try:
                    building_obj = self._building_repo.get(anc_id)
                    context['building_name'] = building_obj.name
                except Exception as e:
                    log.warning(f"Не удалось получить корпус {anc_id}: {e}")

            elif anc_type == NodeType.FLOOR:
                try:
                    floor_obj = self._floor_repo.get(anc_id)
                    context['floor_num'] = floor_obj.number
                except Exception as e:
                    log.warning(f"Не удалось получить этаж {anc_id}: {e}")

        return context

    def get_building_context(self, building_id: int) -> Dict[str, Any]:
        """
        Возвращает полный контекст для корпуса.

        Returns:
            Словарь с контекстом корпуса
        """
        context = {}

        try:
            building = self._building_repo.get(building_id)

            context['building_name'] = building.name

            if building.complex_id:
                try:
                    complex_obj = self._complex_repo.get(building.complex_id)
                    context['complex_name'] = complex_obj.name
                except Exception as e:
                    log.warning(f"Не удалось получить комплекс {building.complex_id}: {e}")
        except Exception as e:
            log.error(f"Не удалось получить контекст корпуса {building_id}: {e}")

        return context


    # ---- ВНУТРЕННИЕ МЕТОДЫ ----
    def _get_ancestors(self, node: NodeIdentifier) -> List[Tuple[NodeType, int]]:
        """
        Получает всех предков узла.

        Returns:
            Список кортежей (тип, ID) в порядке от ближайшего к дальнему
        """
        ancestors = []
        current_type = node.node_type
        current_id = node.node_id

        while True:
            if current_type == NodeType.BUILDING:
                try:
                    building = self._building_repo.get(current_id)
                    if building.complex_id:
                        ancestors.append((NodeType.COMPLEX, building.complex_id))
                    current_type = NodeType.COMPLEX
                    current_id = building.complex_id
                    continue
                except Exception:
                    break

            if current_type == NodeType.FLOOR:
                try:
                    floor = self._floor_repo.get(current_id)
                    if floor.building_id:
                        ancestors.append((NodeType.BUILDING, floor.building_id))
                    current_type = NodeType.BUILDING
                    current_id = floor.building_id
                    continue
                except Exception:
                    break

            if current_type == NodeType.ROOM:
                try:
                    room = self._room_repo.get(current_id)
                    if room.floor_id:
                        ancestors.append((NodeType.FLOOR, room.floor_id))
                    current_type = NodeType.FLOOR
                    current_id = room.floor_id
                    continue
                except Exception:
                    break

            break

        return ancestors