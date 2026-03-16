# tests/client/core/bus/test_advanced_scenarios/test_recursive_emit.py
"""Тест рекурсивных испусканий событий."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestRecursiveEmit:
    """Тестирует рекурсивные испускания событий."""

    def test_recursive_emit_same_event(self):
        """Проверяет рекурсивное испускание того же события."""
        # Arrange
        event_bus = EventBus()
        call_count = 0
        max_depth = 3
        
        def recursive_handler(event):
            nonlocal call_count
            call_count += 1
            if call_count < max_depth:
                event_bus.emit('recursive_event')
        
        # Act
        event_bus.subscribe('recursive_event', recursive_handler)
        event_bus.emit('recursive_event')
        
        # Assert
        assert call_count == max_depth, \
            f"Рекурсивный обработчик должен вызваться {max_depth} раз"

    def test_recursive_emit_with_condition(self):
        """Проверяет рекурсивный emit с условием остановки."""
        # Arrange
        event_bus = EventBus()
        values = []
        
        def counter_handler(event):
            current = event['data'].get('count', 0)
            values.append(current)
            if current < 3:
                event_bus.emit('count_event', {'count': current + 1})
        
        # Act
        event_bus.subscribe('count_event', counter_handler)
        event_bus.emit('count_event', {'count': 0})
        
        # Assert
        assert values == [0, 1, 2, 3], \
            "Должны накопиться значения от 0 до 3"

    def test_recursive_emit_doesnt_overflow_stack(self):
        """Проверяет, что рекурсивные emit не вызывают переполнение стека."""
        # Arrange
        event_bus = EventBus()
        counter = 0
        max_iterations = 100  # Достаточно большое число
        
        def recursive_handler(event):
            nonlocal counter
            counter += 1
            if counter < max_iterations:
                # Должно работать без переполнения стека
                event_bus.emit('recursive')
        
        # Act
        event_bus.subscribe('recursive', recursive_handler)
        
        # Должно выполниться без RecursionError
        try:
            event_bus.emit('recursive')
        except RecursionError:
            pytest.fail("Рекурсивные emit не должны вызывать RecursionError")
        
        # Assert
        assert counter == max_iterations, \
            f"Должно быть выполнено {max_iterations} итераций"

    def test_mutual_recursion(self):
        """Проверяет взаимную рекурсию событий."""
        # Arrange
        event_bus = EventBus()
        order = []
        
        def handler_a(event):
            order.append('A')
            if len(order) < 5:
                event_bus.emit('event_b')
        
        def handler_b(event):
            order.append('B')
            if len(order) < 5:
                event_bus.emit('event_a')
        
        # Act
        event_bus.subscribe('event_a', handler_a)
        event_bus.subscribe('event_b', handler_b)
        
        event_bus.emit('event_a')
        
        # Assert
        expected = ['A', 'B', 'A', 'B', 'A']
        assert order == expected, \
            f"Взаимная рекурсия должна работать: {expected}"

    def test_recursive_emit_with_multiple_handlers(self):
        """Проверяет рекурсивный emit с несколькими обработчиками."""
        # Arrange
        event_bus = EventBus()
        log = []
        
        def handler1(event):
            log.append('h1_start')
            if len(log) < 4:
                event_bus.emit('test')
            log.append('h1_end')
        
        def handler2(event):
            log.append('h2_start')
            if len(log) < 4:
                event_bus.emit('test')
            log.append('h2_end')
        
        # Act
        event_bus.subscribe('test', handler1)
        event_bus.subscribe('test', handler2)
        
        event_bus.emit('test')
        
        # Assert - проверяем, что нет бесконечной рекурсии
        assert len(log) < 20, "Не должно быть бесконечной рекурсии"
        assert 'h1_start' in log
        assert 'h2_start' in log