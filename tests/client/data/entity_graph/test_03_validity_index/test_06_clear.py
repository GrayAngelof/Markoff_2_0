"""
Тест: очистка индекса валидности.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR


def test_clear_removes_all_valid_flags(validity_index):
    """Проверяет, что clear() удаляет все флаги валидности."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(COMPLEX, 2)
    validity_index.mark_valid(BUILDING, 10)
    
    # Act
    validity_index.clear()
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(COMPLEX, 2) is False
    assert validity_index.is_valid(BUILDING, 10) is False


def test_clear_on_empty_index(validity_index):
    """Проверяет clear() на пустом индексе."""
    # Act & Assert (не должно быть исключений)
    validity_index.clear()
    
    # Проверяем, что всё ещё пусто
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(BUILDING, 1) is False


def test_clear_after_operations(validity_index):
    """Проверяет clear() после различных операций."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_invalid(COMPLEX, 1)
    validity_index.mark_valid(COMPLEX, 2)
    
    # Act
    validity_index.clear()
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(COMPLEX, 2) is False


def test_clear_twice(validity_index):
    """Проверяет повторный clear()."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    
    # Act
    validity_index.clear()
    validity_index.clear()  # Второй раз
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is False


def test_clear_and_add_new(validity_index):
    """Проверяет, что после clear() можно добавлять новые валидные сущности."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.clear()
    
    # Act
    validity_index.mark_valid(COMPLEX, 2)
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(COMPLEX, 2) is True