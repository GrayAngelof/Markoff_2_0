# tests/client/core/bus/test_basic_functionality/test_no_subscribers_scenario.py
"""Тест сценария без подписчиков."""
import pytest
import gc
from unittest.mock import Mock, patch

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestNoSubscribersScenario:
    """Тестирует работу EventBus при отсутствии подписчиков."""

    def test_emit_with_no_subscribers(self):
        """Проверяет, что испускание события без подписчиков не вызывает ошибок."""
        # Arrange
        event_bus = EventBus()
        
        # Act & Assert - не должно быть исключений
        try:
            event_bus.emit(UIEvents.NODE_SELECTED, {"node_id": 1})
            event_bus.emit(SystemEvents.DATA_LOADED)
            event_bus.emit("non.existent.event")
        except Exception as e:
            pytest.fail(f"Emit без подписчиков вызвал исключение: {e}")

    def test_emit_to_removed_subscribers(self):
        """Проверяет испускание события после удаления всех подписчиков."""
        # Arrange
        event_bus = EventBus()
        mock_callback = Mock()
        
        # Подписываемся и отписываемся
        unsubscribe = event_bus.subscribe(UIEvents.NODE_SELECTED, mock_callback)
        unsubscribe()
        
        # Act
        event_bus.emit(UIEvents.NODE_SELECTED)
        
        # Assert
        mock_callback.assert_not_called()

    def test_emit_to_expired_weak_refs(self):
        """Проверяет обработку мёртвых weakref-ссылок."""
        # Arrange
        event_bus = EventBus()
        
        # Создаём временный объект с методом-обработчиком
        class TempHandler:
            def handle(self, event):
                # Этот метод никогда не должен быть вызван
                assert False, "Мёртвый объект не должен получать события"
        
        temp = TempHandler()
        
        # Подписываем метод временного объекта
        event_bus.subscribe(SystemEvents.DATA_LOADING, temp.handle)
        
        # Удаляем объект и форсируем сборку мусора
        del temp
        gc.collect()
        
        # Act - испускаем событие
        # Не должно быть ошибок и вызовов
        try:
            event_bus.emit(SystemEvents.DATA_LOADING)
        except Exception as e:
            pytest.fail(f"Emit с мёртвыми ссылками вызвал исключение: {e}")

    def test_subscriber_count_with_no_subscribers(self):
        """Проверяет подсчёт подписчиков при их отсутствии."""
        # Arrange
        event_bus = EventBus()
        
        # Act
        count_for_type = event_bus.get_subscriber_count(UIEvents.NODE_SELECTED)
        all_counts = event_bus.get_subscriber_count()
        
        # Assert
        assert count_for_type == 0
        assert isinstance(all_counts, dict)
        assert len(all_counts) == 0  # Должен быть пустой словарь

    def test_emit_with_dead_subscribers_only(self):
        """Проверяет очистку мёртвых подписок при emit."""
        # Arrange
        event_bus = EventBus()
        
        # Создаём временные объекты с привязкой к локальной области видимости
        def create_subscriber_and_subscribe():
            """Создаёт подписчика и подписывает его, но не возвращает ссылку."""
            class TempSubscriber:
                def __init__(self, name):
                    self.name = name
                    self.called = False
                
                def handler(self, event):
                    self.called = True
                    # Если этот метод вызовется, тест упадёт
                    assert False, f"Мёртвый объект {self.name} не должен получать события"
            
            # Создаём объект и подписываем его
            temp = TempSubscriber("dead")
            event_bus.subscribe(SystemEvents.DATA_LOADED, temp.handler)
            # Объект temp удаляется при выходе из функции
        
        # Создаём двух "мёртвых" подписчиков через функцию
        create_subscriber_and_subscribe()
        create_subscriber_and_subscribe()
        
        # Создаём одного живого подписчика
        class LiveSubscriber:
            def __init__(self):
                self.called = False
            
            def handler(self, event):
                self.called = True
        
        live = LiveSubscriber()
        event_bus.subscribe(SystemEvents.DATA_LOADED, live.handler)
        
        # Форсируем сборку мусора
        gc.collect()
        
        # Act - испускаем событие
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert - должен остаться один живой подписчик
        count = event_bus.get_subscriber_count(SystemEvents.DATA_LOADED)
        assert count == 1, f"Ожидалось 1 живой подписчик, получено {count}"
        
        # Проверяем, что живой подписчик получил событие
        assert live.called, "Живой подписчик должен получить событие"

    def test_emit_with_all_dead_subscribers(self):
        """Проверяет очистку всех мёртвых подписок."""
        # Arrange
        event_bus = EventBus()
        
        # Создаём функцию, которая создаёт и подписывает временные объекты
        def create_dead_subscriber(name):
            """Создаёт подписчика, который умрёт после выхода из функции."""
            class TempSubscriber:
                def __init__(self, name):
                    self.name = name
                
                def handler(self, event):
                    # Этот метод никогда не должен быть вызван
                    assert False, f"Мёртвый объект {self.name} не должен получать события"
            
            temp = TempSubscriber(name)
            event_bus.subscribe(SystemEvents.DATA_LOADED, temp.handler)
            # temp удаляется при выходе из функции
        
        # Создаём трёх мёртвых подписчиков
        create_dead_subscriber("dead1")
        create_dead_subscriber("dead2")
        create_dead_subscriber("dead3")
        
        # Форсируем сборку мусора несколько раз для надёжности
        for _ in range(3):
            gc.collect()
        
        # Act - испускаем событие
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert - все подписчики должны быть мертвы
        count = event_bus.get_subscriber_count(SystemEvents.DATA_LOADED)
        assert count == 0, f"Ожидалось 0 живых подписчиков, получено {count}"

    @patch('client.src.core.event_bus.log')
    def test_logging_with_no_subscribers(self, mock_log):
        """Проверяет логирование при отсутствии подписчиков."""
        # Очищаем все предыдущие вызовы мока
        mock_log.reset_mock()
        
        # Arrange
        event_bus = EventBus()
        
        # Очищаем лог после инициализации
        mock_log.reset_mock()
        
        # Act
        event_bus.emit(SystemEvents.CONNECTION_CHANGED, {"is_online": True})
        
        # Assert
        # Проверяем, что был вызван info ровно один раз (для emit)
        mock_log.info.assert_called_once()
        assert "EMIT" in mock_log.info.call_args[0][0]
        mock_log.error.assert_not_called()

    def test_clear_all_subscriptions(self):
        """Проверяет очистку всех подписок."""
        # Arrange
        event_bus = EventBus()
        mock_callback1 = Mock()
        mock_callback2 = Mock()
        
        event_bus.subscribe(UIEvents.NODE_SELECTED, mock_callback1)
        event_bus.subscribe(SystemEvents.DATA_LOADED, mock_callback2)
        
        # Act
        event_bus.clear()
        
        # Испускаем события
        event_bus.emit(UIEvents.NODE_SELECTED)
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert
        mock_callback1.assert_not_called()
        mock_callback2.assert_not_called()
        assert event_bus.get_subscriber_count(UIEvents.NODE_SELECTED) == 0
        assert event_bus.get_subscriber_count(SystemEvents.DATA_LOADED) == 0

    def test_mixed_live_and_dead_subscribers(self):
        """Проверяет смешанный сценарий с живыми и мёртвыми подписчиками."""
        # Arrange
        event_bus = EventBus()
        
        # Функция для создания мёртвых подписчиков
        def create_dead_subscriber():
            """Создаёт мёртвого подписчика."""
            class DeadSubscriber:
                def handler(self, event):
                    assert False, "Мёртвый подписчик не должен вызываться"
            
            temp = DeadSubscriber()
            event_bus.subscribe(SystemEvents.DATA_LOADED, temp.handler)
        
        # Создаём 2 мёртвых подписчиков
        create_dead_subscriber()
        create_dead_subscriber()
        
        # Создаём живых подписчиков
        live_subscribers = []
        live_count = 3
        
        for i in range(live_count):
            class LiveSubscriber:
                def __init__(self):
                    self.called = False
                
                def handler(self, event):
                    self.called = True
            
            live = LiveSubscriber()
            event_bus.subscribe(SystemEvents.DATA_LOADED, live.handler)
            live_subscribers.append(live)
        
        # Форсируем сборку мусора
        for _ in range(3):
            gc.collect()
        
        # Act - испускаем событие
        event_bus.emit(SystemEvents.DATA_LOADED)
        
        # Assert
        count = event_bus.get_subscriber_count(SystemEvents.DATA_LOADED)
        assert count == live_count, f"Ожидалось {live_count} живых подписчиков, получено {count}"
        
        # Проверяем, что все живые подписчики получили событие
        for i, subscriber in enumerate(live_subscribers):
            assert subscriber.called, f"Живой подписчик {i} не получил событие"

    def test_weak_method_cleaning_on_gc(self):
        """Проверяет, что weakref методы очищаются при сборке мусора."""
        # Arrange
        event_bus = EventBus()
        
        # Создаём объект в локальной области видимости
        class Handler:
            def __init__(self):
                self.called = False
            
            def handle(self, event):
                self.called = True
        
        def create_and_subscribe():
            handler = Handler()
            event_bus.subscribe(SystemEvents.DATA_LOADING, handler.handle)
            return handler  # Возвращаем, но не сохраняем
        
        # Создаём и сразу теряем ссылку
        handler = create_and_subscribe()
        
        # Удаляем последнюю ссылку
        del handler
        gc.collect()
        
        # Act
        event_bus.emit(SystemEvents.DATA_LOADING)
        
        # Assert
        count = event_bus.get_subscriber_count(SystemEvents.DATA_LOADING)
        assert count == 0, "Мёртвый подписчик должен быть очищен"