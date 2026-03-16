# tests/client/core/bus/test_04_error_handling/test_error_handling.py
"""Тест обработки ошибок в обработчиках событий."""
import pytest
from unittest.mock import Mock, patch

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestErrorHandling:
    """Тестирует обработку ошибок в обработчиках событий."""

    def test_one_handler_error_doesnt_affect_others(self):
        """Проверяет, что ошибка в одном обработчике не влияет на другие."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def failing_handler(event):
            execution_order.append('failing')
            raise ValueError("Тестовая ошибка")
        
        def normal_handler1(event):
            execution_order.append('normal1')
        
        def normal_handler2(event):
            execution_order.append('normal2')
        
        # Act
        event_bus.subscribe('test_event', failing_handler)
        event_bus.subscribe('test_event', normal_handler1)
        event_bus.subscribe('test_event', normal_handler2)
        
        # Должно выполниться без исключений
        try:
            event_bus.emit('test_event')
        except Exception:
            pytest.fail("EventBus не должен пробрасывать исключения из обработчиков")
        
        # Assert
        assert execution_order == ['failing', 'normal1', 'normal2'], \
            "Все обработчики должны быть вызваны несмотря на ошибку"

    def test_multiple_handlers_with_errors(self):
        """Проверяет ситуацию с несколькими ошибочными обработчиками."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def failing_handler1(event):
            execution_order.append('failing1')
            raise ValueError("Ошибка 1")
        
        def failing_handler2(event):
            execution_order.append('failing2')
            raise RuntimeError("Ошибка 2")
        
        def normal_handler(event):
            execution_order.append('normal')
        
        # Act
        event_bus.subscribe('multi_error', failing_handler1)
        event_bus.subscribe('multi_error', failing_handler2)
        event_bus.subscribe('multi_error', normal_handler)
        
        event_bus.emit('multi_error')
        
        # Assert
        assert execution_order == ['failing1', 'failing2', 'normal'], \
            "Все обработчики должны быть вызваны, даже если некоторые падают"

    def test_error_in_middle_of_handlers(self):
        """Проверяет ошибку в середине цепочки обработчиков."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def first_handler(event):
            execution_order.append('first')
        
        def middle_handler(event):
            execution_order.append('middle')
            raise Exception("Ошибка в середине")
        
        def last_handler(event):
            execution_order.append('last')
        
        # Act
        event_bus.subscribe('chain_event', first_handler)
        event_bus.subscribe('chain_event', middle_handler)
        event_bus.subscribe('chain_event', last_handler)
        
        event_bus.emit('chain_event')
        
        # Assert
        assert execution_order == ['first', 'middle', 'last'], \
            "Обработчики после ошибочного должны继续 выполняться"

    def test_error_in_first_handler(self):
        """Проверяет ошибку в первом обработчике."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def first_handler(event):
            execution_order.append('first')
            raise Exception("Ошибка в первом")
        
        def second_handler(event):
            execution_order.append('second')
        
        def third_handler(event):
            execution_order.append('third')
        
        # Act
        event_bus.subscribe('first_error', first_handler)
        event_bus.subscribe('first_error', second_handler)
        event_bus.subscribe('first_error', third_handler)
        
        event_bus.emit('first_error')
        
        # Assert
        assert execution_order == ['first', 'second', 'third'], \
            "Остальные обработчики должны выполняться даже после ошибки в первом"

    def test_error_in_last_handler(self):
        """Проверяет ошибку в последнем обработчике."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def first_handler(event):
            execution_order.append('first')
        
        def second_handler(event):
            execution_order.append('second')
        
        def last_handler(event):
            execution_order.append('last')
            raise Exception("Ошибка в последнем")
        
        # Act
        event_bus.subscribe('last_error', first_handler)
        event_bus.subscribe('last_error', second_handler)
        event_bus.subscribe('last_error', last_handler)
        
        event_bus.emit('last_error')
        
        # Assert
        assert execution_order == ['first', 'second', 'last'], \
            "Ошибка в последнем обработчике не должна влиять на предыдущие"

    def test_error_doesnt_affect_future_emits(self):
        """Проверяет, что ошибка не влияет на будущие испускания."""
        # Arrange
        event_bus = EventBus()
        call_count = 0
        
        def failing_handler(event):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Ошибка при первом вызове")
        
        def normal_handler(event):
            nonlocal call_count
            call_count += 1
        
        # Act
        event_bus.subscribe('future_test', failing_handler)
        event_bus.subscribe('future_test', normal_handler)
        
        # Первый emit (с ошибкой)
        event_bus.emit('future_test')
        assert call_count == 2, "Оба обработчика должны быть вызваны"
        
        # Второй emit
        event_bus.emit('future_test')
        
        # Assert
        assert call_count == 4, "Оба обработчика должны вызываться при последующих emit"