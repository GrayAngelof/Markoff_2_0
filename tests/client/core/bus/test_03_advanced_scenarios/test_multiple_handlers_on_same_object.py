# tests/client/core/bus/test_advanced_scenarios/test_multiple_handlers_on_same_object.py
"""Тест множественных обработчиков на одном объекте."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.event_constants import UIEvents, SystemEvents, HotkeyEvents, ProjectionEvents


class TestMultipleHandlersOnSameObject:
    """Тестирует объект с несколькими обработчиками для разных событий."""

    def test_object_with_multiple_handlers(self):
        """Проверяет объект, имеющий несколько методов-обработчиков."""
        # Arrange
        event_bus = EventBus()
        
        class ComplexComponent:
            def __init__(self):
                self.node_selected_called = False
                self.data_loaded_called = False
                self.hotkey_pressed_called = False
                self.tree_updated_called = False
                
                # Подписываемся на разные события
                event_bus.subscribe(UIEvents.NODE_SELECTED, self.on_node_selected)
                event_bus.subscribe(SystemEvents.DATA_LOADED, self.on_data_loaded)
                event_bus.subscribe(HotkeyEvents.REFRESH_CURRENT, self.on_refresh)
                event_bus.subscribe(ProjectionEvents.TREE_UPDATED, self.on_tree_updated)
            
            def on_node_selected(self, event):
                self.node_selected_called = True
                self.last_node = event['data'].get('node_id')
            
            def on_data_loaded(self, event):
                self.data_loaded_called = True
                self.last_data = event['data']
            
            def on_refresh(self, event):
                self.hotkey_pressed_called = True
            
            def on_tree_updated(self, event):
                self.tree_updated_called = True
                self.tree_data = event['data'].get('tree')
        
        # Act
        component = ComplexComponent()
        
        # Испускаем разные события
        event_bus.emit(UIEvents.NODE_SELECTED, {"node_id": 42})
        event_bus.emit(SystemEvents.DATA_LOADED, {"items": [1, 2, 3]})
        event_bus.emit(HotkeyEvents.REFRESH_CURRENT)
        event_bus.emit(ProjectionEvents.TREE_UPDATED, {"tree": ["root", "child"]})
        
        # Assert
        assert component.node_selected_called, "on_node_selected должен быть вызван"
        assert component.data_loaded_called, "on_data_loaded должен быть вызван"
        assert component.hotkey_pressed_called, "on_refresh должен быть вызван"
        assert component.tree_updated_called, "on_tree_updated должен быть вызван"
        
        assert component.last_node == 42
        assert component.last_data == {"items": [1, 2, 3]}
        assert component.tree_data == ["root", "child"]

    def test_correct_routing_to_methods(self):
        """Проверяет правильную маршрутизацию событий к соответствующим методам."""
        # Arrange
        event_bus = EventBus()
        
        class Router:
            def __init__(self):
                self.calls = []
                event_bus.subscribe('event.type1', self.method1)
                event_bus.subscribe('event.type2', self.method2)
                event_bus.subscribe('event.type3', self.method3)
            
            def method1(self, event):
                self.calls.append('method1')
            
            def method2(self, event):
                self.calls.append('method2')
            
            def method3(self, event):
                self.calls.append('method3')
        
        # Act
        router = Router()
        
        # Испускаем события в разном порядке
        event_bus.emit('event.type2')
        event_bus.emit('event.type1')
        event_bus.emit('event.type3')
        event_bus.emit('event.type2')
        
        # Assert
        assert router.calls == ['method2', 'method1', 'method3', 'method2'], \
            "События должны направляться к правильным методам"

    def test_methods_isolated_from_each_other(self):
        """Проверяет изоляцию методов-обработчиков друг от друга."""
        # Arrange
        event_bus = EventBus()
        
        class Component:
            def __init__(self):
                self.value = 0
                event_bus.subscribe('increment', self.increment)
                event_bus.subscribe('decrement', self.decrement)
                event_bus.subscribe('crash', self.crash)
            
            def increment(self, event):
                self.value += 1
            
            def decrement(self, event):
                self.value -= 1
            
            def crash(self, event):
                raise ValueError("Ошибка в crash методе")
        
        # Act
        component = Component()
        
        # Даже если один метод падает, другие должны работать
        try:
            event_bus.emit('crash')
        except:
            pass  # Игнорируем, ошибка должна логироваться внутри шины
        
        event_bus.emit('increment')
        event_bus.emit('increment')
        event_bus.emit('decrement')
        
        # Assert
        assert component.value == 1, \
            "Методы должны быть изолированы: 2 инкремента - 1 декремент = 1"

    def test_unsubscribe_one_method_doesnt_affect_others(self):
        """Проверяет, что отписка одного метода не влияет на другие."""
        # Arrange
        event_bus = EventBus()
        
        class Component:
            def __init__(self):
                self.calls = []
                self.unsub_increment = None
                self.unsub_decrement = None
            
            def setup(self):
                self.unsub_increment = event_bus.subscribe('counter.inc', self.increment)
                self.unsub_decrement = event_bus.subscribe('counter.dec', self.decrement)
                event_bus.subscribe('counter.reset', self.reset)
            
            def increment(self, event):
                self.calls.append('inc')
            
            def decrement(self, event):
                self.calls.append('dec')
            
            def reset(self, event):
                self.calls.clear()
        
        # Act
        component = Component()
        component.setup()
        
        event_bus.emit('counter.inc')
        event_bus.emit('counter.dec')
        
        # Отписываем только increment
        if component.unsub_increment:
            component.unsub_increment()
        
        event_bus.emit('counter.inc')  # Не должен вызваться
        event_bus.emit('counter.dec')  # Должен вызваться
        
        # Assert
        assert component.calls == ['inc', 'dec', 'dec'], \
            "После отписки должен вызываться только decrement"