# tests/client/core/bus/test_subscription_management/conftest.py
"""Фикстуры для тестов управления подписками."""
import pytest

from client.src.core.event_bus import EventBus


@pytest.fixture
def event_bus():
    """Создаёт чистый экземпляр EventBus для каждого теста."""
    bus = EventBus()
    yield bus
    bus.clear()


@pytest.fixture
def call_order_tracker():
    """Создаёт трекер порядка вызовов."""
    class CallTracker:
        def __init__(self):
            self.calls = []
        
        def track(self, name):
            def _tracker(event):
                self.calls.append(name)
            return _tracker
        
        def clear(self):
            self.calls.clear()
    
    return CallTracker()