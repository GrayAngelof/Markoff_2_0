# client/src/ui/tree/tree_loader.py
"""
Модуль для загрузки данных дерева
"""
from PySide6.QtCore import QModelIndex, Slot, QTimer
from typing import Optional

from src.ui.tree_model import NodeType
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class TreeLoaderMixin:
    """
    Миксин для загрузки данных дерева
    """
    
    @Slot()
    def load_complexes(self):
        """Загрузка комплексов (корневые узлы)"""
        if not hasattr(self, 'show_loading'):
            return
        
        self.show_loading(True)
        
        try:
            # Проверяем кэш
            cached = self.cache.get("complexes:all")
            if cached:
                print("📦 TreeView: комплексы загружены из кэша")
                complexes = cached
            else:
                # Загружаем с сервера
                complexes = self.api_client.get_complexes()
                # Сохраняем в кэш
                self.cache.set("complexes:all", complexes)
                print("🌐 TreeView: комплексы загружены с сервера")
            
            # Обновляем модель
            self.model.set_complexes(complexes)
            
            # Обновляем заголовок
            if hasattr(self, 'title_label'):
                self.title_label.setText(f"Объекты ({len(complexes)})")
            
        except Exception as e:
            if hasattr(self, '_show_error'):
                self._show_error("Ошибка загрузки комплексов", str(e))
            
        finally:
            self.show_loading(False)
    
    @Slot(QModelIndex)
    def _load_children(self, parent_index: QModelIndex):
        """
        Загрузка дочерних элементов для узла (первоначальная загрузка)
        """
        node = self.model._get_node(parent_index)
        if not node:
            return
        
        # Проверяем через модель, есть ли у узла дети
        has_children = self.model.hasChildren(parent_index)
        
        # Если уже загружено или не может иметь детей - выходим
        if node.loaded or not has_children:
            return

        # Определяем, что и как загружать
        node_type = node.node_type
        node_id = node.get_id()
        
        # Формируем ключ для кэша и функцию загрузки
        if node_type == NodeType.COMPLEX:
            cache_key = f"complex:{node_id}:buildings"
            load_func = self.api_client.get_buildings
            child_type = NodeType.BUILDING
        elif node_type == NodeType.BUILDING:
            cache_key = f"building:{node_id}:floors"
            load_func = self.api_client.get_floors
            child_type = NodeType.FLOOR
        elif node_type == NodeType.FLOOR:
            cache_key = f"floor:{node_id}:rooms"
            load_func = self.api_client.get_rooms
            child_type = NodeType.ROOM
        else:
            return
        
        # Сигнализируем о начале загрузки
        if hasattr(self, 'data_loading'):
            self.data_loading.emit(node_type.value, node_id)
        
        try:
            # Проверяем кэш
            children = self.cache.get(cache_key)
            
            if children is not None:
                print(f"📦 TreeView: {child_type.value} загружены из кэша для {node_type.value} #{node_id}")
            else:
                # Загружаем с сервера
                print(f"🌐 TreeView: загрузка {child_type.value} для {node_type.value} #{node_id}")
                children = load_func(node_id)
                # Сохраняем в кэш
                self.cache.set(cache_key, children)
            
            # Добавляем в модель
            if children:
                self.model.add_children(parent_index, children, child_type)
            
            if hasattr(self, 'data_loaded'):
                self.data_loaded.emit(node_type.value, node_id)
            
        except Exception as e:
            print(f"❌ TreeView: ошибка загрузки {child_type.value}: {e}")
            if hasattr(self, 'data_error'):
                self.data_error.emit(node_type.value, node_id, str(e))
    
    @Slot(str, int, QModelIndex, dict)
    def _load_details_if_needed(self, item_type: str, item_id: int, index: QModelIndex, context: dict):
        """Загрузить детальные данные, если их нет в текущем объекте"""
        # Устанавливаем флаг загрузки
        if hasattr(self, '_loading_details'):
            self._loading_details = True
        
        try:
            node = self.model._get_node(index)
            if not node:
                return
            
            item_data = node.data
            
            if item_type == 'complex' and isinstance(item_data, Complex):
                if item_data.address is None and item_data.description is None:
                    print(f"🔍 Загружаем детали комплекса #{item_id}")
                    detailed = self.api_client.get_complex_detail(item_id)
                    if detailed:
                        node.data = detailed
                        self.model.dataChanged.emit(index, index, [])
                        # Отправляем обновлённые данные с тем же контекстом
                        QTimer.singleShot(10, 
                            lambda: self._emit_updated_selection(item_type, item_id, detailed, context))
            
            elif item_type == 'building' and isinstance(item_data, Building):
                if item_data.description is None and item_data.address is None:
                    print(f"🔍 Загружаем детали корпуса #{item_id}")
                    detailed = self.api_client.get_building_detail(item_id)
                    if detailed:
                        node.data = detailed
                        self.model.dataChanged.emit(index, index, [])
                        QTimer.singleShot(10, 
                            lambda: self._emit_updated_selection(item_type, item_id, detailed, context))
            
            elif item_type == 'floor' and isinstance(item_data, Floor):
                if item_data.description is None:
                    print(f"🔍 Загружаем детали этажа #{item_id}")
                    detailed = self.api_client.get_floor_detail(item_id)
                    if detailed:
                        node.data = detailed
                        self.model.dataChanged.emit(index, index, [])
                        QTimer.singleShot(10, 
                            lambda: self._emit_updated_selection(item_type, item_id, detailed, context))
            
            elif item_type == 'room' and isinstance(item_data, Room):
                if item_data.area is None or item_data.status_code is None:
                    print(f"🔍 Загружаем детали помещения #{item_id}")
                    detailed = self.api_client.get_room_detail(item_id)
                    if detailed:
                        node.data = detailed
                        self.model.dataChanged.emit(index, index, [])
                        QTimer.singleShot(10, 
                            lambda: self._emit_updated_selection(item_type, item_id, detailed, context))
        finally:
            # Сбрасываем флаг через небольшую задержку
            if hasattr(self, '_reset_loading_flag'):
                QTimer.singleShot(100, self._reset_loading_flag)
    
    @Slot()
    def _reset_loading_flag(self):
        """Сбросить флаг загрузки деталей"""
        if hasattr(self, '_loading_details'):
            self._loading_details = False
    
    @Slot(str, int, object, dict)
    def _emit_updated_selection(self, item_type: str, item_id: int, item_data, context: dict):
        """Отправить обновлённые данные в DetailsPanel"""
        if hasattr(self, 'item_selected'):
            self.item_selected.emit(item_type, item_id, item_data, context)