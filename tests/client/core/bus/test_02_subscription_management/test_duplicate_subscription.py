# tests/client/core/bus/test_subscription_management/test_duplicate_subscription.py
"""Тест дублирования подписок."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.event_constants import SystemEvents


class TestDuplicateSubscription:
    """Тестирует дублирование подписок."""

    def test_same_callback_subscribed_multiple_times(self):
        """Проверяет поведение при многократной подписке одного обработчика."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        event_type = SystemEvents.DATA_LOADED
        
        # Act - подписываем один и тот же callback 3 раза
        unsubscribe1 = event_bus.subscribe(event_type, mock_callback)
        unsubscribe2 = event_bus.subscribe(event_type, mock_callback)
        unsubscribe3 = event_bus.subscribe(event_type, mock_callback)
        
        event_bus.emit(event_type)
        
        # Assert - должен быть вызван 3 раза (по одному на каждую подписку)
        assert mock_callback.call_count == 3, "Обработчик должен вызываться для каждой подписки"
        
        # Проверяем, что отписка работает для каждой подписки отдельно
        unsubscribe1()
        event_bus.emit(event_type)
        assert mock_callback.call_count == 5, "После отписки первого должно остаться 2 подписки"
        
        unsubscribe2()
        event_bus.emit(event_type)
        assert mock_callback.call_count == 6, "После отписки второго должна остаться 1 подписка"
        
        unsubscribe3()
        event_bus.emit(event_type)
        assert mock_callback.call_count == 6, "После отписки третьего не должно быть вызовов"

    def test_same_method_subscribed_multiple_times(self):
        """Проверяет дублирование подписки одного метода класса."""
        # Arrange
        event_bus = EventBus()
        
        class Handler:
            def __init__(self):
                self.call_count = 0
            
            def handle(self, event):
                self.call_count += 1
        
        handler = Handler()
        
        # Act - подписываем один метод 3 раза
        unsubscribe1 = event_bus.subscribe(SystemEvents.DATA_LOADING, handler.handle)
        unsubscribe2 = event_bus.subscribe(SystemEvents.DATA_LOADING, handler.handle)
        unsubscribe3 = event_bus.subscribe(SystemEvents.DATA_LOADING, handler.handle)
        
        event_bus.emit(SystemEvents.DATA_LOADING)
        
        # Assert
        assert handler.call_count == 3, "Метод должен вызываться для каждой подписки"
        
        # Отписываемся от одной подписки
        unsubscribe2()
        event_bus.emit(SystemEvents.DATA_LOADING)
        assert handler.call_count == 5, "Должно остаться 2 подписки"

    def test_different_objects_same_method_name(self):
        """Проверяет подписку методов с одинаковым именем от разных объектов."""
        # Arrange
        event_bus = EventBus()
        
        class Handler:
            def __init__(self, name):
                self.name = name
                self.called = False
            
            def handle(self, event):
                self.called = True
        
        handler1 = Handler("first")
        handler2 = Handler("second")
        
        # Act
        event_bus.subscribe(SystemEvents.CONNECTION_CHANGED, handler1.handle)
        event_bus.subscribe(SystemEvents.CONNECTION_CHANGED, handler2.handle)
        
        event_bus.emit(SystemEvents.CONNECTION_CHANGED)
        
        # Assert
        assert handler1.called, "Первый обработчик должен быть вызван"
        assert handler2.called, "Второй обработчик должен быть вызван"