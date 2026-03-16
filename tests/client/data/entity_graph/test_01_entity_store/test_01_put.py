"""
Тест: добавление сущности в хранилище.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.models import Complex, Building


def test_put_adds_entity(entity_store, complex_entity):
    """Проверяет, что put() сохраняет объект."""
    # Act
    entity_store.put(COMPLEX, 1, complex_entity)
    
    # Assert
    assert entity_store.has(COMPLEX, 1) is True
    stored = entity_store.get(COMPLEX, 1)
    assert stored is complex_entity  # Должен быть тот же объект
    assert stored.id == 1
    assert stored.name == "Тестовый комплекс"
    assert stored.buildings_count == 2  # Проверяем обязательное поле


def test_put_overwrites_existing(entity_store, complex_entity):
    """Проверяет, что put() перезаписывает существующий объект."""
    # Arrange
    entity_store.put(COMPLEX, 1, complex_entity)
    
    # Создаём новый объект с ОБЯЗАТЕЛЬНЫМ buildings_count
    new_complex = Complex(
        id=1, 
        name="Обновлённый комплекс", 
        buildings_count=3,  # Обязательное поле!
        address="Новый адрес"
    )
    
    # Act
    entity_store.put(COMPLEX, 1, new_complex)
    
    # Assert
    stored = entity_store.get(COMPLEX, 1)
    assert stored is new_complex
    assert stored.name == "Обновлённый комплекс"
    assert stored.buildings_count == 3


def test_put_different_ids(entity_store, complex_entity):
    """Проверяет, что разные ID хранятся отдельно."""
    # Arrange
    # complex_entity уже имеет id=1 из фикстуры
    
    # Создаём второй комплекс с ОБЯЗАТЕЛЬНЫМ buildings_count
    complex_2 = Complex(
        id=2, 
        name="Комплекс 2", 
        buildings_count=1,  # Обязательное поле!
        address="Адрес 2"
    )
    
    # Act
    entity_store.put(COMPLEX, 1, complex_entity)
    entity_store.put(COMPLEX, 2, complex_2)
    
    # Assert
    assert entity_store.get(COMPLEX, 1) is complex_entity
    assert entity_store.get(COMPLEX, 2) is complex_2
    assert entity_store.size() == 2


def test_put_different_types(entity_store, complex_entity, building_entity):
    """Проверяет, что разные типы хранятся отдельно."""
    # Act
    entity_store.put(COMPLEX, 1, complex_entity)
    entity_store.put(BUILDING, 1, building_entity)
    
    # Assert
    assert entity_store.get(COMPLEX, 1) is complex_entity
    assert entity_store.get(BUILDING, 1) is building_entity
    assert entity_store.size() == 2


def test_put_with_all_optional_fields(entity_store):
    """Проверяет создание комплекса со всеми полями."""
    # Arrange
    complex_full = Complex(
        id=3,
        name="Полный комплекс",
        buildings_count=5,  # Обязательное поле
        description="Подробное описание комплекса",
        address="ул. Полная, 10",
        owner_id=42,
        created_at="2024-01-01T10:00:00",
        updated_at="2024-01-02T15:30:00"
    )
    
    # Act
    entity_store.put(COMPLEX, 3, complex_full)
    stored = entity_store.get(COMPLEX, 3)
    
    # Assert
    assert stored.id == 3
    assert stored.name == "Полный комплекс"
    assert stored.buildings_count == 5
    assert stored.description == "Подробное описание комплекса"
    assert stored.address == "ул. Полная, 10"
    assert stored.owner_id == 42
    assert stored.created_at == "2024-01-01T10:00:00"
    assert stored.updated_at == "2024-01-02T15:30:00"


def test_put_null_optional_fields(entity_store):
    """Проверяет создание комплекса с null в опциональных полях."""
    # Arrange
    complex_minimal = Complex(
        id=4,
        name="Минимальный комплекс",
        buildings_count=0,  # Обязательное поле, может быть 0
        description=None,
        address=None,
        owner_id=None,
        created_at=None,
        updated_at=None
    )
    
    # Act
    entity_store.put(COMPLEX, 4, complex_minimal)
    stored = entity_store.get(COMPLEX, 4)
    
    # Assert
    assert stored.id == 4
    assert stored.name == "Минимальный комплекс"
    assert stored.buildings_count == 0
    assert stored.description is None
    assert stored.address is None
    assert stored.owner_id is None
    assert stored.created_at is None
    assert stored.updated_at is None