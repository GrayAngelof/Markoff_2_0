# tests/test_basic_functionality/test_event_type_filtering.py
"""Тест фильтрации событий по типу."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents, HotkeyEvents, ProjectionEvents


class TestEventTypeFiltering:
    """Тестирует фильтрацию событий по типу."""

    def test_handler_receives_only_subscribed_events(self):
        """Проверяет, что обработчик получает только события своего типа."""
        # Arrange
        event_bus = EventBus()
        mock_handler = Mock()
        
        # Подписываем только на одно событие
        event_bus.subscribe(UIEvents.NODE_SELECTED, mock_handler)
        
        # Act - испускаем разные события
        event_bus.emit(UIEvents.NODE_SELECTED, {"node_id": 1})
        event_bus.emit(SystemEvents.DATA_LOADED, {"node_id": 1})
        event_bus.emit(HotkeyEvents.REFRESH_CURRENT)
        event_bus.emit(ProjectionEvents.TREE_UPDATED)
        
        # Assert
        mock_handler.assert_called_once()
        called_event = mock_handler.call_args[0][0]
        assert called_event['type'] == UIEvents.NODE_SELECTED

    def test_multiple_handlers_different_events(self):
        """Проверяет работу нескольких обработчиков на разные события."""
        # Arrange
        event_bus = EventBus()
        mock_handler1 = Mock()  # Для NODE_SELECTED
        mock_handler2 = Mock()  # Для DATA_LOADED
        mock_handler3 = Mock()  # Для HOTKEY
        
        # Act
        event_bus.subscribe(UIEvents.NODE_SELECTED, mock_handler1)
        event_bus.subscribe(SystemEvents.DATA_LOADED, mock_handler2)
        event_bus.subscribe(HotkeyEvents.REFRESH_CURRENT, mock_handler3)
        
        # Испускаем только одно событие
        event_bus.emit(UIEvents.NODE_SELECTED)
        
        # Assert
        mock_handler1.assert_called_once()
        mock_handler2.assert_not_called()
        mock_handler3.assert_not_called()

    def test_related_events_filtering(self):
        """Проверяет фильтрацию связанных событий."""
        # Arrange
        event_bus = EventBus()
        node_selected_count = 0
        node_expanded_count = 0
        
        def on_selected(event):
            nonlocal node_selected_count
            node_selected_count += 1
        
        def on_expanded(event):
            nonlocal node_expanded_count
            node_expanded_count += 1
        
        # Act
        event_bus.subscribe(UIEvents.NODE_SELECTED, on_selected)
        event_bus.subscribe(UIEvents.NODE_EXPANDED, on_expanded)
        
        # Испускаем оба типа
        event_bus.emit(UIEvents.NODE_SELECTED)
        event_bus.emit(UIEvents.NODE_EXPANDED)
        event_bus.emit(UIEvents.NODE_SELECTED)
        
        # Assert
        assert node_selected_count == 2
        assert node_expanded_count == 1

    def test_no_cross_contamination(self):
        """Проверяет отсутствие перекрёстного загрязнения событий."""
        # Arrange
        event_bus = EventBus()
        
        class Receiver:
            def __init__(self):
                self.received_events = []
            
            def handle_ui(self, event):
                self.received_events.append(('ui', event['type']))
            
            def handle_system(self, event):
                self.received_events.append(('system', event['type']))
        
        receiver = Receiver()
        
        # Act
        event_bus.subscribe(UIEvents.NODE_SELECTED, receiver.handle_ui)
        event_bus.subscribe(UIEvents.NODE_EXPANDED, receiver.handle_ui)
        event_bus.subscribe(SystemEvents.DATA_LOADED, receiver.handle_system)
        event_bus.subscribe(SystemEvents.CACHE_UPDATED, receiver.handle_system)
        
        # Испускаем события
        event_bus.emit(UIEvents.NODE_SELECTED)
        event_bus.emit(SystemEvents.DATA_LOADED)
        event_bus.emit(UIEvents.NODE_EXPANDED)
        event_bus.emit(SystemEvents.CACHE_UPDATED)
        
        # Assert
        assert len(receiver.received_events) == 4
        assert receiver.received_events[0] == ('ui', UIEvents.NODE_SELECTED)
        assert receiver.received_events[1] == ('system', SystemEvents.DATA_LOADED)
        assert receiver.received_events[2] == ('ui', UIEvents.NODE_EXPANDED)
        assert receiver.received_events[3] == ('system', SystemEvents.CACHE_UPDATED)

    def test_similar_event_names(self):
        """Проверяет обработку событий с похожими именами."""
        # Arrange
        event_bus = EventBus()
        mock_handler = Mock()
        
        # Создаём похожие имена событий
        event_type1 = "test.event"
        event_type2 = "test.event.similar"
        event_type3 = "test_event"
        
        # Act
        event_bus.subscribe(event_type1, mock_handler)
        
        event_bus.emit(event_type2)
        event_bus.emit(event_type3)
        event_bus.emit(event_type1)
        
        # Assert
        mock_handler.assert_called_once()
        assert mock_handler.call_args[0][0]['type'] == event_type1