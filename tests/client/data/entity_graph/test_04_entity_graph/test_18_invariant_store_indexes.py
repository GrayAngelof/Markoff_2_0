"""
Инвариант 2: Консистентность хранилища и индексов.

Если entity в store, то:
1. entity должен иметь корректные индексы в RelationIndex (если есть родитель)
2. entity должен иметь корректный статус в ValidityIndex
3. Для родителей - дети должны существовать в store
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_invariant_entity_in_store_has_parent_index(entity_graph):
    """Проверяет, что сущность в store имеет индекс родителя (если должен)."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Assert - building в store
    assert entity_graph._store.has(BUILDING, 1) is True
    
    # Должен иметь индекс родителя
    parent = entity_graph._relations.get_parent(BUILDING, 1)
    assert parent is not None
    assert parent == (COMPLEX, 1)


def test_invariant_entity_in_store_has_validity_flag(entity_graph):
    """Проверяет, что сущность в store имеет флаг валидности."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    
    # Act
    entity_graph.add_or_update(complex_1)
    
    # Assert
    assert entity_graph._store.has(COMPLEX, 1) is True
    assert entity_graph._validity.is_valid(COMPLEX, 1) is True


def test_invariant_root_in_store_no_parent(entity_graph):
    """Проверяет, что корневая сущность в store не имеет родителя."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    entity_graph.add_or_update(complex_1)
    
    # Assert
    assert entity_graph._store.has(COMPLEX, 1) is True
    assert entity_graph._relations.get_parent(COMPLEX, 1) is None


def test_invariant_parent_children_exist_in_store(entity_graph):
    """Проверяет, что все дети родителя существуют в store."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=4)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    
    # Assert - все дети complex существуют в store
    children = entity_graph._relations.get_children(COMPLEX, 1)
    for child_id in children:
        assert entity_graph._store.has(BUILDING, child_id) is True


def test_invariant_after_update_indexes_updated(entity_graph):
    """Проверяет, что после обновления сущности индексы актуальны."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    complex_2 = Complex(id=2, name="Комплекс 2", buildings_count=1, address="Адрес 2")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(complex_2)
    entity_graph.add_or_update(building_1)
    
    # Act - обновляем building, меняем родителя
    updated_building = Building(id=1, name="Корпус", complex_id=2, floors_count=3)
    entity_graph.add_or_update(updated_building)
    
    # Assert - building всё ещё в store
    assert entity_graph._store.has(BUILDING, 1) is True
    
    # Индекс родителя обновился
    assert entity_graph._relations.get_parent(BUILDING, 1) == (COMPLEX, 2)
    
    # Флаг валидности должен быть True (после обновления)
    assert entity_graph._validity.is_valid(BUILDING, 1) is True


def test_invariant_after_remove_entity_not_in_indexes(entity_graph):
    """Проверяет, что после удаления сущности она исчезает из всех индексов."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act - удаляем building
    entity_graph.remove(BUILDING, 1, cascade=True)
    
    # Assert - building нет в store
    assert entity_graph._store.has(BUILDING, 1) is False
    
    # Нет в parents индексе
    assert entity_graph._relations.get_parent(BUILDING, 1) is None
    
    # Нет в validity индексе
    assert entity_graph._validity.is_valid(BUILDING, 1) is False
    
    # Не должен быть в children у complex
    assert 1 not in entity_graph._relations.get_children(COMPLEX, 1)


def test_invariant_after_clear_no_entities_in_indexes(entity_graph):
    """Проверяет, что после clear нет сущностей нигде."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Act
    entity_graph.clear()
    
    # Assert - store пуст
    assert entity_graph._store.size() == 0
    
    # relations пусты
    assert entity_graph._relations.get_all_relations()['children_set'] == {}
    assert entity_graph._relations.get_all_relations()['children_sorted'] == {}
    assert entity_graph._relations.get_all_relations()['parents'] == {}
    
    # validity пуст (проверяем через is_valid)
    assert entity_graph._validity.is_valid(COMPLEX, 1) is False
    assert entity_graph._validity.is_valid(BUILDING, 1) is False