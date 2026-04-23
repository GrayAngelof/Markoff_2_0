# tests/test_basic_functionality/test_basic_subscription_and_emit.py
"""Тест базовой подписки и испускания событий."""
import pytest
import time
from unittest.mock import Mock, MagicMock

from client.src.core.event_bus import EventBus
from client.src.core.event_constants import SystemEvents, UIEvents


class TestBasicSubscriptionAndEmit:
    """Тестирует базовую подписку и испускание событий."""

    def test_subscriber_receives_event_after_subscription(self):
        """Проверяет, что подписчик получает событие после подписки."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        event_type = UIEvents.NODE_SELECTED
        test_data = {"node_type": "test_type", "node_id": 42, "data": "test_object"}
        test_source = "test_source"
        
        # Act
        event_bus.subscribe(event_type, mock_callback)
        event_bus.emit(event_type, data=test_data, source=test_source)
        
        # Assert
        mock_callback.assert_called_once()
        
        # Проверяем структуру события
        called_event = mock_callback.call_args[0][0]
        assert called_event['type'] == event_type
        assert called_event['data'] == test_data
        assert called_event['source'] == test_source
        assert 'timestamp' in called_event
        assert isinstance(called_event['timestamp'], float)
        assert called_event['timestamp'] <= time.time()

    def test_subscriber_receives_event_with_empty_data(self):
        """Проверяет работу с пустыми данными события."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        event_type = SystemEvents.CONNECTION_CHANGED
        
        # Act
        event_bus.subscribe(event_type, mock_callback)
        event_bus.emit(event_type)  # Без data и source
        
        # Assert
        mock_callback.assert_called_once()
        called_event = mock_callback.call_args[0][0]
        assert called_event['type'] == event_type
        assert called_event['data'] == {}  # Должен быть пустой словарь
        assert called_event['source'] is None

    def test_multiple_emits_to_same_subscriber(self):
        """Проверяет, что подписчик получает все испускаемые события."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        event_type = UIEvents.REFRESH_REQUESTED
        
        # Act
        event_bus.subscribe(event_type, mock_callback)
        event_bus.emit(event_type, {"mode": "current"})
        event_bus.emit(event_type, {"mode": "visible"})
        event_bus.emit(event_type, {"mode": "full"})
        
        # Assert
        assert mock_callback.call_count == 3
        calls = mock_callback.call_args_list
        assert calls[0][0][0]['data']['mode'] == "current"
        assert calls[1][0][0]['data']['mode'] == "visible"
        assert calls[2][0][0]['data']['mode'] == "full"

    def test_timestamp_accuracy(self):
        """Проверяет точность временных меток событий."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        event_type = SystemEvents.DATA_LOADING
        
        # Act
        before_emit = time.time()
        event_bus.subscribe(event_type, mock_callback)
        event_bus.emit(event_type, {"node_type": "test"})
        after_emit = time.time()
        
        # Assert
        called_event = mock_callback.call_args[0][0]
        event_timestamp = called_event['timestamp']
        assert before_emit <= event_timestamp <= after_emit