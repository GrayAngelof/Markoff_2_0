# tests/client/core/bus/test_advanced_scenarios/test_cross_module_delivery.py
"""Тест доставки событий между модулями."""
import pytest
import sys
from unittest.mock import Mock, MagicMock
from types import ModuleType

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestCrossModuleDelivery:
    """Тестирует доставку событий между различными модулями."""

    def test_subscribe_in_one_module_emit_in_another(self):
        """Проверяет подписку в одном модуле и испускание в другом."""
        # Создаём имитацию разных модулей через простые классы
        class ModuleA:
            def __init__(self):
                self.called = False
                self.received_data = None
            
            def handler(self, event):
                self.called = True
                self.received_data = event['data']
        
        class ModuleB:
            def __init__(self):
                self.called = False
            
            def handler(self, event):
                self.called = True
        
        # Act
        event_bus = EventBus()
        module_a = ModuleA()
        module_b = ModuleB()
        
        # Подписка из module_a и module_b
        event_bus.subscribe('cross_module_event', module_a.handler)
        event_bus.subscribe('cross_module_event', module_b.handler)
        
        # Испускание (может быть из третьего модуля)
        test_data = {"key": "value"}
        event_bus.emit('cross_module_event', test_data)
        
        # Assert
        assert module_a.called, "Обработчик из module_a должен быть вызван"
        assert module_b.called, "Обработчик из module_b должен быть вызван"
        assert module_a.received_data == test_data, \
            "Данные должны корректно передаваться между модулями"

    def test_event_bus_as_global_singleton(self):
        """Проверяет использование глобальной шины событий."""
        # Создаём класс-синглтон для теста
        class TestEventBus(EventBus):
            _instance = None
            _initialized = False
            
            def __new__(cls):
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                return cls._instance
            
            def __init__(self):
                # Инициализируем только один раз
                if not self.__class__._initialized:
                    super().__init__()
                    self.__class__._initialized = True
        
        class ModuleA:
            def __init__(self):
                self.events = []
                self.bus = TestEventBus()
                self.bus.subscribe('global_event', self.on_event)
            
            def on_event(self, event):
                self.events.append(event)
        
        class ModuleB:
            def __init__(self):
                self.events = []
                self.bus = TestEventBus()
                self.bus.subscribe('global_event', self.on_event)
            
            def on_event(self, event):
                self.events.append(event)
        
        class ModuleC:
            def __init__(self):
                self.bus = TestEventBus()
            
            def do_something(self):
                self.bus.emit('global_event', {'from': 'module_c'})
        
        # Сбрасываем синглтон перед тестом
        TestEventBus._instance = None
        TestEventBus._initialized = False
        
        # Act
        module_a = ModuleA()
        module_b = ModuleB()
        module_c = ModuleC()
        
        module_c.do_something()
        
        # Assert
        assert len(module_a.events) == 1, "ModuleA должен получить событие"
        assert len(module_b.events) == 1, "ModuleB должен получить событие"
        assert module_a.events[0]['data']['from'] == 'module_c'

    def test_module_import_order_independence(self):
        """Проверяет независимость от порядка импорта модулей."""
        event_bus = EventBus()
        
        # Используем простые функции вместо модулей
        results = []
        
        # "Модуль X" подписывается первым
        def handler_x(event):
            results.append('X')
        
        event_bus.subscribe('order_test', handler_x)
        
        # "Модуль Y" подписывается вторым
        def handler_y(event):
            results.append('Y')
        
        event_bus.subscribe('order_test', handler_y)
        
        # "Модуль Z" подписывается третьим
        def handler_z(event):
            results.append('Z')
        
        event_bus.subscribe('order_test', handler_z)
        
        # Act
        event_bus.emit('order_test')
        
        # Assert
        assert results == ['X', 'Y', 'Z'], \
            "Порядок вызова должен соответствовать порядку подписки, а не импорта"

    def test_module_isolation(self):
        """Проверяет изоляцию обработчиков разных модулей."""
        event_bus = EventBus()
        
        # Модуль A (как класс)
        class ModuleA:
            def __init__(self):
                self.called = False
                event_bus.subscribe('test_event', self.on_event)
            
            def on_event(self, event):
                self.called = True
                # Модуль A не должен влиять на другие модули
                if event['data'].get('crash'):
                    raise ValueError("Ошибка в модуле A")
        
        # Модуль B (как класс)
        class ModuleB:
            def __init__(self):
                self.called = False
                event_bus.subscribe('test_event', self.on_event)
            
            def on_event(self, event):
                self.called = True
        
        # Act
        module_a = ModuleA()
        module_b = ModuleB()
        
        # Ошибка в модуле A не должна влиять на модуль B
        event_bus.emit('test_event', {'crash': True})
        
        # Assert
        assert module_a.called, "Модуль A должен быть вызван"
        assert module_b.called, "Модуль B должен быть вызван несмотря на ошибку в A"

    def test_real_module_import_simulation(self):
        """Проверяет симуляцию реальных импортов модулей через setattr."""
        event_bus = EventBus()
        
        # Создаём временный модуль
        test_module_name = 'test_dynamic_module'
        
        # Удаляем модуль если он уже существует
        if test_module_name in sys.modules:
            del sys.modules[test_module_name]
        
        # Создаём новый модуль
        test_module = ModuleType(test_module_name)
        
        # Добавляем атрибуты через setattr
        setattr(test_module, 'called', False)
        setattr(test_module, 'event_data', None)
        
        def module_handler(event):
            setattr(test_module, 'called', True)
            setattr(test_module, 'event_data', event['data'])
        
        setattr(test_module, 'handler', module_handler)
        
        # Регистрируем модуль
        sys.modules[test_module_name] = test_module
        
        # Подписываемся через импортированный модуль
        imported_module = sys.modules[test_module_name]
        event_bus.subscribe('module_event', imported_module.handler)
        
        # Испускаем событие
        event_bus.emit('module_event', {'test': True})
        
        # Assert - получаем значения через getattr
        assert getattr(imported_module, 'called'), "Обработчик из модуля должен быть вызван"
        assert getattr(imported_module, 'event_data') == {'test': True}
        
        # Очистка
        del sys.modules[test_module_name]