# tests/test_details_panel_integration.py
"""
Интеграционные тесты для DetailsPanel
Симулируем реальное поведение пользователя и проверяем получаемые данные
"""
import sys
import os
import unittest
from typing import List, Dict, Any
from datetime import datetime

sys.path.append('/app')

# === ПОДАВЛЕНИЕ QT ЛОГОВ ===
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.core.*=false"
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # Для CI/CD, если нужно

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt
from PySide6.QtCore import qInstallMessageHandler, QtMsgType
import logging

# Свой обработчик сообщений Qt, который игнорирует всё кроме критических ошибок
def qt_message_handler(mode, context, message):
    # Полностью игнорируем все Qt сообщения
    pass

# Устанавливаем обработчик ДО создания QApplication
qInstallMessageHandler(qt_message_handler)

# Настраиваем логирование Python
logging.basicConfig(level=logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# === КОНЕЦ ПОДАВЛЕНИЯ ЛОГОВ ===

from src.ui.main_window import MainWindow
from src.ui.tree_view import TreeView
from src.ui.details_panel import DetailsPanel
from src.core.api_client import ApiClient
from src.core.cache import DataCache
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class TestDetailsPanelIntegration(unittest.TestCase):
    """Интеграционные тесты для DetailsPanel с реальными запросами к API"""
    
    @classmethod
    def setUpClass(cls):
        """Создаём QApplication один раз для всех тестов"""
        if not QApplication.instance():
            cls.app = QApplication([])
    
    def setUp(self):
        """Подготовка перед каждым тестом"""
        # Создаём реальный API клиент (будет обращаться к настоящему бекенду)
        self.api_client = ApiClient()
        
        # Создаём главное окно (оно создаст всё остальное)
        self.window = MainWindow()
        self.tree_view = self.window.tree_view
        self.details_panel = self.window.details_panel
        
        # Флаг для отслеживания завершения асинхронных операций
        self.test_complete = False
        self.current_step = 0
        self.test_results = []
        
        print("\n" + "="*80)
        print("🧪 ЗАПУСК ИНТЕГРАЦИОННОГО ТЕСТА DETAILS PANEL")
        print("="*80)
    
    def tearDown(self):
        """Очистка после теста"""
        self.window.close()
    
    def log_result(self, step: str, data: Any, source: str):
        """Логирование результата теста"""
        result = {
            'step': step,
            'data': data,
            'source': source,
            'timestamp': datetime.now().strftime("%H:%M:%S.%f")[:-3]
        }
        self.test_results.append(result)
        
        # Выводим в консоль
        print(f"\n[{result['timestamp']}] 📍 Шаг {len(self.test_results)}: {step}")
        print(f"   📦 Источник: {source}")
        if data:
            if hasattr(data, '__dict__'):
                # Для объектов моделей
                attrs = {k: v for k, v in data.__dict__.items() 
                        if not k.startswith('_') and v is not None}
                print(f"   📊 Данные: {attrs}")
            else:
                print(f"   📊 Данные: {data}")
    
    def run_user_scenario(self):
        """
        Симуляция действий пользователя:
        1. Загрузить комплексы
        2. Выбрать первый комплекс
        3. Раскрыть комплекс
        4. Выбрать корпус Б
        5. Раскрыть корпус Б
        6. Выбрать первый этаж корпуса Б
        7. Раскрыть первый этаж
        8. Выбрать второе помещение (если есть)
        9. Вернуться к подвалу (если есть)
        """
        print("\n🚀 Начинаем симуляцию пользователя...")
        
        # Шаг 1: Загрузка комплексов (происходит автоматически при создании)
        QTimer.singleShot(500, self._step_1_check_complexes)
    
    def _step_1_check_complexes(self):
        """Шаг 1: Проверка загрузки комплексов"""
        complexes = self.tree_view.model._root_node.children
        source = "cache" if self.tree_view.cache.get("complexes:all") else "api"
        
        self.log_result(
            "Загрузка комплексов",
            [f"{c.data.name} (корпусов: {c.data.buildings_count})" for c in complexes],
            source
        )
        
        # Проверяем, что комплексы загружены
        self.assertGreater(len(complexes), 0, "Комплексы не загрузились")
        
        # Шаг 2: Выбираем первый комплекс
        first_complex = complexes[0]
        complex_index = self.tree_view.model.index(0, 0)
        self.tree_view.tree_view.setCurrentIndex(complex_index)
        
        # Даём время на обновление DetailsPanel
        QTimer.singleShot(500, self._step_2_check_complex_details)
    
    def _step_2_check_complex_details(self):
        """Шаг 2: Проверка отображения деталей комплекса"""
        current_type, current_id, current_data = self.details_panel.get_current_selection()
        
        self.log_result(
            f"Детали комплекса #{current_id}",
            current_data,
            "details_panel (из сигнала tree_view)"
        )
        
        # Проверяем, что данные комплекса отображаются
        self.assertEqual(current_type, "complex")
        self.assertIsNotNone(current_data)
        self.assertTrue(hasattr(current_data, 'name'))
        
        # Проверяем обработку отсутствующих данных
        if hasattr(current_data, 'address'):
            self.log_result(
                "Поле address комплекса",
                current_data.address or "ОТСУТСТВУЕТ",
                "модель данных"
            )
        
        # Шаг 3: Раскрываем комплекс
        complex_index = self.tree_view.model.index(0, 0)
        self.tree_view.tree_view.expand(complex_index)
        
        # Даём время на загрузку корпусов
        QTimer.singleShot(1000, self._step_3_check_buildings)
    
    def _step_3_check_buildings(self):
        """Шаг 3: Проверка загрузки корпусов"""
        complex_index = self.tree_view.model.index(0, 0)
        buildings_count = self.tree_view.model.rowCount(complex_index)
        
        # Проверяем источник данных для корпусов
        cache_key = "complex:1:buildings"
        source = "cache" if self.tree_view.cache.get(cache_key) else "api"
        
        self.log_result(
            f"Загрузка корпусов комплекса (найдено: {buildings_count})",
            f"Кэш-ключ: {cache_key}",
            source
        )
        
        self.assertGreater(buildings_count, 0, "Корпуса не загрузились")
        
        # Ищем корпус Б (building_id = 4)
        building_b_index = None
        for row in range(buildings_count):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 4:  # Корпус Б
                building_b_index = idx
                break
        
        if building_b_index:
            # Шаг 4: Выбираем корпус Б
            self.tree_view.tree_view.setCurrentIndex(building_b_index)
            QTimer.singleShot(500, self._step_4_check_building_details)
        else:
            print("⚠️ Корпус Б не найден, пропускаем шаги с ним")
            self.test_complete = True
    
    def _step_4_check_building_details(self):
        """Шаг 4: Проверка отображения деталей корпуса"""
        current_type, current_id, current_data = self.details_panel.get_current_selection()
        
        self.log_result(
            f"Детали корпуса #{current_id}",
            current_data,
            "details_panel"
        )
        
        self.assertEqual(current_type, "building")
        self.assertIsNotNone(current_data)
        
        # Проверяем поля корпуса
        fields_to_check = ['name', 'floors_count', 'description', 'address']
        for field in fields_to_check:
            if hasattr(current_data, field):
                value = getattr(current_data, field)
                self.log_result(
                    f"Поле {field} корпуса",
                    value if value is not None else "ОТСУТСТВУЕТ",
                    "модель данных"
                )
        
        # Шаг 5: Раскрываем корпус Б
        complex_index = self.tree_view.model.index(0, 0)
        for row in range(self.tree_view.model.rowCount(complex_index)):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 4:
                self.tree_view.tree_view.expand(idx)
                break
        
        # Даём время на загрузку этажей
        QTimer.singleShot(1000, self._step_5_check_floors)
    
    def _step_5_check_floors(self):
        """Шаг 5: Проверка загрузки этажей корпуса Б"""
        # Находим индекс корпуса Б
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
            cache_key = f"building:4:floors"
            source = "cache" if self.tree_view.cache.get(cache_key) else "api"
            
            self.log_result(
                f"Загрузка этажей корпуса Б (найдено: {floors_count})",
                f"Кэш-ключ: {cache_key}",
                source
            )
            
            # Шаг 6: Выбираем первый этаж
            if floors_count > 0:
                first_floor_idx = self.tree_view.model.index(0, 0, building_b_index)
                self.tree_view.tree_view.setCurrentIndex(first_floor_idx)
                QTimer.singleShot(500, self._step_6_check_floor_details)
            else:
                print("⚠️ Нет этажей в корпусе Б")
                self._step_9_check_basement()
    
    def _step_6_check_floor_details(self):
        """Шаг 6: Проверка отображения деталей этажа"""
        current_type, current_id, current_data = self.details_panel.get_current_selection()
        
        self.log_result(
            f"Детали этажа #{current_id}",
            current_data,
            "details_panel"
        )
        
        self.assertEqual(current_type, "floor")
        self.assertIsNotNone(current_data)
        
        # Проверяем поля этажа
        fields_to_check = ['number', 'rooms_count', 'description']
        for field in fields_to_check:
            if hasattr(current_data, field):
                value = getattr(current_data, field)
                self.log_result(
                    f"Поле {field} этажа",
                    value if value is not None else "ОТСУТСТВУЕТ",
                    "модель данных"
                )
        
        # Шаг 7: Раскрываем этаж
        complex_index = self.tree_view.model.index(0, 0)
        building_b_index = None
        for row in range(self.tree_view.model.rowCount(complex_index)):
            idx = self.tree_view.model.index(row, 0, complex_index)
            node = self.tree_view.model._get_node(idx)
            if node and node.data.id == 4:
                building_b_index = idx
                break
        
        if building_b_index and self.tree_view.model.rowCount(building_b_index) > 0:
            first_floor_idx = self.tree_view.model.index(0, 0, building_b_index)
            self.tree_view.tree_view.expand(first_floor_idx)
            
            # Даём время на загрузку помещений
            QTimer.singleShot(1000, self._step_7_check_rooms)
    
    def _step_7_check_rooms(self):
        """Шаг 7: Проверка загрузки помещений этажа"""
        # Находим первый этаж корпуса Б
        complex_index = self.tree_view.model.index(0, 0)
        for row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(row, 0, complex_index)
            building_node = self.tree_view.model._get_node(building_idx)
            if building_node and building_node.data.id == 4:
                if self.tree_view.model.rowCount(building_idx) > 0:
                    floor_idx = self.tree_view.model.index(0, 0, building_idx)
                    floor_node = self.tree_view.model._get_node(floor_idx)
                    
                    if floor_node:
                        rooms_count = self.tree_view.model.rowCount(floor_idx)
                        cache_key = f"floor:{floor_node.data.id}:rooms"
                        source = "cache" if self.tree_view.cache.get(cache_key) else "api"
                        
                        self.log_result(
                            f"Загрузка помещений этажа {floor_node.data.number} (найдено: {rooms_count})",
                            f"Кэш-ключ: {cache_key}",
                            source
                        )
                        
                        # Шаг 8: Выбираем второе помещение (если есть)
                        if rooms_count >= 2:
                            second_room_idx = self.tree_view.model.index(1, 0, floor_idx)
                            self.tree_view.tree_view.setCurrentIndex(second_room_idx)
                            QTimer.singleShot(500, self._step_8_check_room_details)
                        elif rooms_count > 0:
                            # Если есть хотя бы одно помещение
                            first_room_idx = self.tree_view.model.index(0, 0, floor_idx)
                            self.tree_view.tree_view.setCurrentIndex(first_room_idx)
                            QTimer.singleShot(500, self._step_8_check_room_details)
                        else:
                            print("⚠️ Нет помещений на этаже")
                            self._step_9_check_basement()
    
    def _step_8_check_room_details(self):
        """Шаг 8: Проверка отображения деталей помещения"""
        current_type, current_id, current_data = self.details_panel.get_current_selection()
        
        self.log_result(
            f"Детали помещения #{current_id}",
            current_data,
            "details_panel"
        )
        
        self.assertEqual(current_type, "room")
        self.assertIsNotNone(current_data)
        
        # Проверяем поля помещения
        fields_to_check = ['number', 'area', 'status_code', 'description', 'max_tenants']
        for field in fields_to_check:
            if hasattr(current_data, field):
                value = getattr(current_data, field)
                self.log_result(
                    f"Поле {field} помещения",
                    value if value is not None else "ОТСУТСТВУЕТ",
                    "модель данных"
                )
        
        # Шаг 9: Возвращаемся к подвалу (если есть)
        self._step_9_check_basement()
    
    def _step_9_check_basement(self):
        """Шаг 9: Поиск и проверка подвала"""
        print("\n🔍 Поиск подвальных этажей...")
        
        # Ищем этажи с отрицательными номерами
        complex_index = self.tree_view.model.index(0, 0)
        basements_found = []
        
        for building_row in range(self.tree_view.model.rowCount(complex_index)):
            building_idx = self.tree_view.model.index(building_row, 0, complex_index)
            if self.tree_view.model.hasChildren(building_idx):
                for floor_row in range(self.tree_view.model.rowCount(building_idx)):
                    floor_idx = self.tree_view.model.index(floor_row, 0, building_idx)
                    floor_node = self.tree_view.model._get_node(floor_idx)
                    if floor_node and floor_node.data and floor_node.data.number < 0:
                        basements_found.append(floor_node.data)
        
        if basements_found:
            for basement in basements_found:
                self.log_result(
                    f"Найден подвал в корпусе {basement.building_id}",
                    f"Этаж {basement.number} (помещений: {basement.rooms_count})",
                    "модель данных"
                )
        else:
            self.log_result(
                "Поиск подвалов",
                "Подвальные этажи не найдены",
                "база данных"
            )
        
        # Завершаем тест
        self._finish_test()
    
    def _finish_test(self):
        """Завершение теста и вывод статистики"""
        self.test_complete = True
        
        print("\n" + "="*80)
        print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
        print("="*80)
        
        # Анализ источников данных
        cache_hits = sum(1 for r in self.test_results if r['source'] == 'cache')
        api_calls = sum(1 for r in self.test_results if r['source'] == 'api')
        panel_calls = sum(1 for r in self.test_results if r['source'] == 'details_panel')
        
        print(f"\n📦 Источники данных:")
        print(f"  • Из кэша: {cache_hits}")
        print(f"  • Из API: {api_calls}")
        print(f"  • Из DetailsPanel: {panel_calls}")
        
        # Анализ отсутствующих данных
        missing_data = [r for r in self.test_results 
                       if isinstance(r['data'], str) and 'ОТСУТСТВУЕТ' in r['data']]
        
        if missing_data:
            print(f"\n⚠️ Отсутствующие данные:")
            for r in missing_data:
                print(f"  • {r['step']}: {r['data']}")
        else:
            print(f"\n✅ Все запрошенные поля присутствуют в моделях")
        
        print("\n📋 Детальный лог:")
        for r in self.test_results:
            print(f"  [{r['timestamp']}] {r['step']}")
        
        print("\n✅ Тест завершён")
        QApplication.quit()
    
    def test_user_scenario(self):
        """Запуск пользовательского сценария"""
        # Запускаем симуляцию
        self.run_user_scenario()
        
        # Ждём завершения всех асинхронных операций
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)
        
        # Запускаем event loop
        self.app.exec()
        
        # Проверяем, что тест выполнился
        self.assertTrue(self.test_complete, "Тест не завершился")


if __name__ == '__main__':
    unittest.main()