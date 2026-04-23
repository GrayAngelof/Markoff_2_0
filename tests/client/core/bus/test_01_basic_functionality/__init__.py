# tests/test_basic_functionality/conftest.py
"""Фикстуры для тестов базовой функциональности."""
import pytest

from client.src.core.event_bus import EventBus


@pytest.fixture
def event_bus():
    """Создаёт чистый экземпляр EventBus для каждого теста."""
    bus = EventBus()
    yield bus
    bus.clear()  # Очищаем после теста


@pytest.fixture
def sample_event_data():
    """Предоставляет стандартные тестовые данные для событий."""
    return {
        "node_type": "test_type",
        "node_id": 42,
        "data": {"key": "value"}
    }


@pytest.fixture
def event_collector():
    """Создаёт коллектор событий для проверки."""
    class EventCollector:
        def __init__(self):
            self.events = []
            self.call_count = 0
        
        def collect(self, event):
            self.events.append(event)
            self.call_count += 1
        
        def clear(self):
            self.events.clear()
            self.call_count = 0
    
    return EventCollector()