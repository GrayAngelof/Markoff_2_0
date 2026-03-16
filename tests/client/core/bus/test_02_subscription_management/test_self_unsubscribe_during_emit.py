# tests/client/core/bus/test_subscription_management/test_self_unsubscribe_during_emit.py
"""Тест самоотписки во время обработки события."""
import pytest
from unittest.mock import Mock
from typing import Optional, Callable

from client.src.core.event_bus import EventBus
from client.src.core.events import HotkeyEvents, SystemEvents


class TestSelfUnsubscribeDuringEmit:
    """Тестирует отписку обработчика от самого себя во время обработки."""

    def test_self_unsubscribe_prevents_future_calls(self):
        """Проверяет, что самоотписка предотвращает будущие вызовы."""
        # Arrange
        event_bus = EventBus()
        
        call_timestamps = []
        unsubscribe_func: Optional[Callable[[], None]] = None
        
        def handler(event):
            call_timestamps.append(len(call_timestamps))
            if unsubscribe_func and len(call_timestamps) == 1:
                unsubscribe_func()
        
        # Act
        unsubscribe_func = event_bus.subscribe(HotkeyEvents.REFRESH_CURRENT, handler)
        
        # Первый вызов
        event_bus.emit(HotkeyEvents.REFRESH_CURRENT)
        # Второй вызов
        event_bus.emit(HotkeyEvents.REFRESH_CURRENT)
        # Третий вызов
        event_bus.emit(HotkeyEvents.REFRESH_CURRENT)
        
        # Assert
        assert len(call_timestamps) == 1, "Обработчик должен быть вызван только один раз"

    def test_self_unsubscribe_doesnt_affect_current_emit(self):
        """Проверяет, что самоотписка не влияет на текущий emit."""
        # Arrange
        event_bus = EventBus()
        
        execution_order = []
        unsubscribe_self: Optional[Callable[[], None]] = None
        
        def self_unsubscriber(event):
            execution_order.append('self_unsubscriber')
            # Отписываемся
            if unsubscribe_self:
                unsubscribe_self()
        
        def other_handler(event):
            execution_order.append('other_handler')
        
        # Act
        unsubscribe_self = event_bus.subscribe(SystemEvents.CONNECTION_CHANGED, self_unsubscriber)
        event_bus.subscribe(SystemEvents.CONNECTION_CHANGED, other_handler)
        
        # Emit
        event_bus.emit(SystemEvents.CONNECTION_CHANGED)
        
        # Assert
        assert execution_order == ['self_unsubscriber', 'other_handler'], \
            "Оба обработчика должны быть вызваны в текущем emit"
        
        # Проверяем, что отписка сработала для будущих emit
        event_bus.emit(SystemEvents.CONNECTION_CHANGED)
        assert execution_order == ['self_unsubscriber', 'other_handler', 'other_handler'], \
            "При втором emit должен вызываться только other_handler"

    def test_multiple_self_unsubscribes(self):
        """Проверяет множественные самоотписки."""
        # Arrange
        event_bus = EventBus()
        
        calls = []
        
        # Создаём отдельные функции отписки для каждого обработчика
        unsub_A = None
        unsub_B = None
        unsub_C = None
        
        def handler_A(event):
            calls.append('A')
            if unsub_A:
                unsub_A()
        
        def handler_B(event):
            calls.append('B')
            if unsub_B:
                unsub_B()
        
        def handler_C(event):
            calls.append('C')
            if unsub_C:
                unsub_C()
        
        # Подписываем обработчики
        unsub_A = event_bus.subscribe(SystemEvents.DATA_LOADED, handler_A)
        unsub_B = event_bus.subscribe(SystemEvents.DATA_LOADED, handler_B)
        unsub_C = event_bus.subscribe(SystemEvents.DATA_LOADED, handler_C)
        
        # Act - первый emit
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert - все должны быть вызваны в первом emit
        assert calls == ['A', 'B', 'C'], f"Ожидалось ['A', 'B', 'C'], получено {calls}"
        
        # Act - второй emit
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert - никто не должен быть вызван
        assert calls == ['A', 'B', 'C'], f"Во втором emit не должно быть вызовов, получено {calls}"
        
        # Проверяем, что подписки действительно удалены
        assert event_bus.get_subscriber_count(SystemEvents.DATA_LOADED) == 0

    def test_self_unsubscribe_with_multiple_emits_before_unsubscribe(self):
        """Проверяет самоотписку после нескольких вызовов."""
        # Arrange
        event_bus = EventBus()
        
        call_count = 0
        unsubscribe: Optional[Callable[[], None]] = None
        
        def handler(event):
            nonlocal call_count, unsubscribe
            call_count += 1
            if call_count == 2 and unsubscribe is not None:  # Отписываемся после второго вызова
                unsub_func = unsubscribe
                unsubscribe = None
                unsub_func()
        
        # Act
        unsubscribe = event_bus.subscribe(SystemEvents.DATA_ERROR, handler)
        
        event_bus.emit(SystemEvents.DATA_ERROR)  # 1
        event_bus.emit(SystemEvents.DATA_ERROR)  # 2 (здесь отписываемся)
        event_bus.emit(SystemEvents.DATA_ERROR)  # 3
        event_bus.emit(SystemEvents.DATA_ERROR)  # 4
        
        # Assert
        assert call_count == 2, "Обработчик должен быть вызван только два раза"

    def test_self_unsubscribe_and_resubscribe(self):
        """Проверяет самоотписку и повторную подписку."""
        # Arrange
        event_bus = EventBus()
        
        calls = []
        unsubscribe: Optional[Callable[[], None]] = None
        
        def handler(event):
            nonlocal unsubscribe
            calls.append(len(calls))
            if len(calls) == 1 and unsubscribe is not None:
                current_unsub = unsubscribe
                unsubscribe = None
                current_unsub()  # Отписываемся после первого вызова
                # Снова подписываемся
                new_unsub = event_bus.subscribe(SystemEvents.DATA_LOADING, handler)
                unsubscribe = new_unsub
        
        # Act
        unsubscribe = event_bus.subscribe(SystemEvents.DATA_LOADING, handler)
        
        event_bus.emit(SystemEvents.DATA_LOADING)  # Первый вызов (отписывается и подписывается заново)
        event_bus.emit(SystemEvents.DATA_LOADING)  # Второй вызов
        event_bus.emit(SystemEvents.DATA_LOADING)  # Третий вызов
        
        # Assert
        assert len(calls) == 3, "Обработчик должен вызываться после повторной подписки"

    def test_mixed_self_and_other_unsubscribes(self):
        """Проверяет смешанные самоотписки и отписки других обработчиков."""
        # Arrange
        event_bus = EventBus()
        
        order = []
        unsubscribes: list[Optional[Callable[[], None]]] = [None, None, None]
        
        def handler_a(event):
            order.append('A')
            # Отписываем C
            if unsubscribes[2] is not None:
                unsub_func = unsubscribes[2]
                unsubscribes[2] = None
                unsub_func()
        
        def handler_b(event):
            order.append('B')
            # Отписываемся сами
            if unsubscribes[1] is not None:
                unsub_func = unsubscribes[1]
                unsubscribes[1] = None
                unsub_func()
        
        def handler_c(event):
            order.append('C')
        
        # Act
        unsubscribes[0] = event_bus.subscribe(SystemEvents.CACHE_UPDATED, handler_a)
        unsubscribes[1] = event_bus.subscribe(SystemEvents.CACHE_UPDATED, handler_b)
        unsubscribes[2] = event_bus.subscribe(SystemEvents.CACHE_UPDATED, handler_c)
        
        event_bus.emit(SystemEvents.CACHE_UPDATED)  # Первый emit
        event_bus.emit(SystemEvents.CACHE_UPDATED)  # Второй emit
        
        # Assert
        # Первый emit: A, B, C (отписки происходят после вызовов)
        # Второй emit: только A (B отписался, C отписан)
        assert order == ['A', 'B', 'C', 'A']
        
        # Проверяем количество подписчиков после всех операций
        assert event_bus.get_subscriber_count(SystemEvents.CACHE_UPDATED) == 1  # Только A остался