# tests/test_models.py (дополнение)
"""
Дополнительные тесты для моделей данных
"""
import sys
import os
sys.path.append('/app')

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


def print_header(text):
    """Вывод заголовка теста"""
    print(f"\n{'='*50}")
    print(f"🧪 {text}")
    print(f"{'='*50}")


def print_success(text):
    """Вывод сообщения об успехе"""
    print(f"  ✅ {text}")


def print_info(text):
    """Вывод информационного сообщения"""
    print(f"  ℹ️ {text}")


def test_complex_model():
    """Тест модели Complex"""
    print_header("Тестирование Complex")
    
    # Тестовые данные как от API
    complex_data = {
        "id": 1,
        "name": "Фабрика Веретено",
        "buildings_count": 2
    }
    
    # Создаём модель
    complex_obj = Complex.from_dict(complex_data)
    
    # Проверяем поля
    assert complex_obj.id == 1, f"ID должен быть 1, получен {complex_obj.id}"
    assert complex_obj.name == "Фабрика Веретено", f"Name должен быть 'Фабрика Веретено', получен '{complex_obj.name}'"
    assert complex_obj.buildings_count == 2, f"buildings_count должен быть 2, получен {complex_obj.buildings_count}"
    
    print_info(f"Создан: {repr(complex_obj)}")
    print_info(f"Отображение: {complex_obj}")
    print_info(f"С корпусами: {complex_obj.display_name()}")
    
    # Тест с отсутствующим buildings_count
    minimal_data = {
        "id": 2,
        "name": "Минимальный комплекс"
    }
    minimal_complex = Complex.from_dict(minimal_data)
    assert minimal_complex.buildings_count == 0, "По умолчанию buildings_count должен быть 0"
    
    print_success("Complex модель работает корректно")
    return complex_obj


def test_building_model():
    """Тест модели Building"""
    print_header("Тестирование Building")
    
    data = {
        "id": 3,
        "name": "Корпус А",
        "complex_id": 1,
        "floors_count": 4
    }
    
    building = Building.from_dict(data)
    
    assert building.id == 3
    assert building.name == "Корпус А"
    assert building.complex_id == 1
    assert building.floors_count == 4
    
    print_info(f"Создан: {repr(building)}")
    print_info(f"Отображение: {building}")
    print_success("Building модель работает корректно")
    
    return building


def test_floor_model():
    """Тест модели Floor"""
    print_header("Тестирование Floor")
    
    data = {
        "id": 1,
        "number": 1,
        "building_id": 3,
        "rooms_count": 0
    }
    
    floor = Floor.from_dict(data)
    
    assert floor.id == 1
    assert floor.number == 1
    assert floor.building_id == 3
    assert floor.rooms_count == 0
    
    print_info(f"Создан: {repr(floor)}")
    print_info(f"Отображение: {floor}")
    print_info(f"Подвал: {Floor.from_dict({'id': 2, 'number': -1, 'building_id': 3, 'rooms_count': 0})}")
    
    # Тест отрицательного этажа
    basement = Floor.from_dict({"id": 2, "number": -1, "building_id": 3, "rooms_count": 0})
    assert str(basement) == "Подвал 1"
    
    print_success("Floor модель работает корректно")
    
    return floor


def test_room_model():
    """Тест модели Room"""
    print_header("Тестирование Room")
    
    data = {
        "id": 101,
        "number": "101",
        "floor_id": 1,
        "area": 45.5,
        "status_code": "free"
    }
    
    room = Room.from_dict(data)
    
    assert room.id == 101
    assert room.number == "101"
    assert room.floor_id == 1
    assert room.area == 45.5
    assert room.status_code == "free"
    
    print_info(f"Создан: {repr(room)}")
    print_info(f"Отображение: {room}")
    print_info(f"Статус: {room.get_status_display()}")
    
    # Тест минимальных данных
    minimal_data = {
        "id": 102,
        "number": "102А",
        "floor_id": 1
    }
    minimal_room = Room.from_dict(minimal_data)
    assert minimal_room.area is None
    assert minimal_room.status_code is None
    print_info(f"Минимальный: {minimal_room.number}")
    
    print_success("Room модель работает корректно")
    
    return room


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ЗАПУСК ТЕСТОВ МОДЕЛЕЙ ДАННЫХ")
    print("="*60)
    
    tests = [
        test_complex_model,
        test_building_model,
        test_floor_model,
        test_room_model
    ]
    
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print_success(f"Тест {test.__name__} пройден")
        except AssertionError as e:
            print(f"  ❌ Ошибка в {test.__name__}: {e}")
        except Exception as e:
            print(f"  ❌ Исключение в {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"✅ Пройдено тестов: {passed}/{len(tests)}")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()