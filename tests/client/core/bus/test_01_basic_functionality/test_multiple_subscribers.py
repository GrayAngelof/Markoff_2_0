# tests/test_basic_functionality/test_multiple_subscribers.py
"""Тест работы с несколькими подписчиками на одно событие."""
import pytest
from unittest.mock import Mock, patch

from client.src.core.event_bus import EventBus
from client.src.core.events import SystemEvents, UIEvents


class TestMultipleSubscribers:
    """Тестирует работу с несколькими подписчиками."""

    def test_all_subscribers_receive_event(self):
        """Проверяет, что все подписчики получают событие."""
        # Arrange
        event_bus = EventBus()
        mock_callback1 = Mock()
        mock_callback2 = Mock()
        mock_callback3 = Mock()
        event_type = SystemEvents.DATA_LOADED
        test_data = {"node_type": "test", "node_id": 1}
        
        # Act
        event_bus.subscribe(event_type, mock_callback1)
        event_bus.subscribe(event_type, mock_callback2)
        event_bus.subscribe(event_type, mock_callback3)
        event_bus.emit(event_type, test_data)
        
        # Assert
        mock_callback1.assert_called_once()
        mock_callback2.assert_called_once()
        mock_callback3.assert_called_once()
        
        # Проверяем, что все получили одинаковые данные
        event1 = mock_callback1.call_args[0][0]
        event2 = mock_callback2.call_args[0][0]
        event3 = mock_callback3.call_args[0][0]
        assert event1['data'] == event2['data'] == event3['data'] == test_data

    def test_subscriber_order_preservation(self):
        """Проверяет, что подписчики вызываются в порядке подписки."""
        # Arrange
        event_bus = EventBus()
        call_order = []
        
        def subscriber1(event):
            call_order.append(1)
        
        def subscriber2(event):
            call_order.append(2)
        
        def subscriber3(event):
            call_order.append(3)
        
        event_type = SystemEvents.CONNECTION_CHANGED
        
        # Act
        event_bus.subscribe(event_type, subscriber1)
        event_bus.subscribe(event_type, subscriber2)
        event_bus.subscribe(event_type, subscriber3)
        event_bus.emit(event_type)
        
        # Assert
        assert call_order == [1, 2, 3]

    def test_one_subscriber_error_doesnt_affect_others(self):
        """Проверяет, что ошибка в одном подписчике не блокирует других."""
        # Arrange
        event_bus = EventBus()
        mock_callback1 = Mock(side_effect=Exception("Test error"))
        mock_callback2 = Mock()
        mock_callback3 = Mock()
        event_type = UIEvents.TAB_CHANGED
        
        # Act
        event_bus.subscribe(event_type, mock_callback1)
        event_bus.subscribe(event_type, mock_callback2)
        event_bus.subscribe(event_type, mock_callback3)
        
        # Эмитируем событие - не должно быть исключения
        try:
            event_bus.emit(event_type, {"tab_index": 1})
        except Exception:
            pytest.fail("EventBus не должен пробрасывать исключения из обработчиков")
        
        # Assert
        mock_callback1.assert_called_once()  # Вызвался, но упал
        mock_callback2.assert_called_once()  # Должен быть вызван
        mock_callback3.assert_called_once()  # Должен быть вызван

    def test_error_logging(self, mock_logger):  # используем фикстуру, а не @patch
        """Проверяет, что ошибки в обработчиках логируются."""
        # Arrange
        event_bus = EventBus()
        error_message = "Critical error in handler"

        def failing_handler(event):
            raise ValueError(error_message)

        event_bus.subscribe(SystemEvents.DATA_ERROR, failing_handler)

        # Сбрасываем счётчик вызовов перед Act
        mock_logger.reset_mock()

        # Act
        event_bus.emit(SystemEvents.DATA_ERROR, {"error": "test"})

        # Assert
        mock_logger.error.assert_called_once()