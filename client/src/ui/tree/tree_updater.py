# client/src/ui/tree/tree_updater.py
"""
Модуль для обновления данных дерева
"""
from PySide6.QtCore import QModelIndex, Slot, QTimer
from typing import Optional

from src.ui.tree_model import NodeType


class TreeUpdaterMixin:
    """
    Миксин для обновления данных дерева
    """
    
    @Slot()
    def refresh_current(self):
        """Обновить текущий выбранный узел"""
        if not hasattr(self, 'get_selected_node_info'):
            return
        
        info = self.get_selected_node_info()
        if not info:
            print("⚠️ TreeView: нет выбранного узла для обновления")
            return
        
        node_type, node_id, _ = info
        
        # Находим индекс узла
        index = self.model.get_index_by_id(NodeType(node_type), node_id)
        if not index.isValid():
            return
        
        node = self.model._get_node(index)
        if not node:
            return
        
        context = self._get_context_for_node(node)
        
        print(f"🔄 TreeView: обновление узла {node_type} #{node_id}")
        
        # Определяем параметры для обновления
        if node.node_type == NodeType.COMPLEX:
            cache_key = f"complex:{node_id}:buildings"
            load_func = self.api_client.get_buildings
            child_type = NodeType.BUILDING
        elif node.node_type == NodeType.BUILDING:
            cache_key = f"building:{node_id}:floors"
            load_func = self.api_client.get_floors
            child_type = NodeType.FLOOR
        elif node.node_type == NodeType.FLOOR:
            cache_key = f"floor:{node_id}:rooms"
            load_func = self.api_client.get_rooms
            child_type = NodeType.ROOM
        else:
            return
        
        # Блокируем сигналы на время обновления
        self.tree_view.selectionModel().blockSignals(True)
        
        try:
            # Удаляем кэш детей
            self.cache.remove(cache_key)
            
            # Загружаем свежие данные
            children = load_func(node_id)
            
            if children is not None:
                # Обновляем детей в модели
                self.model.update_children(index, children, child_type)
                # Сохраняем в кэш
                self.cache.set(cache_key, children)
            
            print(f"✅ TreeView: узел {node_type} #{node_id} обновлён")
            
        except Exception as e:
            print(f"❌ TreeView: ошибка обновления {node_type} #{node_id}: {e}")
            if hasattr(self, 'data_error'):
                self.data_error.emit(node_type, node_id, str(e))
            
        finally:
            # Разблокируем сигналы
            self.tree_view.selectionModel().blockSignals(False)
        
        # Восстанавливаем выделение
        QTimer.singleShot(100, lambda: self._restore_selection_safe(node_type, node_id, context))
    
    @Slot()
    def refresh_visible(self):
        """Обновить все раскрытые узлы"""
        expanded = self.cache.get_expanded_nodes()
        if not expanded:
            print("ℹ️ TreeView: нет раскрытых узлов для обновления")
            return
        
        # Запоминаем текущий выбранный узел
        selected_info = self.get_selected_node_info()
        selected_type, selected_id, selected_context = None, None, None
        
        if selected_info:
            selected_type, selected_id, _ = selected_info
            index = self.model.get_index_by_id(NodeType(selected_type), selected_id)
            if index.isValid():
                node = self.model._get_node(index)
                if node:
                    selected_context = self._get_context_for_node(node)
            print(f"🔍 Будет восстановлен узел: {selected_type} #{selected_id}")
        
        print(f"🔄 TreeView: обновление {len(expanded)} раскрытых узлов")
        
        # Блокируем сигналы на время обновления
        self.tree_view.selectionModel().blockSignals(True)
        
        try:
            for node_type, node_id in expanded:
                index = self.model.get_index_by_id(NodeType(node_type), node_id)
                if index.isValid():
                    self._refresh_node(index, use_cache=False)
            
            print(f"✅ TreeView: обновление {len(expanded)} узлов завершено")
            
        finally:
            # Разблокируем сигналы
            self.tree_view.selectionModel().blockSignals(False)
        
        # Восстанавливаем выделение
        if selected_type and selected_id:
            QTimer.singleShot(100, 
                lambda: self._restore_selection_safe(selected_type, selected_id, selected_context))
    
    @Slot()
    def full_reset(self):
        """Полная перезагрузка"""
        print("🔄 TreeView: полная перезагрузка")
        
        # Очищаем кэш
        self.cache.clear()
        
        # Перезагружаем комплексы
        self.load_complexes()
    
    @Slot(QModelIndex, bool)
    def _refresh_node(self, index: QModelIndex, use_cache: bool = False):
        """Обновить конкретный узел"""
        node = self.model._get_node(index)
        if not node:
            return
        
        node_type = node.node_type.value
        node_id = node.get_id()
        
        # Определяем параметры для обновления
        if node.node_type == NodeType.COMPLEX:
            cache_key = f"complex:{node_id}:buildings"
            load_func = self.api_client.get_buildings
            child_type = NodeType.BUILDING
        elif node.node_type == NodeType.BUILDING:
            cache_key = f"building:{node_id}:floors"
            load_func = self.api_client.get_floors
            child_type = NodeType.FLOOR
        elif node.node_type == NodeType.FLOOR:
            cache_key = f"floor:{node_id}:rooms"
            load_func = self.api_client.get_rooms
            child_type = NodeType.ROOM
        else:
            return
        
        # Если не используем кэш - удаляем его
        if not use_cache:
            self.cache.remove(cache_key)
        
        try:
            # Загружаем данные
            if use_cache:
                children = self.cache.get(cache_key)
                if children is None:
                    children = load_func(node_id)
                    self.cache.set(cache_key, children)
            else:
                children = load_func(node_id)
                self.cache.set(cache_key, children)
            
            # Обновляем детей в модели
            if children is not None:
                self.model.update_children(index, children, child_type)
            
        except Exception as e:
            print(f"❌ TreeView: ошибка обновления {node_type} #{node_id}: {e}")
            if hasattr(self, 'data_error'):
                self.data_error.emit(node_type, node_id, str(e))