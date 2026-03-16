"""
Тест: обновление сущности в графе.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.models import Complex, Building


def test_update_complex_entity(entity_graph):
    """Проверяет обновление существующего комплекса."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    entity_graph.add_or_update(complex_1)
    
    # Act
    updated_complex = Complex(
        id=1, 
        name="Комплекс 1 (обновлённый)", 
        buildings_count=3, 
        address="Новый адрес"
    )
    result = entity_graph.add_or_update(updated_complex)
    
    # Assert
    assert result is True
    stored = entity_graph.get(COMPLEX, 1)
    assert stored is updated_complex
    assert stored.name == "Комплекс 1 (обновлённый)"
    assert stored.buildings_count == 3
    assert stored.address == "Новый адрес"


def test_update_building_parent(entity_graph):
    """Проверяет обновление родителя у корпуса."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=2, name="Комплекс 2", buildings_count=1, address="Адрес 2")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(complex_2)
    entity_graph.add_or_update(building_1)
    
    # Проверяем начальную связь
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
    
    # Act - меняем родителя
    updated_building = Building(id=1, name="Корпус А", complex_id=2, floors_count=3)
    result = entity_graph.add_or_update(updated_building)
    
    # Assert
    assert result is True
    assert entity_graph.get_parent(BUILDING, 1) == (COMPLEX, 2)
    
    # Проверяем индексы
    assert 1 not in entity_graph.get_children(COMPLEX, 1)  # У старого родителя нет
    assert 1 in entity_graph.get_children(COMPLEX, 2)      # У нового родителя есть


def test_update_no_changes_ignored(entity_graph):
    """Проверяет, что обновление без изменений игнорируется."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    entity_graph.add_or_update(complex_1)
    
    # Act - добавляем тот же объект (без изменений)
    result = entity_graph.add_or_update(complex_1)
    
    # Assert
    assert result is False  # Должно быть проигнорировано


def test_update_partial_fields(entity_graph):
    """Проверяет обновление только некоторых полей."""
    # Arrange
    complex_1 = Complex(
        id=1, 
        name="Комплекс 1", 
        buildings_count=2, 
        address="Адрес 1",
        description="Старое описание"
    )
    entity_graph.add_or_update(complex_1)
    
    # Act - обновляем только имя и описание
    updated_complex = Complex(
        id=1,
        name="Новое имя",
        buildings_count=2,  # Не меняется
        address="Адрес 1",   # Не меняется
        description="Новое описание"
    )
    result = entity_graph.add_or_update(updated_complex)
    
    # Assert
    assert result is True
    stored = entity_graph.get(COMPLEX, 1)
    assert stored.name == "Новое имя"
    assert stored.buildings_count == 2
    assert stored.address == "Адрес 1"
    assert stored.description == "Новое описание"


def test_update_non_existent_entity(entity_graph):
    """Проверяет обновление несуществующей сущности (работает как добавление)."""
    # Act
    complex_1 = Complex(id=999, name="Новый", buildings_count=1, address="Адрес")
    result = entity_graph.add_or_update(complex_1)
    
    # Assert
    assert result is True
    assert entity_graph.has_entity(COMPLEX, 999) is True