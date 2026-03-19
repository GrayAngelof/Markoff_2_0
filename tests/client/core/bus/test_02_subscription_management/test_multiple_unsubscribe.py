# tests/client/core/bus/test_subscription_management/test_multiple_unsubscribe.py
"""Тест повторной отписки от событий."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.event_constants import UIEvents


class TestMultipleUnsubscribe:
    """Тестирует повторную отписку от событий."""

    def test_multiple_unsubscribe_calls_dont_cause_errors(self):
        """Проверяет, что повторные вызовы отписки не вызывают ошибок."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        
        # Act
        unsubscribe = event_bus.subscribe(UIEvents.NODE_SELECTED, mock_callback)
        
        # Первая отписка
        unsubscribe()
        
        # Повторные отписки не должны вызывать исключений
        try:
            unsubscribe()  # Второй раз
            unsubscribe()  # Третий раз
        except Exception as e:
            pytest.fail(f"Повторная отписка вызвала исключение: {e}")
        
        # Assert - обработчик не должен вызываться после любой отписки
        event_bus.emit(UIEvents.NODE_SELECTED)
        mock_callback.assert_not_called()

    def test_unsubscribe_after_already_unsubscribed(self):
        """Проверяет отписку после того, как подписка уже была удалена другим способом."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        
        # Act
        unsubscribe = event_bus.subscribe(UIEvents.NODE_SELECTED, mock_callback)
        
        # Удаляем подписку через очистку
        event_bus.clear()
        
        # Пытаемся отписаться через сохранённую функцию
        try:
            unsubscribe()
        except Exception as e:
            pytest.fail(f"Отписка после clear вызвала исключение: {e}")
        
        # Assert
        event_bus.emit(UIEvents.NODE_SELECTED)
        mock_callback.assert_not_called()

    def test_unsubscribe_from_multiple_events(self):
        """Проверяет отписку от нескольких событий."""
        # Arrange
        event_bus = EventBus()
        mock_callback1 = Mock()
        mock_callback2 = Mock()
        
        # Act
        unsubscribe1 = event_bus.subscribe(UIEvents.NODE_SELECTED, mock_callback1)
        unsubscribe2 = event_bus.subscribe(UIEvents.NODE_EXPANDED, mock_callback2)
        
        # Отписываемся
        unsubscribe1()
        unsubscribe2()
        
        # Пытаемся отписаться ещё раз
        unsubscribe1()
        unsubscribe2()
        
        # Assert
        event_bus.emit(UIEvents.NODE_SELECTED)
        event_bus.emit(UIEvents.NODE_EXPANDED)
        
        mock_callback1.assert_not_called()
        mock_callback2.assert_not_called()