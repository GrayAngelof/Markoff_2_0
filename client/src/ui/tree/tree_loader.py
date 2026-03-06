# client/src/ui/tree/tree_loader.py
"""
Модуль для загрузки данных дерева.
Содержит логику загрузки иерархических данных:
- Загрузка комплексов (корневые узлы)
- Загрузка дочерних элементов при раскрытии узла
- Загрузка детальных данных при выборе узла
- Работа с кэшированием данных
"""
from PySide6.QtCore import QModelIndex, Slot, QTimer
from typing import Optional, Dict, Any, Callable, Union

from src.ui.tree_model import NodeType
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeLoaderMixin:
    """
    Миксин для загрузки данных дерева.
    
    Предоставляет методы для загрузки данных на разных уровнях:
    - Загрузка корневых комплексов
    - Загрузка дочерних элементов (корпуса, этажи, помещения)
    - Загрузка детальных данных при выборе узла
    
    Требует наличия в родительском классе:
    - model: TreeModel - модель данных
    - cache: DataCache - система кэширования
    - api_client: ApiClient - клиент API
    - show_loading: метод для отображения индикатора загрузки
    - _show_error: метод для отображения ошибок
    - data_loading/data_loaded/data_error: сигналы (опционально)
    - item_selected: сигнал выбора элемента (опционально)
    """
    
    # ===== Константы =====
    _DETAILS_LOAD_DELAY_MS = 10
    """Задержка перед отправкой обновлённых данных после загрузки деталей"""
    
    _LOADING_FLAG_RESET_DELAY_MS = 100
    """Задержка сброса флага загрузки"""
    
    _CACHE_KEY_COMPLEXES_ALL = "complexes:all"
    """Ключ для кэширования всех комплексов"""
    
    # ===== Приватные вспомогательные методы =====
    
    def _get_child_load_params(self, node) -> Optional[tuple]:
        """
        Определяет параметры для загрузки дочерних элементов.
        
        Args:
            node: Узел дерева (TreeNode)
            
        Returns:
            Кортеж (cache_key, load_func, child_type) или None
        """
        node_id = node.get_id()
        
        params_map = {
            NodeType.COMPLEX: (
                f"complex:{node_id}:buildings",
                self.api_client.get_buildings,
                NodeType.BUILDING
            ),
            NodeType.BUILDING: (
                f"building:{node_id}:floors",
                self.api_client.get_floors,
                NodeType.FLOOR
            ),
            NodeType.FLOOR: (
                f"floor:{node_id}:rooms",
                self.api_client.get_rooms,
                NodeType.ROOM
            )
        }
        
        return params_map.get(node.node_type)
    
    def _safe_emit_data_loading(self, node_type: NodeType, node_id: int) -> None:
        """
        Безопасно испускает сигнал начала загрузки.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        if hasattr(self, 'data_loading'):
            self.data_loading.emit(node_type.value, node_id)
    
    def _safe_emit_data_loaded(self, node_type: NodeType, node_id: int) -> None:
        """
        Безопасно испускает сигнал завершения загрузки.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
        """
        if hasattr(self, 'data_loaded'):
            self.data_loaded.emit(node_type.value, node_id)
    
    def _safe_emit_data_error(self, node_type: NodeType, node_id: int, error: str) -> None:
        """
        Безопасно испускает сигнал ошибки загрузки.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            error: Сообщение об ошибке
        """
        if hasattr(self, 'data_error'):
            self.data_error.emit(node_type.value, node_id, error)
    
    def _safe_emit_item_selected(self, item_type: str, item_id: int, 
                                  item_data: Any, context: dict) -> None:
        """
        Безопасно испускает сигнал выбора элемента.
        
        Args:
            item_type: Тип элемента
            item_id: Идентификатор элемента
            item_data: Данные элемента
            context: Контекст иерархии
        """
        if hasattr(self, 'item_selected'):
            self.item_selected.emit(item_type, item_id, item_data, context)
    
    # ===== Публичные методы загрузки =====
    
    @Slot()
    def load_complexes(self) -> None:
        """
        Загружает список всех комплексов (корневые узлы дерева).
        
        Выполняет следующие действия:
        1. Показывает индикатор загрузки
        2. Проверяет наличие данных в кэше
        3. При отсутствии загружает с сервера
        4. Обновляет модель
        5. Обновляет заголовок с количеством
        6. Скрывает индикатор загрузки
        """
        # Проверяем наличие метода отображения загрузки
        if not hasattr(self, 'show_loading'):
            log.error("TreeLoader: отсутствует метод show_loading")
            return
        
        self.show_loading(True)
        log.info("Загрузка комплексов...")
        
        try:
            # Проверяем кэш
            cached_complexes = self.cache.get(self._CACHE_KEY_COMPLEXES_ALL)
            
            if cached_complexes is not None:
                complexes = cached_complexes
                log.cache(f"Комплексы загружены из кэша: {len(complexes)} шт.")
            else:
                # Загружаем с сервера
                complexes = self.api_client.get_complexes()
                # Сохраняем в кэш
                self.cache.set(self._CACHE_KEY_COMPLEXES_ALL, complexes)
                log.api(f"Комплексы загружены с сервера: {len(complexes)} шт.")
            
            # Обновляем модель
            self.model.set_complexes(complexes)
            
            # Обновляем заголовок, если есть
            if hasattr(self, 'title_label'):
                self.title_label.setText(f"Объекты ({len(complexes)})")
            
            log.success(f"Загружено {len(complexes)} комплексов")
            
        except Exception as error:
            error_message = str(error)
            log.error(f"Ошибка загрузки комплексов: {error_message}")
            
            if hasattr(self, '_show_error'):
                self._show_error("Ошибка загрузки комплексов", error_message)
            
        finally:
            self.show_loading(False)
    
    # ===== Загрузка дочерних элементов =====
    
    @Slot(QModelIndex)
    def _load_children(self, parent_index: QModelIndex) -> None:
        """
        Загружает дочерние элементы для указанного узла (ленивая загрузка).
        
        Args:
            parent_index: Индекс родительского узла в модели
        """
        # Получаем узел
        node = self.model._get_node(parent_index)
        if not node:
            log.warning("TreeLoader: попытка загрузить детей для несуществующего узла")
            return
        
        # Проверяем наличие дочерних элементов
        has_children = self.model.hasChildren(parent_index)
        
        # Если дети уже загружены или узел не может их иметь - выходим
        if node.loaded or not has_children:
            log.debug(f"Загрузка детей не требуется для {node.node_type.value} #{node.get_id()}")
            return
        
        # Определяем параметры загрузки
        load_params = self._get_child_load_params(node)
        if not load_params:
            log.warning(f"TreeLoader: неизвестный тип узла {node.node_type}")
            return
        
        cache_key, load_func, child_type = load_params
        node_type = node.node_type
        node_id = node.get_id()
        
        # Сигнализируем о начале загрузки
        self._safe_emit_data_loading(node_type, node_id)
        log.debug(f"Начало загрузки {child_type.value} для {node_type.value} #{node_id}")
        
        try:
            # Проверяем кэш
            children = self.cache.get(cache_key)
            
            if children is not None:
                log.cache(f"{child_type.value} загружены из кэша для {node_type.value} #{node_id}")
            else:
                # Загружаем с сервера
                log.api(f"Загрузка {child_type.value} для {node_type.value} #{node_id}")
                children = load_func(node_id)
                # Сохраняем в кэш
                self.cache.set(cache_key, children)
                log.cache(f"Данные сохранены в кэш: {cache_key}")
            
            # Добавляем в модель
            if children:
                self.model.add_children(parent_index, children, child_type)
                log.data(f"В модель добавлено {len(children)} {child_type.value}")
            
            # Сигнализируем о завершении загрузки
            self._safe_emit_data_loaded(node_type, node_id)
            log.debug(f"Загрузка {child_type.value} завершена")
            
        except Exception as error:
            error_message = str(error)
            log.error(f"Ошибка загрузки {child_type.value}: {error_message}")
            self._safe_emit_data_error(node_type, node_id, error_message)
    
    # ===== Загрузка детальных данных =====
    
    @Slot(str, int, QModelIndex, dict)
    def _load_details_if_needed(self, item_type: str, item_id: int, 
                                 index: QModelIndex, context: dict) -> None:
        """
        Загружает детальные данные для узла, если они отсутствуют в текущем объекте.
        
        Args:
            item_type: Тип элемента
            item_id: Идентификатор элемента
            index: Индекс узла в модели
            context: Контекст иерархии
        """
        # Устанавливаем флаг загрузки
        if hasattr(self, '_set_loading_flag'):
            self._set_loading_flag(True)
        
        try:
            # Получаем узел
            node = self.model._get_node(index)
            if not node:
                log.warning(f"TreeLoader: узел {item_type} #{item_id} не найден")
                return
            
            item_data = node.data
            
            # Загружаем детали в зависимости от типа
            if item_type == 'complex' and isinstance(item_data, Complex):
                self._load_complex_details(item_id, index, context, item_data)
                
            elif item_type == 'building' and isinstance(item_data, Building):
                self._load_building_details(item_id, index, context, item_data)
                
            elif item_type == 'floor' and isinstance(item_data, Floor):
                self._load_floor_details(item_id, index, context, item_data)
                
            elif item_type == 'room' and isinstance(item_data, Room):
                self._load_room_details(item_id, index, context, item_data)
                
        finally:
            # Сбрасываем флаг через задержку
            if hasattr(self, '_reset_loading_flag'):
                QTimer.singleShot(self._LOADING_FLAG_RESET_DELAY_MS, self._reset_loading_flag)
    
    def _load_complex_details(self, complex_id: int, index: QModelIndex, 
                               context: dict, current_data: Complex) -> None:
        """
        Загружает детальные данные для комплекса.
        
        Args:
            complex_id: Идентификатор комплекса
            index: Индекс узла в модели
            context: Контекст иерархии
            current_data: Текущие данные комплекса
        """
        # Проверяем, нужно ли загружать детали
        if current_data.address is not None and current_data.description is not None:
            log.debug(f"Детали комплекса #{complex_id} уже загружены")
            return
        
        log.info(f"Загрузка деталей комплекса #{complex_id}")
        
        try:
            detailed_data = self.api_client.get_complex_detail(complex_id)
            
            if detailed_data:
                # Обновляем данные в узле
                node = self.model._get_node(index)
                if node:
                    node.data = detailed_data
                    
                    # Сигнализируем об изменении данных
                    self.model.dataChanged.emit(index, index, [])
                    
                    # Отправляем обновлённые данные с задержкой
                    QTimer.singleShot(
                        self._DETAILS_LOAD_DELAY_MS,
                        lambda: self._safe_emit_item_selected(
                            'complex', complex_id, detailed_data, context
                        )
                    )
                    
                    log.success(f"Детали комплекса #{complex_id} загружены")
                    
        except Exception as error:
            log.error(f"Ошибка загрузки деталей комплекса #{complex_id}: {error}")
    
    def _load_building_details(self, building_id: int, index: QModelIndex,
                                context: dict, current_data: Building) -> None:
        """
        Загружает детальные данные для корпуса.
        
        Args:
            building_id: Идентификатор корпуса
            index: Индекс узла в модели
            context: Контекст иерархии
            current_data: Текущие данные корпуса
        """
        # Проверяем, нужно ли загружать детали
        if (current_data.description is not None and 
            current_data.address is not None):
            log.debug(f"Детали корпуса #{building_id} уже загружены")
            return
        
        log.info(f"Загрузка деталей корпуса #{building_id}")
        
        try:
            detailed_data = self.api_client.get_building_detail(building_id)
            
            if detailed_data:
                node = self.model._get_node(index)
                if node:
                    node.data = detailed_data
                    self.model.dataChanged.emit(index, index, [])
                    
                    QTimer.singleShot(
                        self._DETAILS_LOAD_DELAY_MS,
                        lambda: self._safe_emit_item_selected(
                            'building', building_id, detailed_data, context
                        )
                    )
                    
                    log.success(f"Детали корпуса #{building_id} загружены")
                    
        except Exception as error:
            log.error(f"Ошибка загрузки деталей корпуса #{building_id}: {error}")
    
    def _load_floor_details(self, floor_id: int, index: QModelIndex,
                             context: dict, current_data: Floor) -> None:
        """
        Загружает детальные данные для этажа.
        
        Args:
            floor_id: Идентификатор этажа
            index: Индекс узла в модели
            context: Контекст иерархии
            current_data: Текущие данные этажа
        """
        # Проверяем, нужно ли загружать детали
        if current_data.description is not None:
            log.debug(f"Детали этажа #{floor_id} уже загружены")
            return
        
        log.info(f"Загрузка деталей этажа #{floor_id}")
        
        try:
            detailed_data = self.api_client.get_floor_detail(floor_id)
            
            if detailed_data:
                node = self.model._get_node(index)
                if node:
                    node.data = detailed_data
                    self.model.dataChanged.emit(index, index, [])
                    
                    QTimer.singleShot(
                        self._DETAILS_LOAD_DELAY_MS,
                        lambda: self._safe_emit_item_selected(
                            'floor', floor_id, detailed_data, context
                        )
                    )
                    
                    log.success(f"Детали этажа #{floor_id} загружены")
                    
        except Exception as error:
            log.error(f"Ошибка загрузки деталей этажа #{floor_id}: {error}")
    
    def _load_room_details(self, room_id: int, index: QModelIndex,
                            context: dict, current_data: Room) -> None:
        """
        Загружает детальные данные для помещения.
        
        Args:
            room_id: Идентификатор помещения
            index: Индекс узла в модели
            context: Контекст иерархии
            current_data: Текущие данные помещения
        """
        # Проверяем, нужно ли загружать детали
        if (current_data.area is not None and 
            current_data.status_code is not None):
            log.debug(f"Детали помещения #{room_id} уже загружены")
            return
        
        log.info(f"Загрузка деталей помещения #{room_id}")
        
        try:
            detailed_data = self.api_client.get_room_detail(room_id)
            
            if detailed_data:
                node = self.model._get_node(index)
                if node:
                    node.data = detailed_data
                    self.model.dataChanged.emit(index, index, [])
                    
                    QTimer.singleShot(
                        self._DETAILS_LOAD_DELAY_MS,
                        lambda: self._safe_emit_item_selected(
                            'room', room_id, detailed_data, context
                        )
                    )
                    
                    log.success(f"Детали помещения #{room_id} загружены")
                    
        except Exception as error:
            log.error(f"Ошибка загрузки деталей помещения #{room_id}: {error}")
    
    # ===== Управление флагами =====
    
    @Slot()
    def _reset_loading_flag(self) -> None:
        """Сбрасывает флаг загрузки деталей."""
        if hasattr(self, '_set_loading_flag'):
            self._set_loading_flag(False)
            log.debug("Флаг загрузки сброшен")
    
    @Slot(str, int, object, dict)
    def _emit_updated_selection(self, item_type: str, item_id: int, 
                                 item_data: Any, context: dict) -> None:
        """
        Отправляет обновлённые данные о выделении.
        
        Args:
            item_type: Тип элемента
            item_id: Идентификатор элемента
            item_data: Данные элемента
            context: Контекст иерархии
        """
        self._safe_emit_item_selected(item_type, item_id, item_data, context)
        log.debug(f"Обновлённые данные отправлены для {item_type} #{item_id}")