# client/tests/test_models.py
"""
Отдельный тестовый скрипт для проверки моделей
Запускается напрямую: python -m tests.test_models
"""
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room

def test_building_model():
    """Тест модели Building"""
    print("\n📋 Тестирование Building:")
    data = {"id": 3, "name": "Корпус А", "complex_id": 1, "floors_count": 4}
    building = Building.from_dict(data)
    print(f"  Создан: {repr(building)}")
    print(f"  Отображение: {building}")
    assert building.id == 3
    assert building.name == "Корпус А"
    assert building.floors_count == 4
    print("  ✅ Building OK")

def test_floor_model():
    """Тест модели Floor"""
    print("\n📋 Тестирование Floor:")
    data = {"id": 1, "number": 1, "building_id": 3, "rooms_count": 0}
    floor = Floor.from_dict(data)
    print(f"  Создан: {repr(floor)}")
    print(f"  Отображение: {floor}")
    
    # Тест отрицательных этажей
    data_basement = {"id": 2, "number": -1, "building_id": 3, "rooms_count": 0}
    basement = Floor.from_dict(data_basement)
    print(f"  Подвал: {basement}")
    
    assert floor.number == 1
    assert floor.building_id == 3
    print("  ✅ Floor OK")

def test_room_model():
    """Тест модели Room"""
    print("\n📋 Тестирование Room:")
    data = {"id": 101, "number": "101", "floor_id": 1, "area": 45.5, "status_code": "free"}
    room = Room.from_dict(data)
    print(f"  Создан: {repr(room)}")
    print(f"  Отображение: {room}")
    print(f"  Статус: {room.get_status_display()}")
    
    # Тест без опциональных полей
    data_minimal = {"id": 102, "number": "102А", "floor_id": 1}
    room_minimal = Room.from_dict(data_minimal)
    print(f"  Минимальный: {room_minimal}")
    
    assert room.id == 101
    assert room.number == "101"
    assert room.area == 45.5
    print("  ✅ Room OK")

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Запуск тестов моделей данных")
    print("=" * 50)
    
    test_building_model()
    test_floor_model()
    test_room_model()
    
    print("\n" + "=" * 50)
    print("✅ Все тесты пройдены")
    print("=" * 50)