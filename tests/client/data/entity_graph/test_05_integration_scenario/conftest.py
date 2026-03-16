"""
Общие фикстуры для всех интеграционных тестов.
"""
import pytest
from client.src.data import EntityGraph
from client.src.models import Complex, Building, Floor, Room


@pytest.fixture
def complex_1():
    """Комплекс 1."""
    return Complex(id=1, name="Северный жилой комплекс", 
                   buildings_count=2, address="ул. Северная, 1")


@pytest.fixture
def complex_2():
    """Комплекс 2 (для проверки изоляции)."""
    return Complex(id=2, name="Южный жилой комплекс", 
                   buildings_count=1, address="ул. Южная, 10")


@pytest.fixture
def building_1():
    """Корпус 1 (принадлежит комплексу 1)."""
    return Building(id=1, name="Корпус А", complex_id=1, floors_count=2)


@pytest.fixture
def building_2():
    """Корпус 2 (принадлежит комплексу 1)."""
    return Building(id=2, name="Корпус Б", complex_id=1, floors_count=1)


@pytest.fixture
def building_3():
    """Корпус 3 (принадлежит комплексу 2)."""
    return Building(id=3, name="Корпус В", complex_id=2, floors_count=1)


@pytest.fixture
def floor_1():
    """Этаж 1 (принадлежит корпусу 1)."""
    return Floor(id=1, number=1, building_id=1, rooms_count=2)


@pytest.fixture
def floor_2():
    """Этаж 2 (принадлежит корпусу 1)."""
    return Floor(id=2, number=2, building_id=1, rooms_count=1)


@pytest.fixture
def floor_3():
    """Этаж 3 (принадлежит корпусу 2)."""
    return Floor(id=3, number=1, building_id=2, rooms_count=1)


@pytest.fixture
def floor_4():
    """Этаж 4 (принадлежит корпусу 3)."""
    return Floor(id=4, number=1, building_id=3, rooms_count=1)


@pytest.fixture
def room_101():
    """Комната 101 (принадлежит этажу 1)."""
    return Room(id=1, number="101", floor_id=1, area=45.5, status_code="free")


@pytest.fixture
def room_102():
    """Комната 102 (принадлежит этажу 1)."""
    return Room(id=2, number="102", floor_id=1, area=52.0, status_code="occupied")


@pytest.fixture
def room_201():
    """Комната 201 (принадлежит этажу 2)."""
    return Room(id=3, number="201", floor_id=2, area=38.5, status_code="reserved")


@pytest.fixture
def room_301():
    """Комната 301 (принадлежит этажу 3)."""
    return Room(id=4, number="301", floor_id=3, area=60.0, status_code="free")


@pytest.fixture
def room_401():
    """Комната 401 (принадлежит этажу 4)."""
    return Room(id=5, number="401", floor_id=4, area=42.0, status_code="maintenance")


@pytest.fixture
def full_graph(request, entity_graph, complex_1, complex_2, building_1, building_2, building_3,
               floor_1, floor_2, floor_3, floor_4, room_101, room_102, room_201, 
               room_301, room_401):
    """
    Создаёт полную тестовую иерархию:
    
    Complex 1
    ├── Building 1
    │   ├── Floor 1
    │   │   ├── Room 101
    │   │   └── Room 102
    │   └── Floor 2
    │       └── Room 201
    └── Building 2
        └── Floor 3
            └── Room 301
    
    Complex 2
    └── Building 3
        └── Floor 4
            └── Room 401
    """
    # Добавляем комплексы
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(complex_2)
    
    # Добавляем корпуса
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    entity_graph.add_or_update(building_3)
    
    # Добавляем этажи
    entity_graph.add_or_update(floor_1)
    entity_graph.add_or_update(floor_2)
    entity_graph.add_or_update(floor_3)
    entity_graph.add_or_update(floor_4)
    
    # Добавляем комнаты
    entity_graph.add_or_update(room_101)
    entity_graph.add_or_update(room_102)
    entity_graph.add_or_update(room_201)
    entity_graph.add_or_update(room_301)
    entity_graph.add_or_update(room_401)
    
    # Если запрошена очистка после теста
    def cleanup():
        entity_graph.clear()
    request.addfinalizer(cleanup)
    
    return entity_graph