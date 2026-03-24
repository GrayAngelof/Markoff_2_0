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

from typing import Optional, Dict, Any, List
from src.core import NodeType, NodeIdentifier
from src.data import (
    ComplexRepository,
    BuildingRepository,
    FloorRepository,
    RoomRepository,
    CounterpartyRepository,
    ResponsiblePersonRepository
)
from src.models import Counterparty, ResponsiblePerson
from utils.logger import get_logger

log = get_logger(__name__)


class ContextService:
    """
    Сервис для сбора контекста узла.
    
    Используется контроллерами для получения имён родителей
    и связанных данных перед отправкой в UI.
    """
    
    def __init__(
        self,
        complex_repo: ComplexRepository,
        building_repo: BuildingRepository,
        floor_repo: FloorRepository,
        room_repo: RoomRepository, 
        counterparty_repo: CounterpartyRepository,
        person_repo: ResponsiblePersonRepository
    ):
        """
        Инициализирует сервис контекста.
        
        Args:
            complex_repo: Репозиторий комплексов
            building_repo: Репозиторий корпусов
            floor_repo: Репозиторий этажей
            counterparty_repo: Репозиторий контрагентов
            person_repo: Репозиторий ответственных лиц
        """
        self._complex_repo = complex_repo
        self._building_repo = building_repo
        self._floor_repo = floor_repo
        self._room_repo = room_repo
        self._counterparty_repo = counterparty_repo
        self._person_repo = person_repo
        
        log.debug("ContextService initialized")
    
    # ===== Основной метод =====
    
    def get_context(self, node: NodeIdentifier) -> Dict[str, Any]:
        """
        Возвращает контекст для узла.
        
        Args:
            node: Идентификатор узла
            
        Returns:
            Словарь с ключами:
            - complex_name: имя комплекса (если есть)
            - building_name: имя корпуса (если есть)
            - floor_num: номер этажа (если есть)
            - owner: объект владельца (если есть)
            - responsible_persons: список ответственных лиц (если есть)
        """
        context: Dict[str, Any] = {}
        
        # Получаем всех предков через репозитории
        ancestors = self._get_ancestors(node)
        
        for anc_type, anc_id in ancestors:
            if anc_type == NodeType.COMPLEX:
                try:
                    complex_obj = self._complex_repo.get(anc_id)
                    context['complex_name'] = complex_obj.name
                except Exception as e:
                    log.warning(f"Failed to get complex {anc_id}: {e}")
                    
            elif anc_type == NodeType.BUILDING:
                try:
                    building_obj = self._building_repo.get(anc_id)
                    context['building_name'] = building_obj.name
                except Exception as e:
                    log.warning(f"Failed to get building {anc_id}: {e}")
                    
            elif anc_type == NodeType.FLOOR:
                try:
                    floor_obj = self._floor_repo.get(anc_id)
                    context['floor_num'] = floor_obj.number
                except Exception as e:
                    log.warning(f"Failed to get floor {anc_id}: {e}")
        
        return context
    
    def get_building_context(self, building_id: int) -> Dict[str, Any]:
        """
        Возвращает полный контекст для корпуса (включая владельца).
        
        Args:
            building_id: ID корпуса
            
        Returns:
            Словарь с контекстом корпуса
        """
        context = {}
        
        try:
            building = self._building_repo.get(building_id)
            
            # Добавляем имя корпуса
            context['building_name'] = building.name
            
            # Получаем комплекс
            if building.complex_id:
                try:
                    complex_obj = self._complex_repo.get(building.complex_id)
                    context['complex_name'] = complex_obj.name
                except Exception as e:
                    log.warning(f"Failed to get complex {building.complex_id}: {e}")
            
            # Получаем владельца
            if building.owner_id:
                try:
                    owner = self._counterparty_repo.get(building.owner_id)
                    context['owner'] = owner
                    
                    # Получаем ответственных лиц
                    persons = self._person_repo.get_by_counterparty(owner.id)
                    context['responsible_persons'] = persons
                    
                except Exception as e:
                    log.warning(f"Failed to get owner {building.owner_id}: {e}")
                    
        except Exception as e:
            log.error(f"Failed to get building context for {building_id}: {e}")
        
        return context
    
    def get_owner_context(self, counterparty_id: int) -> Dict[str, Any]:
        """
        Возвращает контекст владельца (контрагент + ответственные лица).
        
        Args:
            counterparty_id: ID контрагента
            
        Returns:
            Словарь с контекстом владельца
        """
        context = {}
        
        try:
            owner = self._counterparty_repo.get(counterparty_id)
            context['owner'] = owner
            
            persons = self._person_repo.get_by_counterparty(counterparty_id)
            context['responsible_persons'] = persons
            
        except Exception as e:
            log.error(f"Failed to get owner context for {counterparty_id}: {e}")
        
        return context
    
    # ===== Вспомогательные методы =====
    
    def _get_ancestors(self, node: NodeIdentifier) -> List[tuple]:
        """
        Получает всех предков узла.
        
        Args:
            node: Идентификатор узла
            
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
                    
            elif current_type == NodeType.FLOOR:
                try:
                    floor = self._floor_repo.get(current_id)
                    if floor.building_id:
                        ancestors.append((NodeType.BUILDING, floor.building_id))
                    current_type = NodeType.BUILDING
                    current_id = floor.building_id
                    continue
                except Exception:
                    break
                    
            elif current_type == NodeType.ROOM:
                try:
                    room = self._room_repo.get(current_id)  # может понадобиться
                    if room.floor_id:
                        ancestors.append((NodeType.FLOOR, room.floor_id))
                    current_type = NodeType.FLOOR
                    current_id = room.floor_id
                    continue
                except Exception:
                    break
            
            break
        
        return ancestors