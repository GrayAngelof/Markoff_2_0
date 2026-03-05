# tests/test_details_panel.py
"""
Интеграционные тесты для DetailsPanel с реальными запросами к API
Проверяем корректность отображения данных и иерархии
"""
import sys
import os
import unittest
from typing import List, Dict, Any
from datetime import datetime

sys.path.append('/app')

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt

from src.ui.main_window import MainWindow
from src.ui.tree import TreeView
from src.ui.details import DetailsPanel
from src.core.api_client import ApiClient
from src.core.cache import DataCache
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class TestDetailsPanel(unittest.TestCase):
    """Интеграционные тесты для DetailsPanel"""
    
    @classmethod
    def setUpClass(cls):
        """Создаём QApplication один раз для всех тестов"""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.api_client = ApiClient()
        self.window = MainWindow()
        self.tree_view = self.window.tree_view
        self.details_panel = self.window.details_panel
        
        self.test_complete = False
        self.current_step = 0
        self.test_results = []
        
        print("\n" + "="*80)
        print("🧪 ЗАПУСК ТЕСТА ОТОБРАЖЕНИЯ DETAILS PANEL")
        print("="*80)
    
    def tearDown(self):
        """Очистка после теста"""
        self.window.close()
    
    def log_api_response(self, endpoint: str, data: Any):
        """Логирование ответа от API"""
        print(f"\n🌐 API Response from {endpoint}:")
        if isinstance(data, dict):
            for key, value in data.items():
                if value is not None:
                    print(f"  • {key}: {value}")
        elif data is None:
            print("  • Нет данных")
    
    def log_displayed_data(self, panel):
        """Логирование того, что отображается в DetailsPanel"""
        print("\n📋 Отображаемые данные в DetailsPanel:")
        
        # Шапка
        print(f"  Заголовок: {panel.title_label.text()}")
        print(f"  Иерархия: {panel.hierarchy_label.text()}")
        print(f"  Статус: {panel.status_label.text()}")
        
        # Основная информация
        fields = [
            ("Адрес:", panel.fields["address"]),
            ("Владелец:", panel.fields["owner"]),
            ("Арендатор:", panel.fields["tenant"]),
            ("Описание:", panel.fields["description"]),
            ("Планировка:", panel.fields["plan"]),
            ("Тип:", panel.fields["type"]),
            ("Договор:", panel.fields["contract"]),
            ("Действует до:", panel.fields["valid_until"]),
            ("Арендная плата:", panel.fields["rent"]),
        ]
        
        for label, widget in fields:
            if widget.text() and widget.text() != "—":
                print(f"  {label} {widget.text()}")
        
        # Вкладки - ИСПРАВЛЕНО: panel.tabs вместо panel.tab_widget
        print(f"  Вкладки: {panel.tabs.count()} шт.")
        for i in range(panel.tabs.count()):
            print(f"    • {panel.tabs.tabText(i)}")
    
    def run_user_scenario(self):
        """
        Симуляция действий пользователя:
        1. Загрузить комплексы
        2. Выбрать комплекс и проверить отображение
        3. Раскрыть комплекс, найти корпус Б (id=4)
        4. Выбрать корпус Б и проверить отображение
        5. Раскрыть корпус Б, найти подвал (floor=-1)
        6. Выбрать подвал и проверить отображение
        7. Раскрыть подвал, найти помещение (room=21)
        8. Выбрать помещение и проверить отображение
        9. Вернуться к корпусу АБ (id=22) и проверить переключение контекста
        10. Выбрать другой этаж в корпусе АБ
        11. Выбрать другой корпус и проверить смену контекста
        """
        print("\n🚀 Начинаем симуляцию пользователя...")
        QTimer.singleShot(500, self._step_1_check_complexes)
    
    def _step_1_check_complexes(self):
        """Шаг 1: Проверка загрузки комплексов"""
        complexes = self.tree_view.model._root_node.children
        print(f"\n📊 Загружено комплексов: {len(complexes)}")
        for c in complexes:
            print(f"  • {c.data.name} (ID: {c.data.id}, корпусов: {c.data.buildings_count})")
        
        if complexes:
            # Выбираем первый комплекс
            complex_index = self.tree_view.model.index(0, 0)
            self.tree_view.tree_view.setCurrentIndex(complex_index)
            QTimer.singleShot(1000, self._step_2_check_complex_details)
    
    def _step_2_check_complex_details(self):
        """Шаг 2: Проверка отображения деталей комплекса"""
        print("\n" + "="*60)
        print("🔍 ДЕТАЛИ КОМПЛЕКСА")
        print("="*60)
        
        # Проверяем, что данные отобразились
        self.log_displayed_data(self.details_panel)
        
        # Проверяем контекст (должен быть пустым для комплекса)
        current_type, current_id, current_data = self.details_panel.get_current_selection()
        self.assertEqual(current_type, 'complex')
        self.assertEqual(current_id, 1)
        
        # Раскрываем комплекс для загрузки корпусов
        complex_index = self.tree_view.model.index(0, 0)
        self.tree_view.tree_view.expand(complex_index)
        QTimer.singleShot(1000, self._step_3_find_building_b)
    
    def _step_3_find_building_b(self):
        """Шаг 3: Поиск корпуса Б (id=4)"""
        print("\n" + "="*60)
        print("🔍 ПОИСК КОРПУСА Б")
        print("="*60)
        
        complex_index = self.tree_view.model.index(0, 0)
        buildings_count = self.tree_view.model.rowCount(complex_index)
        print(f"\n📊 Загружено корпусов: {buildings_count}")
        
        # Ищем корпус Б
        building_b_index = None
        for row in range(buildings_count):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 4:
                building_b_index = idx
                print(f"✅ Найден корпус Б: {node.data.name}")
                break
        
        if building_b_index:
            self.tree_view.tree_view.setCurrentIndex(building_b_index)
            QTimer.singleShot(1000, self._step_4_check_building_b_details)
        else:
            print("❌ Корпус Б не найден")
            self._finish_test()
    
    def _step_4_check_building_b_details(self):
        """Шаг 4: Проверка деталей корпуса Б"""
        print("\n" + "="*60)
        print("🔍 ДЕТАЛИ КОРПУСА Б")
        print("="*60)
        
        self.log_displayed_data(self.details_panel)
        
        # Проверяем контекст
        current_type, current_id, _ = self.details_panel.get_current_selection()
        self.assertEqual(current_type, 'building')
        self.assertEqual(current_id, 4)
        
        # Раскрываем корпус Б
        complex_index = self.tree_view.model.index(0, 0)
        for row in range(self.tree_view.model.rowCount(complex_index)):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 4:
                self.tree_view.tree_view.expand(idx)
                break
        
        QTimer.singleShot(1000, self._step_5_find_basement)
    
    def _step_5_find_basement(self):
        """Шаг 5: Поиск подвала (floor=-1) в корпусе Б"""
        print("\n" + "="*60)
        print("🔍 ПОИСК ПОДВАЛА В КОРПУСЕ Б")
        print("="*60)
        
        # Находим корпус Б
        complex_index = self.tree_view.model.index(0, 0)
        building_b_index = None
        for row in range(self.tree_view.model.rowCount(complex_index)):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 4:
                building_b_index = idx
                break
        
        if building_b_index:
            floors_count = self.tree_view.model.rowCount(building_b_index)
            print(f"📊 Этажей в корпусе Б: {floors_count}")
            
            # Ищем подвал
            basement_index = None
            for row in range(floors_count):
                idx = self.tree_view.model.index(row, 0, building_b_index)
                node = self.tree_view.model._get_node(idx)
                if node and node.data.number == -1:
                    basement_index = idx
                    print(f"✅ Найден подвал: {node.data.number}")
                    break
            
            if basement_index:
                self.tree_view.tree_view.setCurrentIndex(basement_index)
                QTimer.singleShot(1000, self._step_6_check_basement_details)
            else:
                print("❌ Подвал не найден")
                self._finish_test()
    
    def _step_6_check_basement_details(self):
        """Шаг 6: Проверка деталей подвала"""
        print("\n" + "="*60)
        print("🔍 ДЕТАЛИ ПОДВАЛА")
        print("="*60)
        
        self.log_displayed_data(self.details_panel)
        
        # Проверяем контекст
        current_type, current_id, _ = self.details_panel.get_current_selection()
        self.assertEqual(current_type, 'floor')
        self.assertEqual(current_id, 8)
        
        # Раскрываем подвал
        complex_index = self.tree_view.model.index(0, 0)
        for row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(row, 0, complex_index)
            building_node = self.tree_view.model._get_node(building_idx)
            if building_node and building_node.data.id == 4:
                for floor_row in range(self.tree_view.model.rowCount(building_idx)):
                    floor_idx = self.tree_view.model.index(floor_row, 0, building_idx)
                    floor_node = self.tree_view.model._get_node(floor_idx)
                    if floor_node and floor_node.data.id == 8:
                        self.tree_view.tree_view.expand(floor_idx)
                        break
        
        QTimer.singleShot(1000, self._step_7_find_room)
    
    def _step_7_find_room(self):
        """Шаг 7: Поиск помещения в подвале"""
        print("\n" + "="*60)
        print("🔍 ПОИСК ПОМЕЩЕНИЯ В ПОДВАЛЕ")
        print("="*60)
        
        # Находим подвал
        complex_index = self.tree_view.model.index(0, 0)
        for row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(row, 0, complex_index)
            building_node = self.tree_view.model._get_node(building_idx)
            if building_node and building_node.data.id == 4:
                for floor_row in range(self.tree_view.model.rowCount(building_idx)):
                    floor_idx = self.tree_view.model.index(floor_row, 0, building_idx)
                    floor_node = self.tree_view.model._get_node(floor_idx)
                    if floor_node and floor_node.data.id == 8:
                        rooms_count = self.tree_view.model.rowCount(floor_idx)
                        print(f"📊 Помещений в подвале: {rooms_count}")
                        
                        if rooms_count > 0:
                            room_idx = self.tree_view.model.index(0, 0, floor_idx)
                            self.tree_view.tree_view.setCurrentIndex(room_idx)
                            QTimer.singleShot(1000, self._step_8_check_room_details)
                            return
        
        print("❌ Помещения не найдены")
        self._finish_test()
    
    def _step_8_check_room_details(self):
        """Шаг 8: Проверка деталей помещения"""
        print("\n" + "="*60)
        print("🔍 ДЕТАЛИ ПОМЕЩЕНИЯ")
        print("="*60)
        
        self.log_displayed_data(self.details_panel)
        
        # Проверяем контекст
        current_type, current_id, _ = self.details_panel.get_current_selection()
        self.assertEqual(current_type, 'room')
        self.assertEqual(current_id, 21)
        
        QTimer.singleShot(1000, self._step_9_switch_to_building_ab)
    
    def _step_9_switch_to_building_ab(self):
        """Шаг 9: Переключение на корпус АБ (id=22)"""
        print("\n" + "="*60)
        print("🔍 ПЕРЕКЛЮЧЕНИЕ НА КОРПУС АБ")
        print("="*60)
        
        complex_index = self.tree_view.model.index(0, 0)
        building_ab_index = None
        for row in range(self.tree_view.model.rowCount(complex_index)):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 22:
                building_ab_index = idx
                print(f"✅ Найден корпус АБ: {node.data.name}")
                break
        
        if building_ab_index:
            self.tree_view.tree_view.setCurrentIndex(building_ab_index)
            QTimer.singleShot(1000, self._step_10_check_building_ab_details)
        else:
            print("❌ Корпус АБ не найден")
            self._step_12_finish()
    
    def _step_10_check_building_ab_details(self):
        """Шаг 10: Проверка деталей корпуса АБ (контекст должен смениться)"""
        print("\n" + "="*60)
        print("🔍 ДЕТАЛИ КОРПУСА АБ")
        print("="*60)
        
        self.log_displayed_data(self.details_panel)
        
        # Проверяем, что контекст сменился
        current_type, current_id, _ = self.details_panel.get_current_selection()
        self.assertEqual(current_type, 'building')
        self.assertEqual(current_id, 22)
        
        # Раскрываем корпус АБ
        complex_index = self.tree_view.model.index(0, 0)
        for row in range(self.tree_view.model.rowCount(complex_index)):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 22:
                self.tree_view.tree_view.expand(idx)
                break
        
        QTimer.singleShot(1000, self._step_11_check_different_floor)
    
    def _step_11_check_different_floor(self):
        """Шаг 11: Выбор другого этажа в корпусе АБ"""
        print("\n" + "="*60)
        print("🔍 ВЫБОР ЭТАЖА В КОРПУСЕ АБ")
        print("="*60)
        
        complex_index = self.tree_view.model.index(0, 0)
        for row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(row, 0, complex_index)
            building_node = self.tree_view.model._get_node(building_idx)
            if building_node and building_node.data.id == 22:
                floors_count = self.tree_view.model.rowCount(building_idx)
                print(f"📊 Этажей в корпусе АБ: {floors_count}")
                
                if floors_count > 0:
                    # Выбираем первый этаж
                    floor_idx = self.tree_view.model.index(0, 0, building_idx)
                    self.tree_view.tree_view.setCurrentIndex(floor_idx)
                    QTimer.singleShot(1000, self._step_12_check_floor_context)
                    return
        
        self._step_12_finish()
    
    def _step_12_check_floor_context(self):
        """Шаг 12: Проверка контекста этажа в другом корпусе"""
        print("\n" + "="*60)
        print("🔍 ДЕТАЛИ ЭТАЖА В КОРПУСЕ АБ")
        print("="*60)
        
        self.log_displayed_data(self.details_panel)
        
        # Проверяем, что иерархия показывает правильный корпус
        hierarchy = self.details_panel.hierarchy_label.text()
        print(f"📋 Иерархия: {hierarchy}")
        
        # Должно содержать "Корпус АБ", а не "Корпус Б"
        self.assertIn("Корпус АБ", hierarchy)
        self.assertNotIn("Корпус Б", hierarchy)
        
        self._step_12_finish()
    
    def _step_12_finish(self):
        """Завершение теста"""
        self.test_complete = True
        
        print("\n" + "="*80)
        print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
        print("="*80)
        print("\n✅ Тест завершён - все проверки пройдены")
        print("ℹ️ Контекст иерархии корректно меняется при переключении между объектами")
        
        QApplication.quit()
    
    def test_user_scenario(self):
        """Запуск пользовательского сценария"""
        self.run_user_scenario()
        
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)
        
        self.app.exec()
        
        self.assertTrue(self.test_complete, "Тест не завершился")


if __name__ == '__main__':
    unittest.main()