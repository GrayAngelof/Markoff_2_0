# tests/client/core/bus/test_subscription_management/test_subscribe_during_emit.py
"""Тест подписки во время испускания события."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.event_constants import UIEvents, SystemEvents


class TestSubscribeDuringEmit:
    """Тестирует подписку на события во время обработки другого события."""

    def test_subscribe_to_different_event_during_emit(self):
        """Проверяет подписку на другое событие во время обработки."""
        # Arrange
        event_bus = EventBus()
        mock_new_handler = Mock()
        
        events_received = []
        
        def handler1(event):
            events_received.append('handler1')
            # Подписываемся на другое событие
            event_bus.subscribe(SystemEvents.DATA_LOADED, mock_new_handler)
        
        def handler2(event):
            events_received.append('handler2')
        
        # Act
        event_bus.subscribe(UIEvents.NODE_SELECTED, handler1)
        event_bus.subscribe(UIEvents.NODE_SELECTED, handler2)
        
        # Испускаем событие
        event_bus.emit(UIEvents.NODE_SELECTED)
        
        # Испускаем событие, на которое подписались во время первого emit
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert
        assert events_received == ['handler1', 'handler2']
        # Исправлено: убираем return value check
        mock_new_handler.assert_called_once()

    def test_subscribe_to_same_event_during_emit(self):
        """Проверяет подписку на то же событие во время его обработки."""
        # Arrange
        event_bus = EventBus()
        
        subscription_order = []
        
        def handler1(event):
            subscription_order.append('handler1')
            # Подписываем новый обработчик на то же событие
            event_bus.subscribe(UIEvents.NODE_EXPANDED, handler3)
        
        def handler2(event):
            subscription_order.append('handler2')
        
        def handler3(event):
            subscription_order.append('handler3')
        
        # Act
        event_bus.subscribe(UIEvents.NODE_EXPANDED, handler1)
        event_bus.subscribe(UIEvents.NODE_EXPANDED, handler2)
        
        # Испускаем событие
        event_bus.emit(UIEvents.NODE_EXPANDED)
        
        # Испускаем ещё раз, чтобы проверить нового подписчика
        event_bus.emit(UIEvents.NODE_EXPANDED)
        
        # Assert
        # Первый emit: только handler1 и handler2
        # Второй emit: handler1, handler2 и handler3
        assert subscription_order == ['handler1', 'handler2', 'handler1', 'handler2', 'handler3']

    def test_subscribe_in_multiple_handlers_during_emit(self):
        """Проверяет множественные подписки во время обработки."""
        # Arrange
        event_bus = EventBus()
        
        new_handlers_called = []
        # Сохраняем ссылки на новые обработчики, чтобы они не были собраны GC
        new_handlers = []
        
        def handler1(event):
            def new_handler1(e):
                new_handlers_called.append('new1')
            # Сохраняем ссылку на обработчик
            new_handlers.append(new_handler1)
            event_bus.subscribe(SystemEvents.CACHE_UPDATED, new_handler1)
        
        def handler2(event):
            def new_handler2(e):
                new_handlers_called.append('new2')
            # Сохраняем ссылку на обработчик
            new_handlers.append(new_handler2)
            event_bus.subscribe(SystemEvents.CACHE_UPDATED, new_handler2)
        
        # Act
        event_bus.subscribe(UIEvents.REFRESH_REQUESTED, handler1)
        event_bus.subscribe(UIEvents.REFRESH_REQUESTED, handler2)
        
        event_bus.emit(UIEvents.REFRESH_REQUESTED)
        
        # Принудительно вызываем сборщик мусора, чтобы убедиться, что наши обработчики живы
        import gc
        gc.collect()
        
        event_bus.emit(SystemEvents.CACHE_UPDATED)
        
        # Assert
        assert len(new_handlers_called) == 2, f"Ожидалось 2 вызова, получено {len(new_handlers_called)}"
        assert 'new1' in new_handlers_called
        assert 'new2' in new_handlers_called

    def test_subscribe_and_emit_chain(self):
        """Проверяет цепочку подписок и испусканий."""
        # Arrange
        event_bus = EventBus()
        chain_order = []
        
        def handler_a(event):
            chain_order.append('A')
            # Подписываемся на B и сразу испускаем
            def handler_b(e):
                chain_order.append('B')
            event_bus.subscribe('test.event_b', handler_b)
            event_bus.emit('test.event_b')
        
        def handler_c(event):
            chain_order.append('C')
        
        # Act
        event_bus.subscribe('test.event_a', handler_a)
        event_bus.subscribe('test.event_c', handler_c)
        
        event_bus.emit('test.event_a')
        event_bus.emit('test.event_c')
        
        # Assert
        assert chain_order == ['A', 'B', 'C']

    def test_subscribe_during_emit_doesnt_affect_current_iteration(self):
        """Проверяет, что подписка во время emit не влияет на текущую итерацию."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        # Создаём нового обработчика заранее
        def new_handler(e):
            execution_order.append('new')
        
        def handler_with_subscribe(event):
            execution_order.append('subscriber')
            # Подписываем нового обработчика (он уже создан)
            event_bus.subscribe(UIEvents.NODE_COLLAPSED, new_handler)
        
        def regular_handler(event):
            execution_order.append('regular')
        
        # Act
        event_bus.subscribe(UIEvents.NODE_COLLAPSED, handler_with_subscribe)
        event_bus.subscribe(UIEvents.NODE_COLLAPSED, regular_handler)
        
        # Первый emit
        event_bus.emit(UIEvents.NODE_COLLAPSED)
        
        # Assert - новый обработчик не должен быть вызван в текущей итерации
        assert execution_order == ['subscriber', 'regular'], \
            f"Первый emit: ожидалось ['subscriber', 'regular'], получено {execution_order}"
        
        # Второй emit
        event_bus.emit(UIEvents.NODE_COLLAPSED)
        
        # Assert - новый обработчик должен быть вызван во втором emit
        expected = ['subscriber', 'regular', 'subscriber', 'regular', 'new']
        assert execution_order == expected, \
            f"Второй emit: ожидалось {expected}, получено {execution_order}"