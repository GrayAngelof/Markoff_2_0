"""
Тест: рекурсивная инвалидация ветки.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM
from client.src.data.graph.validity_index import ValidityIndex


def create_test_hierarchy(validity_index):
    """Создаёт тестовую иерархию и помечает всё валидным."""
    # Complex 1
    # ├── Building 1
    # │   └── Floor 10
    # │       └── Room 100
    # └── Building 2
    #     └── Floor 20
    #         └── Room 200
    validity_index.mark_valid(COMPLEX, 1)
    
    validity_index.mark_valid(BUILDING, 1)
    validity_index.mark_valid(BUILDING, 2)
    
    validity_index.mark_valid(FLOOR, 10)
    validity_index.mark_valid(FLOOR, 20)
    
    validity_index.mark_valid(ROOM, 100)
    validity_index.mark_valid(ROOM, 200)


def mock_get_children(node_type, node_id):
    """Мок-функция для получения детей."""
    children = {
        (COMPLEX, 1): [1, 2],        # Building 1 и 2
        (BUILDING, 1): [10],          # Floor 10
        (BUILDING, 2): [20],          # Floor 20
        (FLOOR, 10): [100],           # Room 100
        (FLOOR, 20): [200],           # Room 200
        (ROOM, 100): [],              # Комнаты без детей
        (ROOM, 200): [],              # Комнаты без детей
    }
    return children.get((node_type, node_id), [])


def test_invalidate_branch_root(validity_index):
    """Проверяет инвалидацию корневой сущности (должна инвалидировать всю иерархию)."""
    # Arrange
    create_test_hierarchy(validity_index)
    
    # Act
    count = validity_index.invalidate_branch(COMPLEX, 1, mock_get_children)
    
    # Assert
    assert count == 7  # Все 7 сущностей: complex + 2 buildings + 2 floors + 2 rooms
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(BUILDING, 1) is False
    assert validity_index.is_valid(BUILDING, 2) is False
    assert validity_index.is_valid(FLOOR, 10) is False
    assert validity_index.is_valid(FLOOR, 20) is False
    assert validity_index.is_valid(ROOM, 100) is False
    assert validity_index.is_valid(ROOM, 200) is False


def test_invalidate_branch_mid_level(validity_index):
    """Проверяет инвалидацию сущности среднего уровня (инвалидирует всех потомков)."""
    # Arrange
    create_test_hierarchy(validity_index)
    
    # Act
    count = validity_index.invalidate_branch(BUILDING, 1, mock_get_children)
    
    # Assert
    assert count == 3  # building 1 + floor 10 + room 100
    assert validity_index.is_valid(COMPLEX, 1) is True   # Комплекс не должен инвалидироваться
    assert validity_index.is_valid(BUILDING, 1) is False
    assert validity_index.is_valid(BUILDING, 2) is True  # Другое здание не должно инвалидироваться
    assert validity_index.is_valid(FLOOR, 10) is False
    assert validity_index.is_valid(FLOOR, 20) is True    # Другой этаж не должен инвалидироваться
    assert validity_index.is_valid(ROOM, 100) is False
    assert validity_index.is_valid(ROOM, 200) is True    # Другая комната не должна инвалидироваться


def test_invalidate_branch_leaf(validity_index):
    """Проверяет инвалидацию листовой сущности (только саму сущность)."""
    # Arrange
    create_test_hierarchy(validity_index)
    
    # Act
    count = validity_index.invalidate_branch(ROOM, 100, mock_get_children)
    
    # Assert
    assert count == 1  # только room 100
    assert validity_index.is_valid(COMPLEX, 1) is True
    assert validity_index.is_valid(BUILDING, 1) is True
    assert validity_index.is_valid(BUILDING, 2) is True
    assert validity_index.is_valid(FLOOR, 10) is True
    assert validity_index.is_valid(FLOOR, 20) is True
    assert validity_index.is_valid(ROOM, 100) is False
    assert validity_index.is_valid(ROOM, 200) is True


def test_invalidate_branch_already_invalid(validity_index):
    """Проверяет инвалидацию уже невалидной ветки."""
    # Arrange
    create_test_hierarchy(validity_index)
    validity_index.mark_invalid(BUILDING, 1)
    validity_index.mark_invalid(FLOOR, 10)  # Специально сделаем floor невалидным
    
    # Act
    count = validity_index.invalidate_branch(BUILDING, 1, mock_get_children)
    
    # Assert
    # Должны инвалидироваться: room 100 (building и floor уже невалидны)
    assert count == 1
    assert validity_index.is_valid(BUILDING, 1) is False  # Уже было невалидно
    assert validity_index.is_valid(FLOOR, 10) is False    # Уже было невалидно
    assert validity_index.is_valid(ROOM, 100) is False    # Стало невалидным


def test_invalidate_branch_with_circular_ref(validity_index):
    """Проверяет устойчивость к циклическим ссылкам."""
    # Arrange
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(BUILDING, 1)
    
    # Создаём цикл в get_children (для теста)
    def circular_get_children(node_type, node_id):
        if (node_type, node_id) == (COMPLEX, 1):
            return [1]  # building 1
        elif (node_type, node_id) == (BUILDING, 1):
            return [1]  # complex 1 - цикл!
        return []
    
    # Act - должно отработать без зацикливания
    count = validity_index.invalidate_branch(COMPLEX, 1, circular_get_children)
    
    # Assert
    assert count == 2  # complex и building
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(BUILDING, 1) is False


def test_invalidate_branch_deep_hierarchy(validity_index):
    """Проверяет инвалидацию глубокой иерархии."""
    # Arrange
    # Создаём более глубокую иерархию
    validity_index.mark_valid(COMPLEX, 1)
    validity_index.mark_valid(BUILDING, 1)
    validity_index.mark_valid(FLOOR, 10)
    validity_index.mark_valid(ROOM, 100)
    validity_index.mark_valid(ROOM, 101)  # Две комнаты на этаже
    
    def deep_get_children(node_type, node_id):
        children = {
            (COMPLEX, 1): [1],
            (BUILDING, 1): [10],
            (FLOOR, 10): [100, 101],
            (ROOM, 100): [],
            (ROOM, 101): [],
        }
        return children.get((node_type, node_id), [])
    
    # Act
    count = validity_index.invalidate_branch(COMPLEX, 1, deep_get_children)
    
    # Assert
    assert count == 5  # complex + building + floor + 2 rooms
    assert validity_index.is_valid(COMPLEX, 1) is False
    assert validity_index.is_valid(BUILDING, 1) is False
    assert validity_index.is_valid(FLOOR, 10) is False
    assert validity_index.is_valid(ROOM, 100) is False
    assert validity_index.is_valid(ROOM, 101) is False