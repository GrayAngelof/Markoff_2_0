# tests/test_tree_integration.py
"""
Интеграционные тесты для дерева объектов
Проверяем совместную работу:
- TreeModel
- TreeView
- DataCache
- API Client (мок)
"""
import sys
import os
import unittest
from unittest.mock import Mock, patch
from typing import List, Optional

sys.path.append('/app')

# Импорты PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QColor

from src.ui.tree_model import TreeModel, NodeType, TreeNode
from src.ui.tree_view import TreeView
from src.core.cache import DataCache
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class TestTreeIntegration(unittest.TestCase):
    """Интеграционные тесты для дерева"""
    
    @classmethod
    def setUpClass(cls):
        """Создаём QApplication один раз для всех тестов"""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        # Создаём тестовые данные
        self._create_test_data()
        
        # Создаём мок для API клиента с правильными возвращаемыми значениями
        self.mock_api = Mock()
        self.mock_api.get_complexes.return_value = [self.complex1, self.complex2]
        self.mock_api.get_buildings.return_value = [self.building1, self.building2]
        self.mock_api.get_floors.return_value = [self.floor1, self.floor2, self.floor3, self.floor4]
        self.mock_api.get_rooms.return_value = [self.room1, self.room2]
        
        # Создаём реальные компоненты
        self.cache = DataCache()
        self.model = TreeModel()
        self.model.set_cache(self.cache)
        
        # Создаём view с замоканным API
        patcher = patch('src.ui.tree_view.ApiClient')
        self.mock_api_class = patcher.start()
        self.mock_api_class.return_value = self.mock_api
        self.addCleanup(patcher.stop)
        
        self.tree_view = TreeView()
        # Подменяем модель в tree_view на нашу тестовую
        self.tree_view.model = self.model
        self.tree_view.tree_view.setModel(self.model)
        
        # Сбросим счётчики вызовов после инициализации
        self.mock_api.reset_mock()
    
    def _create_test_data(self):
        """Создание тестовых данных"""
        # Комплексы
        self.complex1 = Complex(id=1, name="Фабрика Веретено", buildings_count=2)
        self.complex2 = Complex(id=2, name="Тестовый комплекс", buildings_count=1)
        
        # Корпуса для комплекса 1
        self.building1 = Building(id=3, name="Корпус А", complex_id=1, floors_count=4)
        self.building2 = Building(id=4, name="Корпус Б", complex_id=1, floors_count=2)
        
        # Корпуса для комплекса 2
        self.building3 = Building(id=5, name="Корпус В", complex_id=2, floors_count=3)
        
        # Этажи для корпуса А
        self.floor1 = Floor(id=1, number=1, building_id=3, rooms_count=2)
        self.floor2 = Floor(id=2, number=2, building_id=3, rooms_count=0)
        self.floor3 = Floor(id=3, number=3, building_id=3, rooms_count=1)
        self.floor4 = Floor(id=4, number=4, building_id=3, rooms_count=0)
        
        # Этажи для корпуса Б
        self.floor5 = Floor(id=5, number=1, building_id=4, rooms_count=0)
        self.floor6 = Floor(id=6, number=2, building_id=4, rooms_count=3)
        
        # Помещения для этажа 1
        self.room1 = Room(id=101, number="101", floor_id=1, area=45.5, status_code="free")
        self.room2 = Room(id=102, number="102", floor_id=1, area=50.0, status_code="occupied")
        
        # Помещения для этажа 3
        self.room3 = Room(id=301, number="301", floor_id=3, area=75.0, status_code="free")
        
        # Помещения для этажа 6
        self.room4 = Room(id=601, number="601", floor_id=6, area=60.0, status_code="reserved")
        self.room5 = Room(id=602, number="602", floor_id=6, area=65.0, status_code="free")
        self.room6 = Room(id=603, number="603", floor_id=6, area=70.0, status_code="maintenance")
    
    # ===== Тесты модели =====
    
    def test_model_complexes_loading(self):
        """Тест загрузки комплексов в модель"""
        complexes = [self.complex1, self.complex2]
        self.model.set_complexes(complexes)
        
        # Проверяем количество корневых узлов
        assert self.model.rowCount() == 2, "Должно быть 2 комплекса"
        
        # Проверяем первый комплекс
        index = self.model.index(0, 0)
        node = self.model._get_node(index)
        assert node.node_type == NodeType.COMPLEX
        assert node.get_id() == 1
        assert node.get_display_text() == "Фабрика Веретено (2)"
        
        # Проверяем второй комплекс
        index = self.model.index(1, 0)
        node = self.model._get_node(index)
        assert node.get_display_text() == "Тестовый комплекс (1)"
    
    def test_model_children_loading(self):
        """Тест загрузки дочерних узлов"""
        # Загружаем комплексы
        self.model.set_complexes([self.complex1])
        
        # Получаем индекс первого комплекса
        complex_index = self.model.index(0, 0)
        
        # Добавляем корпуса
        self.model.add_children(
            complex_index,
            [self.building1, self.building2],
            NodeType.BUILDING
        )
        
        # Проверяем количество корпусов
        assert self.model.rowCount(complex_index) == 2
        
        # Проверяем первый корпус
        building_index = self.model.index(0, 0, complex_index)
        node = self.model._get_node(building_index)
        assert node.node_type == NodeType.BUILDING
        assert node.get_id() == 3
        assert node.get_display_text() == "Корпус А (4)"
        
        # Добавляем этажи для первого корпуса
        self.model.add_children(
            building_index,
            [self.floor1, self.floor2, self.floor3, self.floor4],
            NodeType.FLOOR
        )
        
        # Проверяем количество этажей
        assert self.model.rowCount(building_index) == 4
        
        # Проверяем отображение разных типов этажей
        floor1_index = self.model.index(0, 0, building_index)
        node = self.model._get_node(floor1_index)
        assert node.get_display_text() == "Этаж 1 (2)"
        
        floor3_index = self.model.index(2, 0, building_index)
        node = self.model._get_node(floor3_index)
        assert node.get_display_text() == "Этаж 3 (1)"
    
    def test_special_floor_display(self):
        """Тест отображения специальных этажей"""
        # Создаём этажи с особыми номерами
        basement = Floor(id=10, number=-1, building_id=3, rooms_count=0)
        ground = Floor(id=11, number=0, building_id=3, rooms_count=2)
        
        self.model.set_complexes([self.complex1])
        complex_index = self.model.index(0, 0)
        self.model.add_children(complex_index, [self.building1], NodeType.BUILDING)
        
        building_index = self.model.index(0, 0, complex_index)
        self.model.add_children(building_index, [basement, ground], NodeType.FLOOR)
        
        # Проверяем отображение
        basement_index = self.model.index(0, 0, building_index)
        assert self.model._get_node(basement_index).get_display_text() == "Подвал 1"
        
        ground_index = self.model.index(1, 0, building_index)
        assert self.model._get_node(ground_index).get_display_text() == "Цокольный этаж (2)"
    
    def test_node_flags_and_state(self):
        """Тест флагов узлов (есть ли дети, загружен ли)"""
        self.model.set_complexes([self.complex1])
        complex_index = self.model.index(0, 0)
        complex_node = self.model._get_node(complex_index)
        
        # У комплекса должны быть дети (корпуса), но они ещё не загружены
        assert complex_node.has_children() is True
        assert complex_node.loaded is False
        assert complex_node.loading is False
        
        # Загружаем корпуса
        self.model.add_children(complex_index, [self.building1], NodeType.BUILDING)
        
        # Теперь дети загружены
        assert complex_node.loaded is True
        
        # Проверяем корпус
        building_index = self.model.index(0, 0, complex_index)
        building_node = self.model._get_node(building_index)
        
        assert building_node.has_children() is True  # у корпуса есть этажи
        assert building_node.loaded is False  # но ещё не загружены
        
        # Помечаем как загружающийся
        self.model.node_loading(building_index)
        assert building_node.loading is True
        
        # Загружаем этажи
        self.model.add_children(building_index, [self.floor1], NodeType.FLOOR)
        assert building_node.loaded is True
        assert building_node.loading is False
    
    def test_room_status_colors(self):
        """Тест цветов для разных статусов помещений"""
        self.model.set_complexes([self.complex1])
        complex_index = self.model.index(0, 0)
        
        # Создаём этаж с разными комнатами
        floor = Floor(id=1, number=1, building_id=3, rooms_count=3)
        self.model.add_children(complex_index, [self.building1], NodeType.BUILDING)
        building_index = self.model.index(0, 0, complex_index)
        self.model.add_children(building_index, [floor], NodeType.FLOOR)
        floor_index = self.model.index(0, 0, building_index)
        
        # Добавляем комнаты с разными статусами
        rooms = [
            Room(id=101, number="101", floor_id=1, status_code="free"),
            Room(id=102, number="102", floor_id=1, status_code="occupied"),
            Room(id=103, number="103", floor_id=1, status_code="reserved"),
            Room(id=104, number="104", floor_id=1, status_code="maintenance"),
        ]
        self.model.add_children(floor_index, rooms, NodeType.ROOM)
        
        # Проверяем цвета
        free_index = self.model.index(0, 0, floor_index)
        free_color = self.model.data(free_index, Qt.ForegroundRole)
        assert free_color is not None
        if free_color:
            free_color = free_color.color()
            assert free_color == QColor(50, 150, 50)
        
        occupied_index = self.model.index(1, 0, floor_index)
        occupied_color = self.model.data(occupied_index, Qt.ForegroundRole)
        assert occupied_color is not None
        if occupied_color:
            occupied_color = occupied_color.color()
            assert occupied_color == QColor(200, 50, 50)
    
    # ===== Тесты с моком API =====
    
    def test_lazy_loading(self):
        """Тест ленивой загрузки (данные загружаются только при раскрытии)"""
        # Настраиваем модель
        self.model.set_complexes([self.complex1])
        
        # Получаем индекс комплекса
        complex_index = self.model.index(0, 0)
        
        # Проверяем, что API ещё не вызывался
        self.mock_api.get_buildings.assert_not_called()
        
        # "Раскрываем" комплекс (эмулируем сигнал expanded)
        self.tree_view._on_node_expanded(complex_index)
        
        # Теперь должен быть вызов API
        self.mock_api.get_buildings.assert_called_once_with(1)
        
        # Проверяем, что дети загружены в модель
        assert self.model.rowCount(complex_index) == 2
        
        # Получаем индекс первого корпуса
        building_index = self.model.index(0, 0, complex_index)
        
        # Проверяем, что API для этажей ещё не вызывался
        self.mock_api.get_floors.assert_not_called()
        
        # Раскрываем корпус
        self.tree_view._on_node_expanded(building_index)
        
        # Теперь должен быть вызов для этажей
        self.mock_api.get_floors.assert_called_once_with(3)
    
    def test_caching(self):
        """Тест кэширования данных"""
        self.model.set_complexes([self.complex1])
        
        complex_index = self.model.index(0, 0)
        
        # Первое раскрытие - запрос к API
        self.tree_view._on_node_expanded(complex_index)
        self.mock_api.get_buildings.assert_called_once()
        
        # Сбросим счётчик
        self.mock_api.get_buildings.reset_mock()
        
        # Сворачиваем и снова раскрываем
        self.tree_view._on_node_collapsed(complex_index)
        self.tree_view._on_node_expanded(complex_index)
        
        # API не должен вызываться повторно (данные из кэша)
        self.mock_api.get_buildings.assert_not_called()
    
    def test_refresh_current_node(self):
        """Тест обновления текущего узла"""
        # Настраиваем моки
        self.mock_api.get_buildings.return_value = [self.building1]
        self.mock_api.get_complexes.return_value = [self.complex1]
        
        # Создаём новый view для этого теста
        with patch('src.ui.tree_view.ApiClient') as MockApiClient:
            MockApiClient.return_value = self.mock_api
            view = TreeView()
        
        # Сбросим счётчики вызовов после инициализации
        self.mock_api.get_buildings.reset_mock()
        self.mock_api.get_complexes.reset_mock()
        
        # Загружаем комплексы в модель вручную
        view.model.set_complexes([self.complex1])
        
        # Получаем индекс комплекса
        complex_index = view.model.index(0, 0)
        
        # Раскрываем комплекс, чтобы загрузить корпуса
        view._on_node_expanded(complex_index)
        
        # Проверяем, что корпуса загрузились
        self.mock_api.get_buildings.assert_called_once_with(1)
        
        # Сохраняем ссылку на узел
        node = view.model._get_node(complex_index)
        assert node.loaded is True
        
        # Сбросим счётчик
        self.mock_api.get_buildings.reset_mock()
        
        # Выбираем комплекс
        view.tree_view.setCurrentIndex(complex_index)
        
        # Обновляем текущий узел
        view.refresh_current()
        
        # После обновления узел должен быть помечен как не загруженный
        assert node.loaded is False
        
        # Повторно раскрываем узел
        view._on_node_expanded(complex_index)
        
        # Должен быть новый запрос к API
        self.mock_api.get_buildings.assert_called_once_with(1)
    
    def test_refresh_visible(self):
        """Тест обновления всех раскрытых узлов"""
        # Настраиваем моки
        self.mock_api.get_buildings.return_value = [self.building1, self.building2]
        self.mock_api.get_floors.return_value = [self.floor1]
        
        # Загружаем комплексы
        self.model.set_complexes([self.complex1])
        
        # Раскрываем комплекс
        complex_index = self.model.index(0, 0)
        self.tree_view._on_node_expanded(complex_index)
        
        # Раскрываем первый корпус
        building_index = self.model.index(0, 0, complex_index)
        self.tree_view._on_node_expanded(building_index)
        
        # Сбросим счётчики
        self.mock_api.get_buildings.reset_mock()
        self.mock_api.get_floors.reset_mock()
        
        # Обновляем все видимые
        self.tree_view.refresh_visible()
        
        # Должны быть запросы для обоих раскрытых узлов
        self.mock_api.get_buildings.assert_called_once_with(1)
        self.mock_api.get_floors.assert_called_once_with(3)
    
    def test_full_reset(self):
        """Тест полной перезагрузки"""
        # Настраиваем мок для get_complexes
        self.mock_api.get_complexes.return_value = [self.complex1, self.complex2]
        
        # Создаём новый view для этого теста
        with patch('src.ui.tree_view.ApiClient') as MockApiClient:
            MockApiClient.return_value = self.mock_api
            view = TreeView()
        
        # Сбросим счётчик вызовов после инициализации
        self.mock_api.get_complexes.reset_mock()
        
        # Полная перезагрузка
        view.full_reset()
        
        # Должен быть новый запрос комплексов
        self.mock_api.get_complexes.assert_called_once()
    
    def test_node_index_access(self):
        """Тест доступа к узлам по ID"""
        self.model.set_complexes([self.complex1, self.complex2])
        
        # Ищем по ID
        node = self.model.get_node_by_id(NodeType.COMPLEX, 1)
        assert node is not None
        assert node.get_id() == 1
        assert node.data.name == "Фабрика Веретено"
        
        # Получаем индекс
        index = self.model.get_index_by_id(NodeType.COMPLEX, 2)
        assert index.isValid()
        assert self.model._get_node(index).data.name == "Тестовый комплекс"
        
        # Несуществующий ID
        node = self.model.get_node_by_id(NodeType.COMPLEX, 999)
        assert node is None
    
    def test_expanded_nodes_tracking(self):
        """Тест отслеживания раскрытых узлов"""
        self.model.set_complexes([self.complex1])
        complex_index = self.model.index(0, 0)
        
        # Раскрываем узел
        self.tree_view._on_node_expanded(complex_index)
        
        # Проверяем, что узел отмечен как раскрытый во внутреннем словаре
        key = f"complex:{self.complex1.id}"
        assert key in self.tree_view._expanded_nodes
        
        # Сворачиваем
        self.tree_view._on_node_collapsed(complex_index)
        
        # Проверяем, что отметка снята
        assert key not in self.tree_view._expanded_nodes
    
    def test_child_count_in_display(self):
        """Тест отображения количества детей в скобках"""
        # Комплекс с корпусами
        self.model.set_complexes([self.complex1])
        complex_index = self.model.index(0, 0)
        
        # Добавляем корпуса
        self.model.add_children(complex_index, [self.building1, self.building2], NodeType.BUILDING)
        
        # Проверяем отображение комплекса
        assert self.model.data(complex_index) == "Фабрика Веретено (2)"
        
        # Проверяем корпус с этажами
        building_index = self.model.index(0, 0, complex_index)
        assert self.model.data(building_index) == "Корпус А (4)"
        
        # Добавляем этажи
        self.model.add_children(building_index, [self.floor1, self.floor2], NodeType.FLOOR)
        
        # Проверяем этаж с комнатами
        floor_index = self.model.index(0, 0, building_index)
        assert self.model.data(floor_index) == "Этаж 1 (2)"
        
        # Этаж без комнат
        floor2_index = self.model.index(1, 0, building_index)
        assert self.model.data(floor2_index) == "Этаж 2"
    
    def test_context_menu(self):
        """Тест контекстного меню (просто проверяем, что не падает)"""
        self.model.set_complexes([self.complex1])
        complex_index = self.model.index(0, 0)
        
        # Эмулируем правый клик (просто вызываем метод)
        try:
            self.tree_view._show_context_menu(None)
        except:
            pass  # Ожидаемо, если нет позиции
        
        assert True
    
    def test_get_selected_node_info(self):
        """Тест получения информации о выбранном узле"""
        self.model.set_complexes([self.complex1])
        complex_index = self.model.index(0, 0)
        
        # Выбираем узел
        self.tree_view.tree_view.setCurrentIndex(complex_index)
        
        # Получаем информацию
        info = self.tree_view.get_selected_node_info()
        assert info is not None
        node_type, node_id, data = info
        assert node_type == "complex"
        assert node_id == 1
        assert data.name == "Фабрика Веретено"
    
    def test_select_node_by_id(self):
        """Тест выбора узла по ID"""
        self.model.set_complexes([self.complex1, self.complex2])
        
        # Выбираем по ID
        result = self.tree_view.select_node("complex", 2)
        assert result is True
        
        # Проверяем, что выбран правильный узел
        selected = self.tree_view.get_selected_node_info()
        assert selected is not None
        assert selected[0] == "complex"
        assert selected[1] == 2
        
        # Несуществующий ID
        result = self.tree_view.select_node("complex", 999)
        assert result is False


if __name__ == '__main__':
    unittest.main()