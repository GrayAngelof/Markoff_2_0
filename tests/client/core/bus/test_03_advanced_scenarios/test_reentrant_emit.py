# tests/client/core/bus/test_advanced_scenarios/test_reentrant_emit.py
"""Тест вложенных (reentrant) испусканий событий."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.event_constants import UIEvents, SystemEvents, ProjectionEvents


class TestReentrantEmit:
    """Тестирует вложенные испускания событий."""

    def test_handler_emits_different_event(self):
        """Проверяет, что обработчик может испускать другое событие."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def handler_a(event):
            execution_order.append('A')
            event_bus.emit('event_b')
        
        def handler_b(event):
            execution_order.append('B')
        
        def handler_c(event):
            execution_order.append('C')
        
        # Act
        event_bus.subscribe('event_a', handler_a)
        event_bus.subscribe('event_b', handler_b)
        event_bus.subscribe('event_c', handler_c)
        
        event_bus.emit('event_a')
        event_bus.emit('event_c')
        
        # Assert
        assert execution_order == ['A', 'B', 'C'], \
            "События должны обрабатываться в порядке: A -> B -> C"

    def test_nested_emit_with_multiple_handlers(self):
        """Проверяет вложенные emit с несколькими обработчиками на каждом уровне."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def handler_a1(event):
            execution_order.append('A1')
            event_bus.emit('event_b')
        
        def handler_a2(event):
            execution_order.append('A2')
        
        def handler_b1(event):
            execution_order.append('B1')
            event_bus.emit('event_c')
        
        def handler_b2(event):
            execution_order.append('B2')
        
        def handler_c1(event):
            execution_order.append('C1')
        
        def handler_c2(event):
            execution_order.append('C2')
        
        # Act
        event_bus.subscribe('event_a', handler_a1)
        event_bus.subscribe('event_a', handler_a2)
        event_bus.subscribe('event_b', handler_b1)
        event_bus.subscribe('event_b', handler_b2)
        event_bus.subscribe('event_c', handler_c1)
        event_bus.subscribe('event_c', handler_c2)
        
        event_bus.emit('event_a')
        
        # Assert
        # Все обработчики event_a должны выполниться до начала event_b
        # Но из-за копирования списка подписчиков, event_b начнётся сразу после handler_a1
        expected = ['A1', 'B1', 'C1', 'C2', 'B2', 'A2']
        assert execution_order == expected, \
            f"Ожидалось {expected}, получено {execution_order}"

    def test_deeply_nested_emits(self):
        """Проверяет глубокую вложенность испусканий событий."""
        # Arrange
        event_bus = EventBus()
        depth_tracker = []
        
        # Создаём обработчики для каждого уровня
        def handler1(event):
            depth_tracker.append("enter_1")
            event_bus.emit("event_2")
            depth_tracker.append("exit_1")
        
        def handler2(event):
            depth_tracker.append("enter_2")
            event_bus.emit("event_3")
            depth_tracker.append("exit_2")
        
        def handler3(event):
            depth_tracker.append("enter_3")
            event_bus.emit("event_4")
            depth_tracker.append("exit_3")
        
        def handler4(event):
            depth_tracker.append("enter_4")
            depth_tracker.append("exit_4")
        
        # Подписываем обработчики
        event_bus.subscribe("event_1", handler1)
        event_bus.subscribe("event_2", handler2)
        event_bus.subscribe("event_3", handler3)
        event_bus.subscribe("event_4", handler4)
        
        # Act
        event_bus.emit("event_1")
        
        # Assert
        expected = [
            'enter_1', 'enter_2', 'enter_3', 'enter_4',
            'exit_4', 'exit_3', 'exit_2', 'exit_1'
        ]
        assert depth_tracker == expected, \
            f"Глубокие вложенные emit должны работать корректно\nОжидалось: {expected}\nПолучено: {depth_tracker}"

    def test_reentrant_emit_preserves_subscriber_order(self):
        """Проверяет, что вложенные emit сохраняют порядок подписчиков."""
        # Arrange
        event_bus = EventBus()
        order = []
        
        def outer1(event):
            order.append('outer1_start')
            event_bus.emit('inner')
            order.append('outer1_end')
        
        def outer2(event):
            order.append('outer2')
        
        def inner1(event):
            order.append('inner1')
        
        def inner2(event):
            order.append('inner2')
        
        # Act
        event_bus.subscribe('outer', outer1)
        event_bus.subscribe('outer', outer2)
        event_bus.subscribe('inner', inner1)
        event_bus.subscribe('inner', inner2)
        
        event_bus.emit('outer')
        
        # Assert
        expected = ['outer1_start', 'inner1', 'inner2', 'outer1_end', 'outer2']
        assert order == expected, \
            f"Порядок выполнения должен сохраняться: {expected}"

        def test_reentrant_emit_with_unsubscribe(self):
            """
            Проверяет отписку во время вложенных emit.
            """
            # Arrange
            event_bus = EventBus()
            order = []
            unsub_outer2 = None
            unsub_inner = None
            
            def outer1(event):
                order.append('outer1')
                # Отписываем outer2
                if unsub_outer2:
                    unsub_outer2()
                # Испускаем inner - это запустит вложенный emit немедленно
                event_bus.emit('inner')
            
            def outer2(event):
                order.append('outer2')  # Будет вызван после завершения вложенных emit
            
            def inner(event):
                order.append('inner')
                # Отписываем inner (самоотписка)
                if unsub_inner:
                    unsub_inner()
            
            # Act
            event_bus.subscribe('outer', outer1)
            unsub_outer2 = event_bus.subscribe('outer', outer2)
            unsub_inner = event_bus.subscribe('inner', inner)
            
            # Первый emit
            event_bus.emit('outer')
            
            # Второй emit - inner не должен вызываться (уже отписан)
            event_bus.emit('inner')
            
            # Assert
            # Ожидаемый порядок:
            # 1. outer1 начинает выполнение
            # 2. outer1 вызывает inner - inner выполняется немедленно
            # 3. inner завершается, управление возвращается к outer1
            # 4. outer1 завершается
            # 5. outer2 выполняется (так как он был в копии списка подписчиков)
            expected_order = ['outer1', 'inner', 'outer2']
            assert order == expected_order, \
                f"Ожидалось {expected_order}, получено {order}"
            
            # Проверяем, что второй emit inner ничего не вызывает
            order_after = []
            def tracker(event):
                order_after.append('called')
            
            event_bus.subscribe('inner', tracker)
            event_bus.emit('inner')
            assert order_after == ['called'], \
                "Новый обработчик должен вызываться, старый inner уже отписан"
            
            # Проверяем, что outer2 больше не вызывается
            order_outer_after = []
            def outer_tracker(event):
                order_outer_after.append('outer_called')
            
            event_bus.subscribe('outer', outer_tracker)
            event_bus.emit('outer')
            assert order_outer_after == ['outer_called'], \
                "Новый обработчик outer должен вызываться, outer2 уже отписан"