"""
Тест: пометка сущности как невалидной.
"""
import pytest
from client.src.data import COMPLEX, BUILDING


def test_mark_invalid_removes_valid_status(validity_index):
    """Проверяет, что mark_invalid() убирает статус валидности."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    assert validity_index.is_valid(COMPLEX, 1) is True
    
    # Act
    result = validity_index.mark_invalid(COMPLEX, 1)
    
    # Assert
    assert result is True
    assert validity_index.is_valid(COMPLEX, 1) is False


def test_mark_invalid_on_already_invalid(validity_index):
    """Проверяет mark_invalid() на уже невалидной сущности."""
    # Act
    first_result = validity_index.mark_invalid(COMPLEX, 1)
    second_result = validity_index.mark_invalid(COMPLEX, 1)
    
    # Assert
    assert first_result is False  # Не было валидной
    assert second_result is False
    assert validity_index.is_valid(COMPLEX, 1) is False


def test_mark_invalid_only_affects_specified_entity(validity_index):
    """Проверяет, что инвалидация одной сущности не влияет на другие."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(COMPLEX, 2)
    validity_index.mark_valid(BUILDING, 10)
    
    # Act
    validity_index.mark_invalid(COMPLEX, 1)
    
    # Assert
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(COMPLEX, 2) is True
    assert validity_index.is_valid(BUILDING, 10) is True


def test_mark_invalid_returns_true_only_when_status_changes(validity_index):
    """Проверяет, что mark_invalid() возвращает True только при реальном изменении."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    
    # Act & Assert
    assert validity_index.mark_invalid(COMPLEX, 1) is True   # Было изменение
    assert validity_index.mark_invalid(COMPLEX, 1) is False  # Уже было невалидно
    assert validity_index.mark_invalid(COMPLEX, 2) is False  # Никогда не было валидным


def test_mark_invalid_on_cleared_index(validity_index):
    """Проверяет mark_invalid() после очистки индекса."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.clear()
    
    # Act
    result = validity_index.mark_invalid(COMPLEX, 1)
    
    # Assert
    assert result is False  # После clear сущность не считается валидной
    assert validity_index.is_valid(COMPLEX, 1) is False