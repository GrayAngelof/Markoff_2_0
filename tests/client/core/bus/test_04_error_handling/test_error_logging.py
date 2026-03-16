# tests/client/core/bus/test_04_error_handling/test_error_logging.py
"""Тест логирования ошибок в EventBus."""
import pytest
from unittest.mock import Mock, patch, call

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestErrorLogging:
    """Тестирует логирование ошибок в обработчиках событий."""

    @patch('client.src.core.event_bus.log')
    def test_error_is_logged(self, mock_log):
        """Проверяет, что ошибка логируется."""
        # Arrange
        event_bus = EventBus()
        
        def failing_handler(event):
            raise ValueError("Тестовая ошибка")
        
        event_bus.subscribe('log_test', failing_handler)
        
        # Сбрасываем счётчик вызовов перед Act
        mock_log.reset_mock()
        
        # Act
        event_bus.emit('log_test')
        
        # Assert
        mock_log.error.assert_called_once()
        error_message = mock_log.error.call_args[0][0]
        assert "Ошибка в обработчике для log_test" in error_message
        assert "ValueError" in error_message or "Тестовая ошибка" in error_message

    @patch('client.src.core.event_bus.log')
    def test_multiple_errors_are_logged(self, mock_log):
        """Проверяет логирование нескольких ошибок."""
        # Arrange
        event_bus = EventBus()
        
        def failing_handler1(event):
            raise ValueError("Ошибка 1")
        
        def failing_handler2(event):
            raise RuntimeError("Ошибка 2")
        
        def normal_handler(event):
            pass
        
        event_bus.subscribe('multi_log', failing_handler1)
        event_bus.subscribe('multi_log', failing_handler2)
        event_bus.subscribe('multi_log', normal_handler)
        
        # Сбрасываем счётчик вызовов перед Act
        mock_log.reset_mock()
        
        # Act
        event_bus.emit('multi_log')
        
        # Assert
        assert mock_log.error.call_count == 2, f"Ожидалось 2 вызова error, получено {mock_log.error.call_count}"
        
        # Получаем все сообщения об ошибках
        error_messages = [call_args[0][0] for call_args in mock_log.error.call_args_list]
        
        # Выводим отладочную информацию
        print(f"\nЗалогированные сообщения: {error_messages}")
        
        # Проверяем наличие обоих типов ошибок
        value_error_found = any("ValueError" in msg for msg in error_messages)
        runtime_error_found = any("RuntimeError" in msg for msg in error_messages)
        
        # Если не нашли по типу, проверяем по тексту ошибки
        if not value_error_found:
            value_error_found = any("Ошибка 1" in msg for msg in error_messages)
        if not runtime_error_found:
            runtime_error_found = any("Ошибка 2" in msg for msg in error_messages)
        
        assert value_error_found, f"ValueError/Ошибка 1 не найдены в сообщениях: {error_messages}"
        assert runtime_error_found, f"RuntimeError/Ошибка 2 не найдены в сообщениях: {error_messages}"

    @patch('client.src.core.event_bus.log')
    def test_error_logging_with_different_exception_types(self, mock_log):
        """Проверяет логирование разных типов исключений."""
        # Arrange
        event_bus = EventBus()
        
        def value_error_handler(event):
            raise ValueError("Value error")
        
        def type_error_handler(event):
            raise TypeError("Type error")
        
        def key_error_handler(event):
            raise KeyError("Key error")
        
        event_bus.subscribe('type_test', value_error_handler)
        event_bus.subscribe('type_test', type_error_handler)
        event_bus.subscribe('type_test', key_error_handler)
        
        # Сбрасываем счётчик вызовов перед Act
        mock_log.reset_mock()
        
        # Act
        event_bus.emit('type_test')
        
        # Assert
        assert mock_log.error.call_count == 3, f"Ожидалось 3 вызова error, получено {mock_log.error.call_count}"
        
        # Получаем все сообщения об ошибках
        error_messages = [call_args[0][0] for call_args in mock_log.error.call_args_list]
        
        # Выводим отладочную информацию
        print(f"\nЗалогированные сообщения: {error_messages}")
        
        # Проверяем, что все типы ошибок залогированы (по названию исключения или по тексту)
        value_error_found = any("ValueError" in msg for msg in error_messages)
        type_error_found = any("TypeError" in msg for msg in error_messages)
        key_error_found = any("KeyError" in msg for msg in error_messages)
        
        # Если не нашли по типу, проверяем по тексту ошибки
        if not value_error_found:
            value_error_found = any("Value error" in msg for msg in error_messages)
        if not type_error_found:
            type_error_found = any("Type error" in msg for msg in error_messages)
        if not key_error_found:
            key_error_found = any("Key error" in msg for msg in error_messages)
        
        assert value_error_found, f"ValueError не найден в сообщениях: {error_messages}"
        assert type_error_found, f"TypeError не найден в сообщениях: {error_messages}"
        assert key_error_found, f"KeyError не найден в сообщениях: {error_messages}"

    @patch('client.src.core.event_bus.log')
    def test_error_logging_preserves_event_type_info(self, mock_log):
        """Проверяет, что в лог попадает информация о типе события."""
        # Arrange
        event_bus = EventBus()
        
        def failing_handler(event):
            raise Exception("Ошибка")
        
        event_type = "custom.event.type"
        event_bus.subscribe(event_type, failing_handler)
        
        # Сбрасываем счётчик вызовов перед Act
        mock_log.reset_mock()
        
        # Act
        event_bus.emit(event_type, {"test": "data"})
        
        # Assert
        mock_log.error.assert_called_once()
        error_message = mock_log.error.call_args[0][0]
        assert event_type in error_message, f"Тип события {event_type} должен быть в сообщении об ошибке: {error_message}"

    @patch('client.src.core.event_bus.log')
    def test_no_logging_when_no_errors(self, mock_log):
        """Проверяет, что при отсутствии ошибок логи не пишутся."""
        # Arrange
        event_bus = EventBus()
        
        def normal_handler(event):
            pass
        
        event_bus.subscribe('no_error', normal_handler)
        
        # Сбрасываем счётчик вызовов перед Act
        mock_log.reset_mock()
        
        # Act
        event_bus.emit('no_error')
        
        # Assert
        mock_log.error.assert_not_called()

    @patch('client.src.core.event_bus.log')
    def test_debug_logging_for_dead_subscribers(self, mock_log):
        """Проверяет debug-логирование при очистке мёртвых подписчиков."""
        # Arrange
        event_bus = EventBus()
        
        # Создаём временный объект, который будет удалён
        class TempHandler:
            def handle(self, event):
                pass
        
        temp = TempHandler()
        event_bus.subscribe('cleanup_test', temp.handle)
        
        # Удаляем объект
        del temp
        import gc
        gc.collect()
        
        # Настраиваем мок для debug-лога
        from client.src.core.event_bus import Logger
        
        # Сбрасываем счётчик вызовов перед Act
        mock_log.reset_mock()
        
        with patch.object(Logger, 'is_debug_enabled', return_value=True):
            # Act
            event_bus.emit('cleanup_test')
            
            # Assert
            # Должен быть хотя бы один вызов debug
            assert mock_log.debug.called, "Должен быть debug-лог об очистке"
            
            # Проверяем, что сообщение содержит информацию об очистке
            if mock_log.debug.call_args_list:
                debug_messages = [call_args[0][0] for call_args in mock_log.debug.call_args_list]
                print(f"\nDebug сообщения: {debug_messages}")
                
                cleanup_found = any(
                    "удалено" in msg.lower() or 
                    "dead" in msg.lower() or 
                    "мёртв" in msg.lower() or
                    "очистк" in msg.lower()
                    for msg in debug_messages
                )
                assert cleanup_found, f"Должно быть сообщение об удалении мёртвых подписчиков: {debug_messages}"