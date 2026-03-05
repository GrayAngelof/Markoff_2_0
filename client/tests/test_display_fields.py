# tests/test_display_fields.py
"""
Тест для проверки корректности отображаемых полей для каждого типа объекта
"""
import sys
import os
import unittest
from typing import List, Dict, Any, Set
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


class TestDisplayFields(unittest.TestCase):
    """
    Тест проверяет, какие поля отображаются для каждого типа объекта
    """
    
    @classmethod
    def setUpClass(cls):
        """Создаём QApplication один раз для всех тестов"""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.api_client = ApiClient()
        self.window = MainWindow()
        self.window.show()  # <-- Явно показываем окно
        self.tree_view = self.window.tree_view
        self.details_panel = self.window.details_panel
        
        self.test_complete = False
        self.test_results = []
        
        print("\n" + "="*80)
        print("🧪 ТЕСТ ОТОБРАЖЕНИЯ ПОЛЕЙ")
        print("="*80)
    
    def tearDown(self):
        """Очистка после теста"""
        self.window.close()
    
    def get_visible_fields(self, panel: DetailsPanel) -> Set[str]:
        """
        Получить множество действительно видимых полей
        
        Returns:
            Set[str]: ключи полей, которые реально видны пользователю
        """
        # Используем новый метод info_grid для получения видимых полей
        visible = set(panel.info_grid.get_visible_fields())
        
        # Для отладки выводим, что получили
        print(f"🔍 Тест получил видимые поля: {sorted(visible)}")
        
        return visible
    
    def log_fields(self, obj_type: str, visible: Set[str], expected: Set[str]):
        """Логирование результатов"""
        print(f"\n📋 {obj_type.upper()}:")
        print(f"  Видимые поля: {sorted(visible)}")
        print(f"  Ожидаемые:    {sorted(expected)}")
        
        # Проверяем соответствие
        if visible == expected:
            print(f"  ✅ CORRECT")
        else:
            missing = expected - visible
            extra = visible - expected
            if missing:
                print(f"  ❌ MISSING: {sorted(missing)}")
            if extra:
                print(f"  ❌ EXTRA: {sorted(extra)}")
        
        self.test_results.append({
            'type': obj_type,
            'visible': visible,
            'expected': expected,
            'passed': visible == expected
        })
    
    def run_test_scenario(self):
        """Запуск тестового сценария"""
        print("\n🚀 Запуск теста отображения полей...")
        # Даём время на полную инициализацию и отображение окна
        QTimer.singleShot(1000, self._step_1_check_complex)
    
    def _step_1_check_complex(self):
        """Шаг 1: Проверка отображения комплекса"""
        # Проверяем, что окно действительно видимо
        if not self.window.isVisible():
            print("⚠️ Окно ещё не видимо, ждём ещё...")
            QTimer.singleShot(500, self._step_1_check_complex)
            return
        
        print("✅ Окно видимо, начинаем тест")
        # Выбираем первый комплекс
        complex_index = self.tree_view.model.index(0, 0)
        self.tree_view.tree_view.setCurrentIndex(complex_index)
        
        # Даём время на загрузку
        QTimer.singleShot(1000, self._step_2_verify_complex)
    
    def _step_2_verify_complex(self):
        """Проверка комплекса"""
        visible = self.get_visible_fields(self.details_panel)
        expected = {"address", "owner", "description", "plan"}
        self.log_fields("complex", visible, expected)
        
        # Переходим к корпусу
        QTimer.singleShot(500, self._step_3_find_building)
    
    def _step_3_find_building(self):
        """Поиск корпуса Б"""
        complex_index = self.tree_view.model.index(0, 0)
        self.tree_view.tree_view.expand(complex_index)
        
        QTimer.singleShot(1000, self._step_4_check_building)
    
    def _step_4_check_building(self):
        """Шаг 4: Проверка корпуса Б"""
        complex_index = self.tree_view.model.index(0, 0)
        
        # Ищем корпус Б
        for row in range(self.tree_view.model.rowCount(complex_index)):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 4:  # Корпус Б
                self.tree_view.tree_view.setCurrentIndex(idx)
                break
        
        QTimer.singleShot(1000, self._step_5_verify_building)
    
    def _step_5_verify_building(self):
        """Проверка корпуса"""
        visible = self.get_visible_fields(self.details_panel)
        expected = {"address", "description", "plan"}
        self.log_fields("building", visible, expected)
        
        # Переходим к подвалу
        QTimer.singleShot(500, self._step_6_find_basement)
    
    def _step_6_find_basement(self):
        """Поиск подвала"""
        complex_index = self.tree_view.model.index(0, 0)
        
        # Находим корпус Б и раскрываем его
        for row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(row, 0, complex_index)
            building_node = self.tree_view.model._get_node(building_idx)
            if building_node and building_node.data.id == 4:
                self.tree_view.tree_view.expand(building_idx)
                break
        
        QTimer.singleShot(1000, self._step_7_check_floor)
    
    def _step_7_check_floor(self):
        """Шаг 7: Проверка подвала"""
        complex_index = self.tree_view.model.index(0, 0)
        
        # Находим подвал
        for row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(row, 0, complex_index)
            building_node = self.tree_view.model._get_node(building_idx)
            if building_node and building_node.data.id == 4:
                for floor_row in range(self.tree_view.model.rowCount(building_idx)):
                    floor_idx = self.tree_view.model.index(floor_row, 0, building_idx)
                    floor_node = self.tree_view.model._get_node(floor_idx)
                    if floor_node and floor_node.data.number == -1:  # Подвал
                        self.tree_view.tree_view.setCurrentIndex(floor_idx)
                        break
        
        QTimer.singleShot(1000, self._step_8_verify_floor)
    
    def _step_8_verify_floor(self):
        """Проверка этажа"""
        visible = self.get_visible_fields(self.details_panel)
        expected = {"description", "plan", "type"}
        self.log_fields("floor", visible, expected)
        
        # Переходим к помещению
        QTimer.singleShot(500, self._step_9_find_room)
    
    def _step_9_find_room(self):
        """Поиск помещения"""
        complex_index = self.tree_view.model.index(0, 0)
        
        # Раскрываем подвал
        for row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(row, 0, complex_index)
            building_node = self.tree_view.model._get_node(building_idx)
            if building_node and building_node.data.id == 4:
                for floor_row in range(self.tree_view.model.rowCount(building_idx)):
                    floor_idx = self.tree_view.model.index(floor_row, 0, building_idx)
                    floor_node = self.tree_view.model._get_node(floor_idx)
                    if floor_node and floor_node.data.number == -1:
                        self.tree_view.tree_view.expand(floor_idx)
                        break
        
        QTimer.singleShot(1000, self._step_10_check_room)
    
    def _step_10_check_room(self):
        """Шаг 10: Проверка помещения"""
        complex_index = self.tree_view.model.index(0, 0)
        
        # Находим помещение
        for row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(row, 0, complex_index)
            building_node = self.tree_view.model._get_node(building_idx)
            if building_node and building_node.data.id == 4:
                for floor_row in range(self.tree_view.model.rowCount(building_idx)):
                    floor_idx = self.tree_view.model.index(floor_row, 0, building_idx)
                    floor_node = self.tree_view.model._get_node(floor_idx)
                    if floor_node and floor_node.data.number == -1:
                        if self.tree_view.model.rowCount(floor_idx) > 0:
                            room_idx = self.tree_view.model.index(0, 0, floor_idx)
                            self.tree_view.tree_view.setCurrentIndex(room_idx)
                            break
        
        QTimer.singleShot(1000, self._step_11_verify_occupied_room)
    
    def _step_11_verify_occupied_room(self):
        """Проверка занятого помещения"""
        visible = self.get_visible_fields(self.details_panel)
        expected = {"address", "type", "description", "plan", 
                   "tenant", "contract", "valid_until", "rent"}
        self.log_fields("occupied_room", visible, expected)
        
        self._step_12_finish()
    
    def _step_12_finish(self):
        """Завершение теста"""
        self.test_complete = True
        
        print("\n" + "="*80)
        print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
        print("="*80)
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        for r in self.test_results:
            status = "✅" if r['passed'] else "❌"
            print(f"\n{status} {r['type']}:")
            print(f"   Видимые: {sorted(r['visible'])}")
            print(f"   Ожидаемые: {sorted(r['expected'])}")
        
        print(f"\n📊 Результат: {passed}/{total} тестов пройдено")
        
        QApplication.quit()
    
    def test_display_fields(self):
        """Запуск теста"""
        self.run_test_scenario()
        
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)
        
        self.app.exec()
        
        self.assertTrue(self.test_complete, "Тест не завершился")


if __name__ == '__main__':
    unittest.main()