# tests/test_basic_functionality/test_multiple_event_types.py
"""Тест подписки одного объекта на несколько типов событий."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.event_constants import UIEvents, SystemEvents, HotkeyEvents


class TestMultipleEventTypes:
    """Тестирует работу с несколькими типами событий для одного подписчика."""

    def test_single_object_subscribes_to_multiple_events(self):
        """Проверяет, что объект может подписаться на несколько событий."""
        # Arrange
        event_bus = EventBus()
        mock_handler = Mock()
        
        # Act
        event_bus.subscribe(UIEvents.NODE_SELECTED, mock_handler)
        event_bus.subscribe(SystemEvents.DATA_LOADED, mock_handler)
        event_bus.subscribe(HotkeyEvents.REFRESH_CURRENT, mock_handler)
        
        # Эмитируем события
        event_bus.emit(UIEvents.NODE_SELECTED, {"node_id": 1})
        event_bus.emit(SystemEvents.DATA_LOADED, {"node_id": 1})
        event_bus.emit(HotkeyEvents.REFRESH_CURRENT)
        
        # Assert
        assert mock_handler.call_count == 3

    def test_handler_receives_correct_event_types(self):
        """Проверяет, что обработчик получает правильные типы событий."""
        # Arrange
        event_bus = EventBus()
        received_types = []
        
        def collector(event):
            received_types.append(event['type'])
        
        # Act
        event_bus.subscribe(UIEvents.NODE_EXPANDED, collector)
        event_bus.subscribe(SystemEvents.CACHE_UPDATED, collector)
        event_bus.subscribe(UIEvents.TAB_CHANGED, collector)
        
        event_bus.emit(UIEvents.NODE_EXPANDED, {"node_id": 1})
        event_bus.emit(SystemEvents.CACHE_UPDATED, {"entity_type": "test"})
        event_bus.emit(UIEvents.TAB_CHANGED, {"tab_index": 2})
        
        # Assert
        assert len(received_types) == 3
        assert received_types[0] == UIEvents.NODE_EXPANDED
        assert received_types[1] == SystemEvents.CACHE_UPDATED
        assert received_types[2] == UIEvents.TAB_CHANGED

    def test_different_handlers_for_different_events(self):
        """Проверяет, что объект может использовать разные обработчики."""
        # Arrange
        event_bus = EventBus()
        
        class HandlerObject:
            def __init__(self):
                self.node_selected_called = False
                self.data_loaded_called = False
                self.hotkey_called = False
            
            def on_node_selected(self, event):
                self.node_selected_called = True
                assert event['type'] == UIEvents.NODE_SELECTED
            
            def on_data_loaded(self, event):
                self.data_loaded_called = True
                assert event['type'] == SystemEvents.DATA_LOADED
            
            def on_hotkey(self, event):
                self.hotkey_called = True
                assert event['type'] == HotkeyEvents.REFRESH_VISIBLE
        
        handler = HandlerObject()
        
        # Act
        event_bus.subscribe(UIEvents.NODE_SELECTED, handler.on_node_selected)
        event_bus.subscribe(SystemEvents.DATA_LOADED, handler.on_data_loaded)
        event_bus.subscribe(HotkeyEvents.REFRESH_VISIBLE, handler.on_hotkey)
        
        event_bus.emit(UIEvents.NODE_SELECTED)
        event_bus.emit(SystemEvents.DATA_LOADED)
        event_bus.emit(HotkeyEvents.REFRESH_VISIBLE)
        
        # Assert
        assert handler.node_selected_called
        assert handler.data_loaded_called
        assert handler.hotkey_called

    def test_subscribe_same_event_multiple_times(self):
        """Проверяет множественную подписку на одно событие."""
        # Arrange
        event_bus = EventBus()
        call_count = 0
        
        def handler(event):
            nonlocal call_count
            call_count += 1
        
        # Act - подписываем один и тот же обработчик дважды
        event_bus.subscribe(SystemEvents.DATA_LOADING, handler)
        event_bus.subscribe(SystemEvents.DATA_LOADING, handler)
        
        event_bus.emit(SystemEvents.DATA_LOADING)
        
        # Assert - должен быть вызван дважды
        assert call_count == 2