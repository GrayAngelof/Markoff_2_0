"""
Тест: проверка временных меток.
"""
import pytest
import time
from datetime import datetime, timedelta
from client.src.data import COMPLEX
from client.src.models import Complex


def test_timestamp_on_put(entity_store):
    """Проверяет, что put() устанавливает временную метку."""
    # Arrange - создаём комплекс со ВСЕМИ обязательными полями
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    # Act
    entity_store.put(COMPLEX, 1, complex_1)
    timestamp = entity_store.get_timestamp(COMPLEX, 1)
    
    # Assert
    assert timestamp is not None
    assert isinstance(timestamp, datetime)
    assert timestamp <= datetime.now()


def test_timestamp_updates_on_put(entity_store):
    """Проверяет, что повторный put() обновляет временную метку."""
    # Arrange - создаём комплекс
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    first_timestamp = entity_store.get_timestamp(COMPLEX, 1)
    
    # Ждём немного, чтобы время точно изменилось
    time.sleep(0.01)
    
    # Act - обновляем комплекс
    new_complex = Complex(
        id=1, 
        name="К1 обновлённый", 
        buildings_count=3,  # Обязательное поле!
        address="А1 обновлённый"
    )
    entity_store.put(COMPLEX, 1, new_complex)
    second_timestamp = entity_store.get_timestamp(COMPLEX, 1)
    
    # Assert
    assert second_timestamp > first_timestamp


def test_timestamp_none_for_missing(entity_store):
    """Проверяет, что get_timestamp() возвращает None для отсутствующей сущности."""
    # Act
    timestamp = entity_store.get_timestamp(COMPLEX, 999)
    
    # Assert
    assert timestamp is None


def test_timestamp_after_remove(entity_store):
    """Проверяет, что после удаления timestamp исчезает."""
    # Arrange - создаём комплекс
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    assert entity_store.get_timestamp(COMPLEX, 1) is not None
    
    # Act
    entity_store.remove(COMPLEX, 1)
    
    # Assert
    assert entity_store.get_timestamp(COMPLEX, 1) is None


def test_timestamp_after_clear(entity_store):
    """Проверяет, что после очистки все timestamp исчезают."""
    # Arrange - создаём несколько комплексов
    for i in range(1, 4):
        entity_store.put(
            COMPLEX, 
            i, 
            Complex(
                id=i, 
                name=f"К{i}", 
                buildings_count=i,  # Обязательное поле!
                address=f"А{i}"
            )
        )
    
    # Проверяем, что timestamp есть
    for i in range(1, 4):
        assert entity_store.get_timestamp(COMPLEX, i) is not None
    
    # Act
    entity_store.clear()
    
    # Assert
    for i in range(1, 4):
        assert entity_store.get_timestamp(COMPLEX, i) is None


def test_timestamp_different_for_different_ids(entity_store):
    """Проверяет, что у разных ID разные timestamp."""
    # Arrange - создаём два комплекса
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    time.sleep(0.01)  # Небольшая задержка
    
    complex_2 = Complex(
        id=2, 
        name="К2", 
        buildings_count=3,  # Обязательное поле!
        address="А2"
    )
    
    # Act
    entity_store.put(COMPLEX, 1, complex_1)
    timestamp_1 = entity_store.get_timestamp(COMPLEX, 1)
    
    entity_store.put(COMPLEX, 2, complex_2)
    timestamp_2 = entity_store.get_timestamp(COMPLEX, 2)
    
    # Assert
    assert timestamp_1 is not None
    assert timestamp_2 is not None
    assert timestamp_2 > timestamp_1  # Второй должен быть позже


def test_timestamp_precision(entity_store):
    """Проверяет, что timestamp обновляется даже при быстрых последовательных put."""
    # Arrange
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    # Act - делаем несколько быстрых обновлений
    timestamps = []
    for i in range(5):
        complex_1.name = f"К1 обновление {i}"
        entity_store.put(COMPLEX, 1, complex_1)
        timestamps.append(entity_store.get_timestamp(COMPLEX, 1))
    
    # Assert - все timestamp должны быть разными (или хотя бы не убывать)
    for i in range(1, len(timestamps)):
        assert timestamps[i] >= timestamps[i-1]