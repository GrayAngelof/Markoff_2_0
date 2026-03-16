# tests/client/core/bus/test_04_error_handling/test_error_propagation.py
"""Тест распространения ошибок в EventBus."""
import pytest
from unittest.mock import Mock, patch
import gc

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestErrorPropagation:
    """Тестирует распространение ошибок в EventBus."""

    def test_error_doesnt_propagate_to_caller(self):
        """Проверяет, что ошибки не распространяются на вызывающий код."""
        # Arrange
        event_bus = EventBus()
        
        def failing_handler(event):
            raise ValueError("Ошибка в обработчике")
        
        event_bus.subscribe('propagation_test', failing_handler)
        
        # Act & Assert - emit не должен выбрасывать исключение
        try:
            event_bus.emit('propagation_test')
        except Exception:
            pytest.fail("emit не должен пробрасывать исключения из обработчиков")

    def test_errors_isolated_between_different_events(self):
        """Проверяет изоляцию ошибок между разными событиями."""
        # Arrange
        event_bus = EventBus()
        normal_event_called = False
        
        def failing_handler(event):
            raise ValueError("Ошибка")
        
        def normal_handler(event):
            nonlocal normal_event_called
            normal_event_called = True
        
        event_bus.subscribe('failing_event', failing_handler)
        event_bus.subscribe('normal_event', normal_handler)
        
        # Act
        event_bus.emit('failing_event')  # Это вызывает ошибку, но не пробрасывает её
        event_bus.emit('normal_event')
        
        # Assert
        assert normal_event_called, "Нормальное событие должно быть обработано"

    def test_errors_isolated_between_different_emits_same_event(self):
        """Проверяет изоляцию ошибок между разными испусканиями одного события."""
        # Arrange
        event_bus = EventBus()
        call_count = 0
        
        def sometimes_failing_handler(event):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:  # Каждый чётный вызов падает
                raise ValueError(f"Ошибка при вызове {call_count}")
        
        event_bus.subscribe('cyclic_test', sometimes_failing_handler)
        
        # Act - несколько emit подряд
        for _ in range(5):
            event_bus.emit('cyclic_test')
        
        # Assert - проверяем, что все emit выполнились
        assert call_count == 5, "Все 5 emit должны быть обработаны"

    def test_subscribe_with_invalid_callback(self):
        """Проверяет подписку с невалидным callback'ом."""
        # Arrange
        event_bus = EventBus()
        
        # Act & Assert - подписка с невызываемым объектом должна вызвать ошибку
        # Используем ignore, чтобы обойти проверку типов для теста
        with pytest.raises(TypeError):
            event_bus.subscribe('test_event', "not callable")  # type: ignore
        
        with pytest.raises(TypeError):
            event_bus.subscribe('test_event', 42)  # type: ignore
        
        with pytest.raises(TypeError):
            event_bus.subscribe('test_event', None)  # type: ignore

    def test_subscribe_with_method_of_deleted_object(self):
        """Проверяет подписку с методом уже удалённого объекта."""
        # Arrange
        event_bus = EventBus()
        
        class Temp:
            def handler(self, event):
                # Этот метод не должен быть вызван
                assert False, "Метод мёртвого объекта не должен вызываться"
                pass
        
        temp = Temp()
        method = temp.handler
        del temp  # Удаляем объект
        
        # Форсируем сборку мусора
        gc.collect()
        
        # Act - подписываемся на метод мёртвого объекта
        event_bus.subscribe('dead_test', method)
        
        # Assert - emit не должен вызывать ошибок, метод просто не вызовется
        try:
            event_bus.emit('dead_test')
        except Exception as e:
            pytest.fail(f"Подписка на мёртвый метод вызвала ошибку: {e}")

    def test_subscribe_with_function_then_delete(self):
        """Проверяет подписку на функцию, которая потом удаляется."""
        # Arrange
        event_bus = EventBus()
        called = False
        
        def dynamic_function(event):
            nonlocal called
            called = True
        
        # Подписываемся
        event_bus.subscribe('dynamic_test', dynamic_function)
        
        # Удаляем функцию
        del dynamic_function
        gc.collect()
        
        # Act - испускаем событие
        event_bus.emit('dynamic_test')
        
        # Assert - функция не должна быть вызвана
        assert not called, "Удалённая функция не должна вызываться"

    def test_subscribe_with_lambda_and_delete(self):
        """Проверяет подписку на лямбду, которая потом удаляется."""
        # Arrange
        event_bus = EventBus()
        result = []
        
        # Создаём лямбду и подписываемся
        lambda_func = lambda e: result.append(1)
        event_bus.subscribe('lambda_test', lambda_func)
        
        # Удаляем лямбду
        del lambda_func
        gc.collect()
        
        # Act
        event_bus.emit('lambda_test')
        
        # Assert - лямбда не должна быть вызвана
        assert len(result) == 0, "Удалённая лямбда не должна вызываться"