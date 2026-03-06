# client/src/ui/tree/tree_updater.py
"""
Модуль для обновления данных дерева.
Содержит логику трёх уровней обновления:
- Текущий узел (F5)
- Все раскрытые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtCore import QModelIndex, Slot, QTimer
from typing import Optional, Dict, Any, Tuple

from src.ui.tree_model import NodeType

from src.utils.logger import get_logger
log = get_logger(__name__)

class TreeUpdaterMixin:
    """
    Миксин для обновления данных дерева.
    
    Предоставляет методы для обновления данных на разных уровнях:
    - refresh_current() - обновление текущего выбранного узла
    - refresh_visible() - обновление всех раскрытых узлов
    - full_reset() - полная перезагрузка всех данных
    
    Требует наличия в родительском классе:
    - model: TreeModel - модель данных
    - tree_view: QTreeView - виджет дерева
    - cache: DataCache - система кэширования
    - api_client: ApiClient - клиент API
    - data_error: Signal - сигнал ошибки
    """
    
    # ===== Константы =====
    _SELECTION_RESTORE_DELAY_MS = 100
    """Задержка восстановления выделения после обновления в миллисекундах"""
    
    # ===== Приватные вспомогательные методы =====
    
    def _get_update_params(self, node) -> Optional[Tuple[str, Any, NodeType]]:
        """
        Определяет параметры для обновления узла.
        
        Args:
            node: Узел дерева (TreeNode)
            
        Returns:
            Кортеж (cache_key, load_func, child_type) или None, если тип не поддерживается
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
    
    def _safe_emit_error(self, node_type: str, node_id: int, error: str) -> None:
        """
        Безопасно испускает сигнал ошибки, если он доступен.
        
        Args:
            node_type: Тип узла
            node_id: Идентификатор узла
            error: Сообщение об ошибке
        """
        if hasattr(self, 'data_error'):
            self.data_error.emit(node_type, node_id, error)
    
    # ===== Публичные методы обновления =====
    
    @Slot()
    def refresh_current(self) -> None:
        """
        Обновляет текущий выбранный узел.
        
        Выполняет следующие действия:
        1. Получает информацию о выбранном узле
        2. Инвалидирует кэш дочерних элементов
        3. Загружает свежие данные
        4. Обновляет модель
        5. Восстанавливает выделение
        
        Горячая клавиша: F5
        """
        # Проверяем наличие необходимых методов
        if not hasattr(self, 'get_selected_node_info'):
            log.error("TreeUpdater: отсутствует метод get_selected_node_info")
            return
        
        # Получаем информацию о выбранном узле
        selected_info = self.get_selected_node_info()
        if not selected_info:
            log.info("TreeUpdater: нет выбранного узла для обновления")
            return
        
        node_type, node_id, _ = selected_info
        
        # Находим индекс узла в модели
        index = self.model.get_index_by_id(NodeType(node_type), node_id)
        if not index.isValid():
            log.warning(f"TreeUpdater: узел {node_type} #{node_id} не найден в модели")
            return
        
        # Получаем узел и его контекст
        node = self.model._get_node(index)
        if not node:
            return
        
        context = self._get_context_for_node(node)
        log.info(f"Обновление узла {node_type} #{node_id}")
        
        # Определяем параметры обновления
        params = self._get_update_params(node)
        if not params:
            log.warning(f"TreeUpdater: неподдерживаемый тип узла {node.node_type}")
            return
        
        cache_key, load_func, child_type = params
        
        # Блокируем сигналы выделения на время обновления
        self.tree_view.selectionModel().blockSignals(True)
        
        try:
            # Инвалидируем кэш дочерних элементов
            self.cache.remove(cache_key)
            
            # Загружаем свежие данные
            children = load_func(node_id)
            
            if children is not None:
                # Обновляем модель
                self.model.update_children(index, children, child_type)
                # Сохраняем в кэш
                self.cache.set(cache_key, children)
                log.success(f"Узел {node_type} #{node_id} обновлён")
            
        except Exception as error:
            error_message = str(error)
            log.error(f"Ошибка обновления {node_type} #{node_id}: {error_message}")
            self._safe_emit_error(node_type, node_id, error_message)
            
        finally:
            # Разблокируем сигналы
            self.tree_view.selectionModel().blockSignals(False)
        
        # Восстанавливаем выделение после задержки
        QTimer.singleShot(
            self._SELECTION_RESTORE_DELAY_MS,
            lambda: self._restore_selection_safe(node_type, node_id, context)
        )
    
    @Slot()
    def refresh_visible(self) -> None:
        """
        Обновляет все раскрытые узлы в дереве.
        
        Выполняет следующие действия:
        1. Получает список раскрытых узлов из кэша
        2. Запоминает текущий выбранный узел
        3. Обновляет каждый раскрытый узел
        4. Восстанавливает выделение
        
        Горячая клавиша: Ctrl+F5
        """
        # Получаем список раскрытых узлов
        expanded_nodes = self.cache.get_expanded_nodes()
        if not expanded_nodes:
            log.info("TreeUpdater: нет раскрытых узлов для обновления")
            return
        
        # Запоминаем текущий выбранный узел
        selected_info = self.get_selected_node_info()
        selected_type = None
        selected_id = None
        selected_context = None
        
        if selected_info:
            selected_type, selected_id, _ = selected_info
            index = self.model.get_index_by_id(NodeType(selected_type), selected_id)
            if index.isValid():
                node = self.model._get_node(index)
                if node:
                    selected_context = self._get_context_for_node(node)
            log.debug(f"Будет восстановлен узел: {selected_type} #{selected_id}")
        
        log.info(f"Обновление {len(expanded_nodes)} раскрытых узлов")
        
        # Блокируем сигналы выделения
        self.tree_view.selectionModel().blockSignals(True)
        
        try:
            # Обновляем каждый раскрытый узел
            for node_type, node_id in expanded_nodes:
                index = self.model.get_index_by_id(NodeType(node_type), node_id)
                if index.isValid():
                    self._refresh_node(index, use_cache=False)
            
            log.success(f"Обновление {len(expanded_nodes)} узлов завершено")
            
        finally:
            # Разблокируем сигналы
            self.tree_view.selectionModel().blockSignals(False)
        
        # Восстанавливаем выделение
        if selected_type and selected_id:
            QTimer.singleShot(
                self._SELECTION_RESTORE_DELAY_MS,
                lambda: self._restore_selection_safe(selected_type, selected_id, selected_context)
            )
    
    @Slot()
    def full_reset(self) -> None:
        """
        Выполняет полную перезагрузку всех данных.
        
        Действия:
        1. Очищает весь кэш
        2. Перезагружает комплексы
        3. Сбрасывает состояние дерева
        
        Горячая клавиша: Ctrl+Shift+F5
        """
        log.info("Полная перезагрузка данных")
        
        # Очищаем кэш
        self.cache.clear()
        
        # Перезагружаем корневые элементы
        self.load_complexes()
        
        log.success("Полная перезагрузка завершена")
    
    # ===== Защищённые методы обновления =====
    
    @Slot(QModelIndex, bool)
    def _refresh_node(self, index: QModelIndex, use_cache: bool = False) -> None:
        """
        Обновляет конкретный узел дерева.
        
        Args:
            index: Индекс обновляемого узла
            use_cache: Флаг использования кэша
                      True - использовать кэш (если есть)
                      False - принудительно загружать с сервера
        """
        # Получаем узел
        node = self.model._get_node(index)
        if not node:
            log.warning("TreeUpdater: попытка обновить несуществующий узел")
            return
        
        node_type = node.node_type.value
        node_id = node.get_id()
        
        # Определяем параметры обновления
        params = self._get_update_params(node)
        if not params:
            log.warning(f"TreeUpdater: неподдерживаемый тип узла {node.node_type}")
            return
        
        cache_key, load_func, child_type = params
        
        # Принудительно удаляем кэш, если не разрешено его использовать
        if not use_cache:
            self.cache.remove(cache_key)
            log.debug(f"Кэш {cache_key} инвалидирован")
        
        try:
            # Загружаем данные
            if use_cache:
                children = self.cache.get(cache_key)
                if children is None:
                    log.debug(f"Кэш пуст, загрузка с сервера для {node_type} #{node_id}")
                    children = load_func(node_id)
                    self.cache.set(cache_key, children)
            else:
                log.debug(f"Принудительная загрузка с сервера для {node_type} #{node_id}")
                children = load_func(node_id)
                self.cache.set(cache_key, children)
            
            # Обновляем модель
            if children is not None:
                self.model.update_children(index, children, child_type)
                log.debug(f"Модель обновлена для {node_type} #{node_id}")
            
        except Exception as error:
            error_message = str(error)
            log.error(f"Ошибка обновления {node_type} #{node_id}: {error_message}")
            self._safe_emit_error(node_type, node_id, error_message)