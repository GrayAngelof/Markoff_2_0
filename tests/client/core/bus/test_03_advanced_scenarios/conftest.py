# tests/client/core/bus/test_advanced_scenarios/conftest.py
"""Фикстуры для тестов расширенных сценариев."""
import pytest

from client.src.core.event_bus import EventBus


@pytest.fixture
def event_bus():
    """Создаёт чистый экземпляр EventBus для каждого теста."""
    bus = EventBus()
    yield bus
    bus.clear()


@pytest.fixture
def order_tracker():
    """Создаёт трекер порядка выполнения."""
    class OrderTracker:
        def __init__(self):
            self.order = []
        
        def track(self, name):
            def _tracker(event):
                self.order.append(name)
            return _tracker
        
        def clear(self):
            self.order.clear()
    
    return OrderTracker()