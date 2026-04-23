import pytest
from unittest.mock import MagicMock
import client.src.core.bus.registry
import client.src.core.event_bus
import client.src.core.bus.weak_callback


# В tests/conftest.py

@pytest.fixture(autouse=True)
def mock_logger():  # ← переименовали с mock_all_loggers на mock_logger
    """
    Напрямую подменяет объекты log во всех модулях.
    """
    # Создаем мок-экземпляр
    mock_instance = MagicMock()
    mock_instance.error = MagicMock()
    mock_instance.warning = MagicMock()
    mock_instance.info = MagicMock()
    mock_instance.debug = MagicMock()
    mock_instance.success = MagicMock()
    mock_instance.api = MagicMock()
    mock_instance.data = MagicMock()
    mock_instance.cache = MagicMock()
    
    # Сохраняем оригинальные логгеры
    import client.src.core.bus.registry
    import client.src.core.event_bus
    import client.src.core.bus.weak_callback
    
    original_registry_log = client.src.core.bus.registry.log
    original_event_bus_log = client.src.core.event_bus.log
    original_weak_log = client.src.core.bus.weak_callback.log
    
    # Подменяем на мок
    client.src.core.bus.registry.log = mock_instance
    client.src.core.event_bus.log = mock_instance
    client.src.core.bus.weak_callback.log = mock_instance
    
    try:
        # Возвращаем мок для проверок
        yield mock_instance
    finally:
        # Восстанавливаем оригиналы после теста
        client.src.core.bus.registry.log = original_registry_log
        client.src.core.event_bus.log = original_event_bus_log
        client.src.core.bus.weak_callback.log = original_weak_log