"""
Общие фикстуры для тестов графа сущностей.
"""
import pytest
import sys
from pathlib import Path

# Добавляем путь к проекту для импортов
project_root = Path(__file__).parent.parent.parent.parent.parent  # Поднимаемся до Markoff_2.0/
client_src = project_root / "client" / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(client_src))

from client.src.models import Complex, Building, Floor, Room
from client.src.data import (
    EntityStore, RelationIndex, ValidityIndex, EntityGraph,
    COMPLEX, BUILDING, FLOOR, ROOM
)


@pytest.fixture
def complex_entity():
    """Фикстура комплекса."""
    return Complex(
        id=1,
        name="Тестовый комплекс",
        buildings_count=2,
        address="ул. Тестовая, 1",
        description="Тестовое описание"
    )


@pytest.fixture
def building_entity():
    """Фикстура корпуса."""
    return Building(
        id=1,
        name="Корпус А",
        complex_id=1,
        floors_count=5,
        description="Тестовый корпус"
    )


@pytest.fixture
def floor_entity():
    """Фикстура этажа."""
    return Floor(
        id=1,
        number=1,
        building_id=1,
        rooms_count=10,
        description="Тестовый этаж"
    )


@pytest.fixture
def room_entity():
    """Фикстура комнаты."""
    return Room(
        id=1,
        number="101",
        floor_id=1,
        area=25.5,
        status_code="free",
        description="Тестовая комната"
    )


@pytest.fixture
def another_complex():
    """Другой комплекс для тестов."""
    return Complex(
        id=2,
        name="Другой комплекс",
        buildings_count=1,
        address="ул. Другая, 2"
    )


@pytest.fixture
def another_building():
    """Другой корпус для тестов."""
    return Building(
        id=2,
        name="Корпус Б",
        complex_id=1,
        floors_count=3
    )


@pytest.fixture
def another_floor():
    """Другой этаж для тестов."""
    return Floor(
        id=2,
        number=2,
        building_id=1,
        rooms_count=5
    )


@pytest.fixture
def another_room():
    """Другая комната для тестов."""
    return Room(
        id=2,
        number="102",
        floor_id=1,
        area=30.0,
        status_code="occupied"
    )


@pytest.fixture
def entity_store():
    """Фикстура EntityStore."""
    return EntityStore()


@pytest.fixture
def relation_index():
    """Фикстура RelationIndex."""
    return RelationIndex()


@pytest.fixture
def validity_index():
    """Фикстура ValidityIndex."""
    return ValidityIndex()


@pytest.fixture
def entity_graph():
    """Фикстура EntityGraph."""
    return EntityGraph()


@pytest.fixture
def sample_hierarchy(entity_graph):
    """
    Создаёт тестовую иерархию:
    Complex#1
    └── Building#1
        └── Floor#1
            └── Room#1
    """
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=1, address="Адрес 1")
    building_1 = Building(id=1, name="Корпус 1", complex_id=1, floors_count=3)
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    room_1 = Room(id=1, number="101", floor_id=1, area=20)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(room_1)
    
    return entity_graph


@pytest.fixture
def complex_hierarchy(entity_graph):
    """
    Создаёт более сложную иерархию для тестов:
    Complex#1
    ├── Building#1
    │   ├── Floor#1
    │   │   └── Room#1
    │   └── Floor#2
    │       └── Room#2
    └── Building#2
        └── Floor#3
            └── Room#3
    """
    # Complex
    complex_1 = Complex(id=1, name="Комплекс 1", buildings_count=2, address="Адрес 1")
    entity_graph.add_or_update(complex_1)
    
    # Building 1 и его иерархия
    building_1 = Building(id=1, name="Корпус 1", complex_id=1, floors_count=2)
    entity_graph.add_or_update(building_1)
    
    floor_1 = Floor(id=1, number=1, building_id=1, rooms_count=1)
    entity_graph.add_or_update(floor_1)
    room_1 = Room(id=1, number="101", floor_id=1, area=20)
    entity_graph.add_or_update(room_1)
    
    floor_2 = Floor(id=2, number=2, building_id=1, rooms_count=1)
    entity_graph.add_or_update(floor_2)
    room_2 = Room(id=2, number="201", floor_id=2, area=25)
    entity_graph.add_or_update(room_2)
    
    # Building 2 и его иерархия
    building_2 = Building(id=2, name="Корпус 2", complex_id=1, floors_count=1)
    entity_graph.add_or_update(building_2)
    
    floor_3 = Floor(id=3, number=1, building_id=2, rooms_count=1)
    entity_graph.add_or_update(floor_3)
    room_3 = Room(id=3, number="101", floor_id=3, area=30)
    entity_graph.add_or_update(room_3)
    
    return entity_graph