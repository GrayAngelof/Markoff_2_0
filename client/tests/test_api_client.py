# tests/test_api_client.py
"""
Тесты для API клиента
Проверяем все методы загрузки данных с сервера
"""
import sys
import os
sys.path.append('/app')

from src.core.api_client import ApiClient
from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


def print_header(text):
    """Вывод заголовка теста"""
    print(f"\n{'='*60}")
    print(f"🧪 {text}")
    print(f"{'='*60}")


def print_success(text):
    """Вывод сообщения об успехе"""
    print(f"  ✅ {text}")


def print_info(text):
    """Вывод информационного сообщения"""
    print(f"  ℹ️ {text}")


def test_connection():
    """Тест соединения с сервером"""
    print_header("Тест соединения с сервером")
    
    client = ApiClient()
    
    # Проверяем соединение
    is_connected = client.check_connection()
    assert is_connected is True, "Сервер должен быть доступен"
    print_success("Сервер доступен")
    
    # Получаем информацию
    info = client.get_server_info()
    assert 'message' in info, "Ответ должен содержать поле 'message'"
    print_success(f"Информация: {info}")
    
    # Показываем эндпоинты
    client.print_endpoints()
    
    return client


def test_get_complexes():
    """Тест получения комплексов"""
    print_header("Тест получения комплексов")
    
    client = ApiClient()
    
    complexes = client.get_complexes()
    
    assert isinstance(complexes, list), "Должен возвращаться список"
    assert len(complexes) > 0, "Должен быть хотя бы один комплекс"
    
    # Проверяем первый комплекс
    complex1 = complexes[0]
    assert isinstance(complex1, Complex), "Элемент должен быть Complex"
    assert complex1.id > 0, "ID должен быть положительным"
    assert complex1.name, "Имя не должно быть пустым"
    
    print_success(f"Загружено комплексов: {len(complexes)}")
    print_info(f"Первый комплекс: {complex1.name} (ID={complex1.id}, корпусов={complex1.buildings_count})")
    
    return complexes


def test_get_buildings():
    """Тест получения корпусов"""
    print_header("Тест получения корпусов")
    
    client = ApiClient()
    
    # Сначала получаем комплексы, чтобы взять ID первого
    complexes = client.get_complexes()
    assert len(complexes) > 0, "Нет комплексов для теста"
    
    complex_id = complexes[0].id
    buildings = client.get_buildings(complex_id)
    
    assert isinstance(buildings, list), "Должен возвращаться список"
    
    if buildings:
        building1 = buildings[0]
        assert isinstance(building1, Building), "Элемент должен быть Building"
        assert building1.complex_id == complex_id, "complex_id должен совпадать"
        
        print_success(f"Загружено корпусов: {len(buildings)}")
        print_info(f"Первый корпус: {building1.name} (ID={building1.id}, этажей={building1.floors_count})")
    else:
        print_info(f"Для комплекса {complex_id} нет корпусов")
    
    return buildings


def test_get_floors():
    """Тест получения этажей"""
    print_header("Тест получения этажей")
    
    client = ApiClient()
    
    # Получаем первый корпус
    complexes = client.get_complexes()
    if not complexes:
        print_info("Нет комплексов, пропускаем тест этажей")
        return
    
    buildings = client.get_buildings(complexes[0].id)
    if not buildings:
        print_info("Нет корпусов, пропускаем тест этажей")
        return
    
    building_id = buildings[0].id
    floors = client.get_floors(building_id)
    
    assert isinstance(floors, list), "Должен возвращаться список"
    
    if floors:
        floor1 = floors[0]
        assert isinstance(floor1, Floor), "Элемент должен быть Floor"
        assert floor1.building_id == building_id, "building_id должен совпадать"
        
        # Проверяем сортировку
        numbers = [f.number for f in floors]
        assert numbers == sorted(numbers), "Этажи должны быть отсортированы по номеру"
        
        print_success(f"Загружено этажей: {len(floors)}")
        print_info(f"Первый этаж: {floor1.number} (ID={floor1.id}, помещений={floor1.rooms_count})")
    else:
        print_info(f"Для корпуса {building_id} нет этажей")
    
    return floors


def test_get_rooms():
    """Тест получения помещений"""
    print_header("Тест получения помещений")
    
    client = ApiClient()
    
    # Получаем первый этаж
    complexes = client.get_complexes()
    if not complexes:
        return
    
    buildings = client.get_buildings(complexes[0].id)
    if not buildings:
        return
    
    floors = client.get_floors(buildings[0].id)
    if not floors:
        print_info("Нет этажей, пропускаем тест помещений")
        return
    
    floor_id = floors[0].id
    rooms = client.get_rooms(floor_id)
    
    assert isinstance(rooms, list), "Должен возвращаться список"
    
    if rooms:
        room1 = rooms[0]
        assert isinstance(room1, Room), "Элемент должен быть Room"
        assert room1.floor_id == floor_id, "floor_id должен совпадать"
        
        # Проверяем статус, если есть
        if room1.status_code:
            status_display = room1.get_status_display()
            print_info(f"Статус помещения: {status_display}")
        
        print_success(f"Загружено помещений: {len(rooms)}")
        print_info(f"Первое помещение: {room1.number} (ID={room1.id}, площадь={room1.area})")
    else:
        print_info(f"Для этажа {floor_id} нет помещений")
    
    return rooms


def test_error_handling():
    """Тест обработки ошибок"""
    print_header("Тест обработки ошибок")
    
    client = ApiClient()
    
    # Тест с несуществующим ID
    try:
        buildings = client.get_buildings(99999)
        print_info(f"Запрос несуществующего комплекса вернул {len(buildings)} записей")
    except Exception as e:
        print_success(f"Ошибка обработана корректно: {e}")
    
    # Тест с неверным URL (временно меняем base_url)
    original_url = client.base_url
    client.base_url = "http://wrong-url:9999"
    
    try:
        client.get_complexes()
        assert False, "Должна быть ошибка подключения"
    except Exception as e:
        print_success(f"Ошибка подключения обработана: {e}")
    finally:
        client.base_url = original_url
    
    return True


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*70)
    print("🧪 ЗАПУСК ТЕСТОВ API КЛИЕНТА")
    print("="*70)
    
    tests = [
        test_connection,
        test_get_complexes,
        test_get_buildings,
        test_get_floors,
        test_get_rooms,
        test_error_handling
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
    
    print("\n" + "="*70)
    print(f"✅ Пройдено тестов: {passed}/{len(tests)}")
    print("="*70)


if __name__ == "__main__":
    run_all_tests()