# tests/client/core/bus/test_subscription_management/test_unsubscribe_during_emit.py
"""Тест отписки во время испускания события."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestUnsubscribeDuringEmit:
    """Тестирует отписку от событий во время обработки другого события."""

    def test_unsubscribe_other_handler_during_emit(self):
        """Проверяет отписку другого обработчика во время обработки."""
        # Arrange
        event_bus = EventBus()
        
        call_order = []
        unsubscribes = []
        
        def handler1(event):
            call_order.append('handler1')
            # Отписываем handler2
            unsubscribes[1]()
        
        def handler2(event):
            call_order.append('handler2')
        
        def handler3(event):
            call_order.append('handler3')
        
        # Act
        unsubscribes.append(event_bus.subscribe(UIEvents.TAB_CHANGED, handler1))
        unsubscribes.append(event_bus.subscribe(UIEvents.TAB_CHANGED, handler2))
        unsubscribes.append(event_bus.subscribe(UIEvents.TAB_CHANGED, handler3))
        
        event_bus.emit(UIEvents.TAB_CHANGED)
        event_bus.emit(UIEvents.TAB_CHANGED)
        
        # Assert
        # Первый emit: все три должны быть вызваны (отписка происходит после вызова handler2)
        # Второй emit: handler2 уже отписан
        assert call_order == ['handler1', 'handler2', 'handler3', 'handler1', 'handler3']

    def test_unsubscribe_self_during_emit(self):
        """Проверяет отписку самого себя во время обработки."""
        # Arrange
        event_bus = EventBus()
        
        call_count = 0
        unsubscribe_self = None
        
        def self_unsubscribing_handler(event):
            nonlocal call_count
            call_count += 1
            if unsubscribe_self:
                unsubscribe_self()
        
        # Act
        unsubscribe_self = event_bus.subscribe(SystemEvents.DATA_ERROR, self_unsubscribing_handler)
        
        event_bus.emit(SystemEvents.DATA_ERROR)
        event_bus.emit(SystemEvents.DATA_ERROR)
        event_bus.emit(SystemEvents.DATA_ERROR)
        
        # Assert
        assert call_count == 1, "Обработчик должен быть вызван только один раз (до самоотписки)"

    def test_unsubscribe_multiple_handlers_during_emit(self):
        """Проверяет отписку нескольких обработчиков во время обработки."""
        # Arrange
        event_bus = EventBus()
        
        called = []
        unsubscribes = []
        
        def killer_handler(event):
            called.append('killer')
            # Отписываем всех, кроме себя
            for i, unsub in enumerate(unsubscribes):
                if i != 0 and unsub is not None:  # Не отписываем себя
                    unsub()
        
        def victim1(event):
            called.append('victim1')
        
        def victim2(event):
            called.append('victim2')
        
        def survivor(event):
            called.append('survivor')
        
        # Act
        unsubscribes.append(event_bus.subscribe(SystemEvents.DATA_LOADING, killer_handler))
        unsubscribes.append(event_bus.subscribe(SystemEvents.DATA_LOADING, victim1))
        unsubscribes.append(event_bus.subscribe(SystemEvents.DATA_LOADING, victim2))
        unsubscribes.append(event_bus.subscribe(SystemEvents.DATA_LOADING, survivor))
        
        event_bus.emit(SystemEvents.DATA_LOADING)
        event_bus.emit(SystemEvents.DATA_LOADING)
        
        # Assert
        # Первый emit: все должны быть вызваны (отписка происходит после вызовов)
        # Второй emit: только killer (survivor был отписан, так как i=3 != 0)
        expected_order = ['killer', 'victim1', 'victim2', 'survivor', 'killer']
        assert called == expected_order, f"Ожидалось {expected_order}, получено {called}"