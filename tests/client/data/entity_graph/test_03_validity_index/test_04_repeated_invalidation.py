"""
Тест: поведение при повторной инвалидизации.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR


def test_repeated_mark_invalid_no_side_effects(validity_index):
    """Проверяет, что повторная инвалидация не имеет побочных эффектов."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(COMPLEX, 2)
    
    # Act - многократная инвалидация одной сущности
    for _ in range(5):
        validity_index.mark_invalid(COMPLEX, 1)
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(COMPLEX, 2) is True  # Другие не должны пострадать


def test_mark_valid_after_repeated_invalid(validity_index):
    """Проверяет, что после многократной инвалидации можно снова сделать валидной."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    
    # Act - много раз инвалидируем
    for _ in range(3):
        validity_index.mark_invalid(COMPLEX, 1)
    
    # Затем делаем валидной
    validity_index.mark_valid(COMPLEX, 1)
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is True


def test_interleaved_valid_invalid_operations(validity_index):
    """Проверяет чередование операций валидации/инвалидации."""
    # Act & Assert
    validity_index.mark_valid(COMPLEX, 1)
    assert validity_index.is_valid(COMPLEX, 1) is True
    
    validity_index.mark_invalid(COMPLEX, 1)
    assert validity_index.is_valid(COMPLEX, 1) is False
    
    validity_index.mark_valid(COMPLEX, 1)
    assert validity_index.is_valid(COMPLEX, 1) is True
    
    validity_index.mark_invalid(COMPLEX, 1)
    validity_index.mark_invalid(COMPLEX, 1)  # Повторно
    assert validity_index.is_valid(COMPLEX, 1) is False


def test_multiple_entities_complex_scenario(validity_index):
    """Проверяет сложный сценарий с множеством сущностей."""
    # Arrange - создаём несколько сущностей
    entities = [
        (COMPLEX, 1), (COMPLEX, 2), (BUILDING, 10), 
        (BUILDING, 20), (FLOOR, 100)
    ]
    
    for node_type, entity_id in entities:
        validity_index.mark_valid(node_type, entity_id)
    
    # Act - инвалидируем некоторые
    validity_index.mark_invalid(COMPLEX, 1)
    validity_index.mark_invalid(BUILDING, 10)
    validity_index.mark_invalid(COMPLEX, 1)  # Повторно
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(COMPLEX, 2) is True
    assert validity_index.is_valid(BUILDING, 10) is False
    assert validity_index.is_valid(BUILDING, 20) is True
    assert validity_index.is_valid(FLOOR, 100) is True