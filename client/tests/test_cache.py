# tests/test_cache.py
"""
Тесты для системы кэширования DataCache
Проверяем все основные методы и сценарии использования
"""
import sys
import os
sys.path.append('/app')  # Добавляем путь к корню приложения

from src.core.cache import DataCache
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


def test_basic_operations():
    """Тест базовых операций get/set/has/remove"""
    print_header("Тест базовых операций")
    
    cache = DataCache()
    
    # Тест set и get
    cache.set("test:1", "test_value")
    value = cache.get("test:1")
    assert value == "test_value", f"Ожидалось 'test_value', получено {value}"
    print_success("set/get работает")
    
    # Тест has
    assert cache.has("test:1") is True, "has должен вернуть True для существующего ключа"
    assert cache.has("test:2") is False, "has должен вернуть False для несуществующего ключа"
    print_success("has работает")
    
    # Тест remove
    cache.remove("test:1")
    assert cache.has("test:1") is False, "После remove ключ должен отсутствовать"
    print_success("remove работает")
    
    return cache


def test_hierarchical_keys():
    """Тест иерархических ключей и методов доступа"""
    print_header("Тест иерархических ключей")
    
    cache = DataCache()
    
    # Создаём тестовые данные
    complex_data = Complex(id=1, name="Тестовый комплекс")
    buildings_data = [
        Building(id=1, name="Корпус А", complex_id=1, floors_count=2),
        Building(id=2, name="Корпус Б", complex_id=1, floors_count=1)
    ]
    floors_data = [
        Floor(id=1, number=1, building_id=1, rooms_count=0),
        Floor(id=2, number=2, building_id=1, rooms_count=0)
    ]
    rooms_data = [
        Room(id=101, number="101", floor_id=1, area=50.0, status_code="free")
    ]
    
    # Сохраняем через специализированные методы
    cache.set_complex(1, complex_data)
    cache.set_buildings(1, buildings_data)
    cache.set_floors(1, floors_data)
    cache.set_rooms(1, rooms_data)
    
    # Проверяем через специализированные методы
    assert cache.get_complex(1) == complex_data, "get_complex не работает"
    assert cache.get_buildings(1) == buildings_data, "get_buildings не работает"
    assert cache.get_floors(1) == floors_data, "get_floors не работает"
    assert cache.get_rooms(1) == rooms_data, "get_rooms не работает"
    print_success("специализированные методы get/set работают")
    
    # Проверяем наличие ключей
    assert cache.has("complex:1") is True
    assert cache.has("complex:1:buildings") is True
    assert cache.has("building:1:floors") is True
    assert cache.has("floor:1:rooms") is True
    print_success("ключи созданы корректно")
    
    return cache


def test_invalidate_node():
    """Тест инвалидации отдельного узла"""
    print_header("Тест инвалидации узла")
    
    cache = DataCache()
    
    # Заполняем данными
    cache.set("complex:1", "data1")
    cache.set("complex:2", "data2")
    
    # Инвалидируем узел
    cache.invalidate_node(DataCache.TYPE_COMPLEX, 1)
    
    # Проверяем
    assert cache.has("complex:1") is False, "Узел должен быть удалён"
    assert cache.has("complex:2") is True, "Другие узлы должны сохраниться"
    print_success("инвалидация узла работает")
    
    return cache


def test_invalidate_branch_complex():
    """Тест инвалидации ветки для комплекса"""
    print_header("Тест инвалидации ветки (комплекс)")
    
    cache = DataCache()
    
    # Создаём тестовые данные
    # Комплекс 1
    cache.set("complex:1", "complex1")
    cache.set("complex:1:buildings", ["building1", "building2"])
    cache.set("building:101:floors", ["floor1", "floor2"])
    cache.set("floor:1001:rooms", ["room1", "room2"])
    cache.set("room:10001", "room_data")
    
    # Комплекс 2 (не должен пострадать)
    cache.set("complex:2", "complex2")
    cache.set("complex:2:buildings", ["building3"])
    
    # Инвалидируем ветку комплекса 1
    cache.invalidate_branch(DataCache.TYPE_COMPLEX, 1)
    
    # Проверяем, что удалилось
    assert cache.has("complex:1") is False, "Комплекс должен быть удалён"
    assert cache.has("complex:1:buildings") is False, "Список корпусов должен быть удалён"
    
    # Проверяем, что комплекс 2 не тронут
    assert cache.has("complex:2") is True, "Другой комплекс должен сохраниться"
    assert cache.has("complex:2:buildings") is True, "Данные другого комплекса должны сохраниться"
    
    print_success("инвалидация ветки комплекса работает")
    return cache


def test_invalidate_branch_building():
    """Тест инвалидации ветки для корпуса"""
    print_header("Тест инвалидации ветки (корпус)")
    
    cache = DataCache()
    
    # Создаём тестовые данные
    cache.set("complex:1", "complex1")
    cache.set("complex:1:buildings", ["building101", "building102"])
    
    # Корпус 101
    cache.set("building:101", "building101")
    cache.set("building:101:floors", ["floor1", "floor2"])
    cache.set("floor:1001:rooms", ["room1"])
    cache.set("floor:1002:rooms", ["room2"])
    
    # Корпус 102 (не должен пострадать)
    cache.set("building:102", "building102")
    cache.set("building:102:floors", ["floor3"])
    
    # Инвалидируем ветку корпуса 101
    cache.invalidate_branch(DataCache.TYPE_BUILDING, 101)
    
    # Проверяем корпус 101
    assert cache.has("building:101") is False, "Корпус должен быть удалён"
    assert cache.has("building:101:floors") is False, "Список этажей должен быть удалён"
    
    # Проверяем корпус 102
    assert cache.has("building:102") is True, "Другой корпус должен сохраниться"
    assert cache.has("building:102:floors") is True, "Данные другого корпуса должны сохраниться"
    
    # Проверяем комплекс (не должен пострадать)
    assert cache.has("complex:1") is True, "Комплекс должен сохраниться"
    
    print_success("инвалидация ветки корпуса работает")
    return cache


def test_invalidate_branch_floor():
    """Тест инвалидации ветки для этажа"""
    print_header("Тест инвалидации ветки (этаж)")
    
    cache = DataCache()
    
    # Создаём тестовые данные
    cache.set("building:101", "building101")
    cache.set("building:101:floors", ["floor1001", "floor1002"])
    
    # Этаж 1001
    cache.set("floor:1001", "floor1001")
    cache.set("floor:1001:rooms", ["room1", "room2"])
    cache.set("room:1", "room1_data")
    cache.set("room:2", "room2_data")
    
    # Этаж 1002 (не должен пострадать)
    cache.set("floor:1002", "floor1002")
    cache.set("floor:1002:rooms", ["room3"])
    
    # Инвалидируем ветку этажа 1001
    cache.invalidate_branch(DataCache.TYPE_FLOOR, 1001)
    
    # Проверяем этаж 1001
    assert cache.has("floor:1001") is False, "Этаж должен быть удалён"
    assert cache.has("floor:1001:rooms") is False, "Список помещений должен быть удалён"
    
    # Проверяем этаж 1002
    assert cache.has("floor:1002") is True, "Другой этаж должен сохраниться"
    assert cache.has("floor:1002:rooms") is True, "Данные другого этажа должны сохраниться"
    
    # Проверяем корпус (не должен пострадать)
    assert cache.has("building:101") is True, "Корпус должен сохраниться"
    
    print_success("инвалидация ветки этажа работает")
    return cache


def test_expanded_nodes():
    """Тест работы с раскрытыми узлами"""
    print_header("Тест раскрытых узлов")
    
    cache = DataCache()
    
    # Отмечаем раскрытые узлы
    cache.mark_expanded(DataCache.TYPE_COMPLEX, 1)
    cache.mark_expanded(DataCache.TYPE_BUILDING, 101)
    cache.mark_expanded(DataCache.TYPE_FLOOR, 1001)
    
    # Проверяем, что они раскрыты
    assert cache.is_expanded(DataCache.TYPE_COMPLEX, 1) is True
    assert cache.is_expanded(DataCache.TYPE_BUILDING, 101) is True
    assert cache.is_expanded(DataCache.TYPE_FLOOR, 1001) is True
    assert cache.is_expanded(DataCache.TYPE_COMPLEX, 2) is False
    
    # Получаем список раскрытых
    expanded = cache.get_expanded_nodes()
    assert len(expanded) == 3
    assert (DataCache.TYPE_COMPLEX, 1) in expanded
    assert (DataCache.TYPE_BUILDING, 101) in expanded
    assert (DataCache.TYPE_FLOOR, 1001) in expanded
    
    # Помечаем как свёрнутый
    cache.mark_collapsed(DataCache.TYPE_BUILDING, 101)
    assert cache.is_expanded(DataCache.TYPE_BUILDING, 101) is False
    assert len(cache.get_expanded_nodes()) == 2
    
    print_success("работа с раскрытыми узлами корректна")
    return cache


def test_clear():
    """Тест полной очистки кэша"""
    print_header("Тест полной очистки")
    
    cache = DataCache()
    
    # Заполняем данными
    cache.set("complex:1", "data1")
    cache.set("complex:2", "data2")
    cache.mark_expanded(DataCache.TYPE_COMPLEX, 1)
    
    # Очищаем
    cache.clear()
    
    # Проверяем
    assert cache.has("complex:1") is False
    assert cache.has("complex:2") is False
    assert cache.is_expanded(DataCache.TYPE_COMPLEX, 1) is False
    assert len(cache.get_expanded_nodes()) == 0
    
    print_success("полная очистка работает")
    return cache


def test_stats():
    """Тест статистики"""
    print_header("Тест статистики")
    
    cache = DataCache()
    
    # Делаем несколько операций
    cache.set("complex:1", "data1")
    cache.get("complex:1")  # hit
    cache.get("complex:2")  # miss
    cache.get("complex:1")  # hit
    cache.invalidate_node(DataCache.TYPE_COMPLEX, 1)  # invalidation
    
    stats = cache.get_stats()
    
    assert stats['size'] == 0  # после инвалидации
    assert stats['hits'] == 2
    assert stats['misses'] == 1
    assert stats['invalidations'] >= 1
    
    print_success(f"статистика: {stats['hit_rate']} попаданий")
    cache.print_stats()
    
    return cache


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ЗАПУСК ТЕСТОВ СИСТЕМЫ КЭШИРОВАНИЯ")
    print("="*60)
    
    tests = [
        test_basic_operations,
        test_hierarchical_keys,
        test_invalidate_node,
        test_invalidate_branch_complex,
        test_invalidate_branch_building,
        test_invalidate_branch_floor,
        test_expanded_nodes,
        test_clear,
        test_stats
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
    
    print("\n" + "="*60)
    print(f"✅ Пройдено тестов: {passed}/{len(tests)}")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()