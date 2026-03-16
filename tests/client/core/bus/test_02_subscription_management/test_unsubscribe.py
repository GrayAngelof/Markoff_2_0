# tests/client/core/bus/test_subscription_management/test_unsubscribe.py
"""Тест базовой отписки от событий."""
import pytest
from unittest.mock import Mock, MagicMock

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestUnsubscribe:
    """Тестирует базовую отписку от событий."""

    def test_unsubscribe_prevents_future_calls(self):
        """Проверяет, что после отписки обработчик больше не вызывается."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        event_type = UIEvents.NODE_SELECTED
        
        # Act
        unsubscribe = event_bus.subscribe(event_type, mock_callback)
        event_bus.emit(event_type)
        unsubscribe()
        event_bus.emit(event_type)
        
        # Assert
        assert mock_callback.call_count == 1, "После отписки обработчик не должен вызываться"

    def test_unsubscribe_removes_only_specific_callback(self):
        """Проверяет, что отписка удаляет только конкретный обработчик."""
        # Arrange
        event_bus = EventBus()
        mock_callback1 = Mock()
        mock_callback2 = Mock()
        event_type = SystemEvents.DATA_LOADED
        
        # Act
        unsubscribe1 = event_bus.subscribe(event_type, mock_callback1)
        event_bus.subscribe(event_type, mock_callback2)
        
        event_bus.emit(event_type)  # Оба получают
        unsubscribe1()
        event_bus.emit(event_type)  # Только второй получает
        
        # Assert
        assert mock_callback1.call_count == 1, "Первый обработчик должен получить только первое событие"
        assert mock_callback2.call_count == 2, "Второй обработчик должен получить оба события"

    def test_unsubscribe_from_one_event_doesnt_affect_others(self):
        """Проверяет, что отписка от одного события не влияет на другие подписки."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        
        # Act
        unsubscribe1 = event_bus.subscribe(UIEvents.NODE_SELECTED, mock_callback)
        event_bus.subscribe(SystemEvents.DATA_LOADED, mock_callback)
        
        event_bus.emit(UIEvents.NODE_SELECTED)
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        unsubscribe1()  # Отписываемся только от NODE_SELECTED
        
        event_bus.emit(UIEvents.NODE_SELECTED)
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert
        assert mock_callback.call_count == 3  # Получил: 2 первых + только DATA_LOADED после отписки