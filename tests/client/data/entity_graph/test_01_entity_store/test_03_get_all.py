"""
Тест: получение всех сущностей определённого типа.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.models import Complex, Building, Floor, Room


def test_get_all_returns_all_entities(entity_store):
    """Проверяет, что get_all() возвращает все сущности типа."""
    # Arrange - создаём три комплекса со ВСЕМИ обязательными полями
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    complex_2 = Complex(
        id=2, 
        name="К2", 
        buildings_count=3,  # Обязательное поле!
        address="А2"
    )
    complex_3 = Complex(
        id=3, 
        name="К3", 
        buildings_count=1,  # Обязательное поле!
        address="А3"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(COMPLEX, 2, complex_2)
    entity_store.put(COMPLEX, 3, complex_3)
    
    # Act
    result = entity_store.get_all(COMPLEX)
    
    # Assert
    assert len(result) == 3
    assert complex_1 in result
    assert complex_2 in result
    assert complex_3 in result


def test_get_all_returns_empty_list_for_empty_type(entity_store):
    """Проверяет, что get_all() возвращает пустой список для пустого типа."""
    # Act
    result = entity_store.get_all(BUILDING)
    
    # Assert
    assert result == []


def test_get_all_returns_only_requested_type(entity_store):
    """Проверяет, что get_all() возвращает только сущности запрошенного типа."""
    # Arrange - создаём сущности разных типов со ВСЕМИ обязательными полями
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    
    building_1 = Building(
        id=1, 
        name="Б1", 
        complex_id=1, 
        floors_count=2,  # Обязательное поле!
        description="Тестовый корпус"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(BUILDING, 1, building_1)
    
    # Act
    complexes = entity_store.get_all(COMPLEX)
    buildings = entity_store.get_all(BUILDING)
    
    # Assert
    assert len(complexes) == 1
    assert complexes[0] is complex_1
    assert len(buildings) == 1
    assert buildings[0] is building_1


def test_get_all_with_mixed_types(entity_store):
    """Проверяет get_all() для всех типов сущностей."""
    # Arrange - создаём по одной сущности каждого типа
    complex_1 = Complex(
        id=1, 
        name="Комплекс", 
        buildings_count=1,  # Обязательное поле!
        address="Адрес"
    )
    
    building_1 = Building(
        id=1, 
        name="Корпус", 
        complex_id=1, 
        floors_count=3,  # Обязательное поле!
        description="Описание корпуса"
    )
    
    floor_1 = Floor(
        id=1, 
        number=1, 
        building_id=1, 
        rooms_count=5,  # Обязательное поле!
        description="Описание этажа"
    )
    
    room_1 = Room(
        id=1, 
        number="101", 
        floor_id=1, 
        area=25.5,
        status_code="free",
        description="Описание комнаты"
    )
    
    entity_store.put(COMPLEX, 1, complex_1)
    entity_store.put(BUILDING, 1, building_1)
    entity_store.put(FLOOR, 1, floor_1)
    entity_store.put(ROOM, 1, room_1)
    
    # Act
    complexes = entity_store.get_all(COMPLEX)
    buildings = entity_store.get_all(BUILDING)
    floors = entity_store.get_all(FLOOR)
    rooms = entity_store.get_all(ROOM)
    
    # Assert
    assert len(complexes) == 1
    assert complexes[0] is complex_1
    assert len(buildings) == 1
    assert buildings[0] is building_1
    assert len(floors) == 1
    assert floors[0] is floor_1
    assert len(rooms) == 1
    assert rooms[0] is room_1
    assert entity_store.size() == 4


def test_get_all_returns_copy_not_reference(entity_store):
    """Проверяет, что get_all() возвращает копию, а не ссылку на внутреннее хранилище."""
    # Arrange
    complex_1 = Complex(
        id=1, 
        name="К1", 
        buildings_count=2,  # Обязательное поле!
        address="А1"
    )
    entity_store.put(COMPLEX, 1, complex_1)
    
    # Act
    result = entity_store.get_all(COMPLEX)
    result.clear()  # Изменяем полученный список
    
    # Assert
    assert entity_store.get_all(COMPLEX) != []  # Внутреннее хранилище не должно измениться
    assert entity_store.has(COMPLEX, 1) is True


def test_get_all_preserves_objects(entity_store):
    """Проверяет, что get_all() возвращает те же объекты, что были положены."""
    # Arrange
    original_objects = []
    for i in range(1, 4):
        complex_obj = Complex(
            id=i, 
            name=f"Комплекс {i}", 
            buildings_count=i,  # Обязательное поле!
            address=f"Адрес {i}"
        )
        entity_store.put(COMPLEX, i, complex_obj)
        original_objects.append(complex_obj)
    
    # Act
    retrieved_objects = entity_store.get_all(COMPLEX)
    
    # Assert
    for original, retrieved in zip(original_objects, retrieved_objects):
        assert retrieved is original  # Должны быть те же объекты, не копии