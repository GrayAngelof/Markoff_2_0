"""
Тест: проверка изменений сущности (внутренний метод _has_changed).
"""
import pytest
from client.src.models import Complex, Building, Floor, Room


def test_has_changed_different_objects(entity_graph):
    """Проверяет, что разные объекты определяются как изменённые."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=1, name="Комплекс 2", buildings_count=3, address="Адрес 2")
    
    # Act
    result = entity_graph._has_changed(complex_1, complex_2)
    
    # Assert
    assert result is True


def test_has_changed_same_object(entity_graph):
    """Проверяет, что один и тот же объект не считается изменённым."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    
    # Act
    result = entity_graph._has_changed(complex_1, complex_1)
    
    # Assert
    assert result is False


def test_has_changed_identical_values(entity_graph):
    """Проверяет, что объекты с одинаковыми значениями не считаются изменёнными."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    
    # Act
    result = entity_graph._has_changed(complex_1, complex_2)
    
    # Assert
    assert result is False


def test_has_changed_single_field(entity_graph):
    """Проверяет, что изменение одного поля обнаруживается."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=1, name="Комплекс 1", buildings_count=3, address="Адрес 1")  # Изменён buildings_count
    
    # Act
    result = entity_graph._has_changed(complex_1, complex_2)
    
    # Assert
    assert result is True


def test_has_changed_different_types(entity_graph):
    """Проверяет сравнение объектов разных типов."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    # Act
    result = entity_graph._has_changed(complex_1, building_1)
    
    # Assert - разные типы всегда считаются изменёнными
    assert result is True


def test_has_changed_with_none(entity_graph):
    """Проверяет сравнение с None."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    
    # Act
    result = entity_graph._has_changed(complex_1, None)
    
    # Assert
    assert result is True