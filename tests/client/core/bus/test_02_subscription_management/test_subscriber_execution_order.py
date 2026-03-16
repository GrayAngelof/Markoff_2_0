# tests/client/core/bus/test_subscription_management/test_subscriber_execution_order.py
"""Тест порядка выполнения подписчиков."""
import pytest
from unittest.mock import Mock

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents, ProjectionEvents


class TestSubscriberExecutionOrder:
    """Тестирует порядок выполнения подписчиков."""

    def test_subscribers_called_in_subscription_order(self):
        """Проверяет, что подписчики вызываются в порядке подписки."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def first(event):
            execution_order.append('first')
        
        def second(event):
            execution_order.append('second')
        
        def third(event):
            execution_order.append('third')
        
        # Act - подписываем в определённом порядке
        event_bus.subscribe(ProjectionEvents.TREE_UPDATED, first)
        event_bus.subscribe(ProjectionEvents.TREE_UPDATED, second)
        event_bus.subscribe(ProjectionEvents.TREE_UPDATED, third)
        
        event_bus.emit(ProjectionEvents.TREE_UPDATED)
        
        # Assert
        assert execution_order == ['first', 'second', 'third'], \
            "Подписчики должны вызываться в порядке подписки"

    def test_order_preserved_with_mixed_subscriber_types(self):
        """Проверяет сохранение порядка со смешанными типами подписчиков."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        # Обычная функция
        def func_subscriber(event):
            execution_order.append('func')
        
        # Метод класса
        class Handler:
            def method(self, event):
                execution_order.append('method')
        
        handler = Handler()
        
        # Лямбда-функция
        lambda_subscriber = lambda e: execution_order.append('lambda')
        
        # Act - подписываем в определённом порядке
        event_bus.subscribe(SystemEvents.CACHE_UPDATED, func_subscriber)
        event_bus.subscribe(SystemEvents.CACHE_UPDATED, handler.method)
        event_bus.subscribe(SystemEvents.CACHE_UPDATED, lambda_subscriber)
        
        event_bus.emit(SystemEvents.CACHE_UPDATED)
        
        # Assert
        assert execution_order == ['func', 'method', 'lambda'], \
            "Порядок должен сохраняться независимо от типа подписчика"

    def test_order_preserved_when_subscribing_after_emit(self):
        """Проверяет сохранение порядка при подписке после emit."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def existing1(event):
            execution_order.append('existing1')
        
        def existing2(event):
            execution_order.append('existing2')
        
        # Act - сначала подписываем двух
        event_bus.subscribe(UIEvents.NODE_SELECTED, existing1)
        event_bus.subscribe(UIEvents.NODE_SELECTED, existing2)
        
        # Первый emit
        event_bus.emit(UIEvents.NODE_SELECTED)
        
        # Подписываем третьего
        def new_subscriber(event):
            execution_order.append('new')
        
        event_bus.subscribe(UIEvents.NODE_SELECTED, new_subscriber)
        
        # Второй emit
        event_bus.emit(UIEvents.NODE_SELECTED)
        
        # Assert
        # Первый emit: existing1, existing2
        # Второй emit: existing1, existing2, new
        assert execution_order == ['existing1', 'existing2', 'existing1', 'existing2', 'new'], \
            "Новый подписчик должен быть вызван после существующих"

    def test_order_with_unsubscribe_and_resubscribe(self):
        """Проверяет порядок при отписке и повторной подписке."""
        # Arrange
        event_bus = EventBus()
        execution_order = []
        
        def subscriber1(event):
            execution_order.append('sub1')
        
        def subscriber2(event):
            execution_order.append('sub2')
        
        def subscriber3(event):
            execution_order.append('sub3')
        
        # Act
        unsub1 = event_bus.subscribe(SystemEvents.DATA_LOADING, subscriber1)
        event_bus.subscribe(SystemEvents.DATA_LOADING, subscriber2)
        unsub3 = event_bus.subscribe(SystemEvents.DATA_LOADING, subscriber3)
        
        # Первый emit
        event_bus.emit(SystemEvents.DATA_LOADING)
        
        # Отписываем subscriber1
        unsub1()
        
        # Второй emit
        event_bus.emit(SystemEvents.DATA_LOADING)
        
        # Отписываем subscriber3 и подписываем снова
        unsub3()
        event_bus.subscribe(SystemEvents.DATA_LOADING, subscriber3)
        
        # Третий emit
        event_bus.emit(SystemEvents.DATA_LOADING)
        
        # Assert
        # Первый: sub1, sub2, sub3
        # Второй: sub2, sub3
        # Третий: sub2, sub3 (sub3 в конце, так как подписан заново)
        expected = ['sub1', 'sub2', 'sub3', 'sub2', 'sub3', 'sub2', 'sub3']
        assert execution_order == expected

    def test_order_with_different_event_types(self):
        """Проверяет, что порядок сохраняется для каждого типа отдельно."""
        # Arrange
        event_bus = EventBus()
        order_type1 = []
        order_type2 = []
        
        def for_type1_1(e):
            order_type1.append('type1_first')
        
        def for_type1_2(e):
            order_type1.append('type1_second')
        
        def for_type2_1(e):
            order_type2.append('type2_first')
        
        def for_type2_2(e):
            order_type2.append('type2_second')
        
        # Act - подписываем вперемешку
        event_bus.subscribe(UIEvents.NODE_SELECTED, for_type1_1)
        event_bus.subscribe(SystemEvents.DATA_LOADED, for_type2_1)
        event_bus.subscribe(UIEvents.NODE_SELECTED, for_type1_2)
        event_bus.subscribe(SystemEvents.DATA_LOADED, for_type2_2)
        
        # Испускаем оба типа
        event_bus.emit(UIEvents.NODE_SELECTED)
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert
        assert order_type1 == ['type1_first', 'type1_second'], \
            "Порядок для первого типа должен сохраниться"
        assert order_type2 == ['type2_first', 'type2_second'], \
            "Порядок для второго типа должен сохраниться"