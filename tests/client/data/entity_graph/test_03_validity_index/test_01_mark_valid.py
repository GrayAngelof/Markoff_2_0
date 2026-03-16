"""
Тест: пометка сущности как валидной.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM


def test_mark_valid_sets_entity_valid(validity_index):
    """Проверяет, что mark_valid() помечает сущность как валидную."""
    # Act
    validity_index.mark_valid(COMPLEX, 1)
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is True


def test_mark_valid_multiple_entities(validity_index):
    """Проверяет пометку нескольких сущностей как валидных."""
    # Act
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(COMPLEX, 2)
    validity_index.mark_valid(BUILDING, 10)
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is True
    assert validity_index.is_valid(COMPLEX, 2) is True
    assert validity_index.is_valid(BUILDING, 10) is True
    assert validity_index.is_valid(COMPLEX, 3) is False


def test_mark_valid_different_types(validity_index):
    """Проверяет пометку сущностей разных типов."""
    # Act
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(BUILDING, 1)
    validity_index.mark_valid(FLOOR, 1)
    validity_index.mark_valid(ROOM, 1)
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is True
    assert validity_index.is_valid(BUILDING, 1) is True
    assert validity_index.is_valid(FLOOR, 1) is True
    assert validity_index.is_valid(ROOM, 1) is True


def test_mark_valid_idempotent(validity_index):
    """Проверяет идемпотентность mark_valid (повторный вызов не меняет состояние)."""
    # Act
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(COMPLEX, 1)  # Повторно
    
    # Assert - должна оставаться валидной
    assert validity_index.is_valid(COMPLEX, 1) is True


def test_mark_valid_after_invalid(validity_index):
    """Проверяет, что после инвалидации можно снова сделать валидной."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_invalid(COMPLEX, 1)
    assert validity_index.is_valid(COMPLEX, 1) is False
    
    # Act
    validity_index.mark_valid(COMPLEX, 1)
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is True