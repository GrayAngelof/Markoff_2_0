# client/src/controllers/tree_controller.py
"""
Контроллер дерева объектов.
Реализует ленивую загрузку с кэшированием для всех уровней иерархии.
"""
from typing import Optional, Dict, Any

from src.core.event_bus import EventBus
from src.core.events import UIEvents, SystemEvents
from src.data.entity_types import NodeType, COMPLEX, BUILDING, FLOOR, ROOM, COUNTERPARTY
from src.data.graph.schema import get_child_type
from src.services.data_load import DataLoader
from src.data.entity_graph import EntityGraph
from src.controllers.base import BaseController

from utils.logger import get_logger


class TreeController(BaseController):
    """
    Контроллер дерева объектов.
    
    Логика:
    - При раскрытии узла → загрузить детей (ленивая загрузка)
    - При выборе узла → проверить кэш, загрузить детали если нужно
    - Детальные данные кэшируются в EntityGraph
    """
    
    def __init__(self, event_bus: EventBus, loader: DataLoader, graph: EntityGraph):
        """
        Инициализирует контроллер дерева.
        
        Args:
            event_bus: Шина событий
            loader: Загрузчик данных
            graph: Граф сущностей
        """
        super().__init__(event_bus)
        
        self._loader = loader
        self._graph = graph
        self._current_selection: Optional[tuple] = None  # (node_type, node_id)
        
        # Подписки на события UI
        self._subscribe(UIEvents.NODE_EXPANDED, self._on_node_expanded)
        self._subscribe(UIEvents.NODE_SELECTED, self._on_node_selected)
        self._subscribe(UIEvents.GET_SELECTED_NODE, self._on_get_selected_node)
        self._subscribe(UIEvents.REFRESH_REQUESTED, self._on_refresh_requested)
        
        self._logger.info("TreeController инициализирован (с поддержкой кэширования)")
    
    # ===== Обработчики событий =====
    
    def _on_node_expanded(self, event: Dict[str, Any]) -> None:
        """
        Пользователь раскрыл узел - загружаем детей при необходимости.
        Ленивая загрузка: загружаем только если детей ещё нет в графе.
        """
        node_type = event['data']['node_type']
        node_id = event['data']['node_id']
        
        self._logger.debug(f"Раскрыт узел {node_type}#{node_id}")
        
        # Определяем тип детей
        child_type = get_child_type(node_type)
        if not child_type:
            self._logger.debug(f"Тип {node_type} не может иметь детей")
            return
        
        # Проверяем, есть ли уже дети в графе (кэш)
        existing_ids = self._graph.get_children(node_type, node_id)
        
        if not existing_ids:
            # Нет детей в графе - загружаем
            self._logger.info(f"Загрузка детей для {node_type}#{node_id} (первый раскрытие)")
            children = self._loader.load_children(node_type, node_id, child_type)
            
            # Для корпусов отправляем событие о загрузке владельцев
            if child_type == BUILDING and children:
                self._notify_owners_loaded(children)
        else:
            # Дети уже есть в кэше
            self._logger.debug(f"Дети для {node_type}#{node_id} уже в кэше")
    
    def _on_node_selected(self, event: Dict[str, Any]) -> None:
        """
        Пользователь выбрал узел - загружаем детали если их нет в кэше.
        """
        # СУПЕР-ЗАМЕТНЫЙ ЛОГ
        print("\n" + "="*80)
        print("🔥🔥🔥 TREE CONTROLLER: _on_node_selected ВЫЗВАН! 🔥🔥🔥")
        print("="*80 + "\n")
        
        # ДЕТАЛЬНЫЙ ЛОГ
        self._logger.info(f"🔥🔥🔥 TREE CONTROLLER: _on_node_selected ВЫЗВАН!")
        self._logger.info(f"🔥 Тип event: {type(event)}")
        self._logger.info(f"🔥 event: {event}")
        
        # Извлекаем данные из события
        try:
            data = event['data']  # событие от EventBus имеет структуру {'data': {...}}
            node_type_obj = data['node_type']  # Это может быть NodeType или строка
            node_id = data['node_id']
            node_data = data.get('data')
            
            # Преобразуем node_type в строку если это NodeType
            if hasattr(node_type_obj, 'value'):
                node_type_str = node_type_obj.value
            else:
                node_type_str = str(node_type_obj)
            
            self._logger.info(f"🔥 _on_node_selected: тип={node_type_str}, id={node_id}")
            
            # Преобразуем строку в NodeType
            try:
                node_type = NodeType(node_type_str)
            except ValueError:
                self._logger.error(f"Неизвестный тип узла: {node_type_str}")
                return
            
            # Сохраняем текущее выделение
            self._current_selection = (node_type, node_id)
            
            # Собираем контекст для узла (имена родителей)
            context = self.get_selected_node_context(node_type, node_id)
            self._logger.info(f"🔥 context собран: {context}")
            
            # ВАЖНО: Всегда загружаем детали при выборе узла
            self._logger.info(f"🔥 ВЫЗЫВАЕМ loader.load_details для {node_type.value}#{node_id}")
            result = self._loader.load_details(node_type, node_id)
            self._logger.info(f"🔥 РЕЗУЛЬТАТ load_details: {result}")
            
            if result:
                self._bus.emit('ui.node_details_loaded', {
                'node_type': node_type.value,
                'node_id': node_id,
                'data': result,
                'context': context
            }, source='tree_controller')
            
            # Для корпусов дополнительно загружаем информацию о владельце
            if node_type == BUILDING and node_data and hasattr(node_data, 'owner_id') and node_data.owner_id:
                self._logger.info(f"🔥 Загружаем владельца для корпуса {node_id}")
                self._load_building_owner_info(node_id, node_data, context)
                
        except KeyError as e:
            self._logger.error(f"🔥 ОШИБКА: отсутствует ключ {e} в event")
            self._logger.error(f"🔥 event data: {event}")
        except Exception as e:
            self._logger.error(f"🔥 ОШИБКА в _on_node_selected: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_building_owner_info(self, building_id: int, building_data, context: Dict[str, Optional[str]]) -> None:
        """
        Загружает информацию о владельце корпуса.
        Владельцы тоже кэшируются.
        """
        if not hasattr(building_data, 'owner_id') or not building_data.owner_id:
            self._logger.debug(f"Корпус {building_id} не имеет владельца")
            return
        
        owner_id = building_data.owner_id
        self._logger.info(f"Загрузка информации о владельце {owner_id} для корпуса {building_id}")
        
        # Проверяем кэш для владельца
        cached_owner = self._graph.get(COUNTERPARTY, owner_id)
        
        if cached_owner:
            self._logger.debug(f"Владелец {owner_id} уже в кэше")
            owner = cached_owner
        else:
            # Загружаем данные о владельце
            owner = self._loader.load_counterparty(owner_id)
        
        if owner:
            # Отправляем событие с информацией о владельце
            self._bus.emit('ui.building_owner_loaded', {
                'building_id': building_id,
                'owner': owner,
                'context': context
            }, source='tree_controller')
    
    def _notify_owners_loaded(self, buildings: list) -> None:
        """
        Уведомляет о загрузке владельцев для списка корпусов.
        """
        for building in buildings:
            if hasattr(building, 'owner_id') and building.owner_id:
                self._bus.emit('ui.building_owner_loaded', {
                    'building_id': building.id,
                    'owner_id': building.owner_id
                }, source='tree_controller')
    
    def _on_refresh_requested(self, event: Dict[str, Any]) -> None:
        """Обрабатывает запросы на обновление."""
        mode = event['data'].get('mode', 'current')
        
        if mode == 'current':
            self._handle_refresh_current(event['data'])
    
    def _handle_refresh_current(self, data: Dict[str, Any]) -> None:
        """Обновление текущего узла - принудительная перезагрузка."""
        node_type = data.get('node_type')
        node_id = data.get('node_id')
        
        if not node_type or not node_id:
            self._logger.warning("Недостаточно данных для обновления текущего узла")
            return
        
        self._logger.info(f"Принудительное обновление узла {node_type}#{node_id}")
        
        # Инвалидируем в графе (помечаем как устаревшие)
        self._graph.invalidate(node_type, node_id)
        
        # Если это корпус, инвалидируем также данные владельца
        if node_type == BUILDING:
            building = self._graph.get(node_type, node_id)
            if building and hasattr(building, 'owner_id') and building.owner_id:
                self._graph.invalidate(COUNTERPARTY, building.owner_id)
        
        # Принудительная загрузка (игнорируем кэш)
        if node_type == COMPLEX:
            child_type = get_child_type(node_type)
            if child_type:
                self._loader.load_children(node_type, node_id, child_type)
        else:
            self._loader.load_details(node_type, node_id)
    
    def _on_get_selected_node(self, event: Dict[str, Any]) -> None:
        """Запрос текущего выбранного узла."""
        if self._current_selection:
            node_type, node_id = self._current_selection
            self._bus.emit(SystemEvents.CURRENT_SELECTION, {
                'node_type': node_type.value,
                'node_id': node_id
            }, source='tree_controller')
        else:
            self._logger.debug("Нет текущего выбранного узла")
    
    def get_selected_node_context(self, node_type: NodeType, node_id: int) -> Dict[str, Optional[str]]:
        """
        Собирает контекст для узла (имена родителей).
        
        Returns:
            Dict с ключами: complex_name, building_name, floor_num, owner_name
        """
        context: Dict[str, Optional[str]] = {
            'complex_name': None,
            'building_name': None,
            'floor_num': None,
            'owner_name': None,
            'complex_owner': None
        }
        
        # Собираем предков
        ancestors = self._graph.get_ancestors(node_type, node_id)
        
        for anc_type, anc_id in ancestors:
            entity = self._graph.get(anc_type, anc_id)
            if not entity:
                continue
            
            if anc_type == COMPLEX:
                context['complex_name'] = str(entity.name) if entity.name else None
                # У комплекса тоже может быть владелец
                if hasattr(entity, 'owner_id') and entity.owner_id:
                    owner = self._loader.load_counterparty(entity.owner_id)
                    if owner:
                        context['complex_owner'] = owner.short_name
                        
            elif anc_type == BUILDING:
                context['building_name'] = str(entity.name) if entity.name else None
                # У корпуса может быть владелец
                if hasattr(entity, 'owner_id') and entity.owner_id:
                    owner = self._loader.load_counterparty(entity.owner_id)
                    if owner:
                        context['owner_name'] = owner.short_name
                        
            elif anc_type == FLOOR:
                context['floor_num'] = str(entity.number) if hasattr(entity, 'number') else None
        
        self._logger.debug(f"Контекст для {node_type.value}#{node_id}: {context}")
        return context