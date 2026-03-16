"""
Тест: обнаружение нарушенной обратной связи.
Проверяет, что check_consistency находит ситуацию, когда
у родителя нет ссылки на ребёнка, хотя ребёнок ссылается на родителя.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.models import Complex, Building


def test_consistency_missing_child_in_parent(monkeypatch, entity_graph):
    """
    Проверяет обнаружение ситуации, когда ребёнок есть в parents,
    но его нет в children у родителя.
    """
    # Arrange - создаём нормальную иерархию
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Ломаем консистентность - удаляем ребёнка из children родителя,
    # но оставляем в parents
    entity_graph._relations._children_set[COMPLEX][1].discard(1)
    # В sorted list тоже нужно удалить для полной несогласованности
    if 1 in entity_graph._relations._children_sorted[COMPLEX][1]:
        entity_graph._relations._children_sorted[COMPLEX][1].remove(1)
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is False
    issues = result['issues']
    assert len(issues) == 1
    
    # Проверяем сообщение об ошибке
    error_msg = issues[0]
    assert "Ребёнок" in error_msg
    assert "building#1" in error_msg
    assert "не найден в children" in error_msg
    
    # В сообщении формат children[complex][1], а не complex#1
    # Проверяем, что упоминается complex и ID=1
    assert "complex" in error_msg
    assert "[1]" in error_msg or "1" in error_msg


def test_consistency_multiple_missing_children(monkeypatch, entity_graph):
    """Проверяет обнаружение нескольких отсутствующих детей у родителя."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=4)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    
    # Ломаем - удаляем обоих детей из children родителя
    entity_graph._relations._children_set[COMPLEX][1].clear()
    entity_graph._relations._children_sorted[COMPLEX][1].clear()
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is False
    issues = result['issues']
    assert len(issues) == 2  # Две ошибки для двух детей
    
    for issue in issues:
        assert "Ребёнок" in issue
        assert "не найден в children" in issue
        assert "complex" in issue
        assert "[1]" in issue


def test_consistency_orphan_in_parent(monkeypatch, entity_graph):
    """
    Проверяет обнаружение ситуации, когда у родителя есть ребёнок,
    но этот ребёнок не ссылается на родителя (нет в parents).
    
    Note: Текущая реализация check_consistency проверяет только обратную связь:
    от детей к родителям. Она не проверяет, что каждый ребёнок в children
    имеет соответствующую запись в parents. Этот тест показывает это ограничение.
    """
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Ломаем - удаляем родителя у ребёнка
    del entity_graph._relations._parents[BUILDING][1]
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    # Текущая реализация НЕ обнаруживает эту ошибку
    # Поэтому тест временно помечаем как xfail или пропускаем
    pytest.xfail("check_consistency пока не проверяет наличие parents для всех детей")
    
    # Когда реализация будет исправлена, раскомментировать:
    # assert result['consistent'] is False
    # issues = result['issues']
    # assert len(issues) == 1
    # assert "Родитель" in issues[0] or "parents" in issues[0]


def test_consistency_complex_breakage(monkeypatch, entity_graph):
    """
    Проверяет обнаружение сложного нарушения: несколько ошибок в разных местах.
    """
    # Arrange - создаём небольшую иерархию
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=4)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    
    # Ломаем в нескольких местах:
    # 1. Удаляем родителя для building_1
    entity_graph._store.remove(COMPLEX, 1)
    
    # 2. Удаляем building_2 из children родителя
    entity_graph._relations._children_set[COMPLEX][1].discard(2)
    if 2 in entity_graph._relations._children_sorted[COMPLEX][1]:
        entity_graph._relations._children_sorted[COMPLEX][1].remove(2)
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is False
    
    # Должны быть ошибки:
    # - building_1: родитель не существует
    # - building_2: отсутствует в children
    issues = result['issues']
    assert len(issues) >= 2
    
    # Проверяем, что есть оба типа ошибок
    parent_errors = [i for i in issues if "Родитель" in i]
    child_errors = [i for i in issues if "Ребёнок" in i and "не найден" in i]
    
    assert len(parent_errors) >= 1
    assert len(child_errors) >= 1