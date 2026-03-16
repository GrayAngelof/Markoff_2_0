"""
Тест: проверка валидности сущности.
"""
import pytest
from client.src.data import COMPLEX, BUILDING


def test_is_valid_returns_true_for_valid_entity(validity_index):
    """Проверяет, что is_valid() возвращает True для валидной сущности."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    
    # Act
    result = validity_index.is_valid(COMPLEX, 1)
    
    # Assert
    assert result is True


def test_is_valid_returns_false_for_invalid_entity(validity_index):
    """Проверяет, что is_valid() возвращает False для невалидной сущности."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_invalid(COMPLEX, 1)
    
    # Act
    result = validity_index.is_valid(COMPLEX, 1)
    
    # Assert
    assert result is False


def test_is_valid_returns_false_for_never_marked(validity_index):
    """Проверяет, что is_valid() возвращает False для никогда не помеченной сущности."""
    # Act
    result = validity_index.is_valid(COMPLEX, 999)
    
    # Assert
    assert result is False


def test_is_valid_after_clear(validity_index):
    """Проверяет is_valid() после очистки индекса."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(COMPLEX, 2)
    validity_index.clear()
    
    # Act & Assert
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(COMPLEX, 2) is False


def test_is_valid_for_different_types(validity_index):
    """Проверяет is_valid() для разных типов."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(BUILDING, 10)
    
    # Act & Assert
    assert validity_index.is_valid(COMPLEX, 1) is True
    assert validity_index.is_valid(BUILDING, 10) is True
    assert validity_index.is_valid(COMPLEX, 2) is False
    assert validity_index.is_valid(BUILDING, 20) is False