"""
Тест: обнаружение нарушенной связи родителя.
Проверяет, что check_consistency находит ситуацию, когда
у ребёнка есть родитель, но родитель не существует в хранилище.
"""
import pytest
from client.src.data import COMPLEX, BUILDING
from client.src.models import Complex, Building


def test_consistency_missing_parent_direct_access(monkeypatch, entity_graph):
    """
    Проверяет обнаружение ситуации, когда у ребёнка есть родитель,
    но родитель не существует в хранилище.
    """
    # Arrange - создаём нормальную иерархию
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Ломаем консистентность - удаляем родителя напрямую из хранилища,
    # минуя граф (чтобы не обновлялись индексы)
    entity_graph._store.remove(COMPLEX, 1)
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is False
    issues = result['issues']
    assert len(issues) == 1
    
    # Проверяем, что сообщение об ошибке содержит нужную информацию
    error_msg = issues[0]
    assert "Родитель" in error_msg
    assert "complex#1" in error_msg or "COMPLEX#1" in error_msg
    assert "building#1" in error_msg or "BUILDING#1" in error_msg
    assert "не существует" in error_msg


def test_consistency_multiple_missing_parents(monkeypatch, entity_graph):
    """Проверяет обнаружение нескольких отсутствующих родителей."""
    # Arrange
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=2, address="Адрес")
    building_1 = Building(id=1, name="Корпус А", complex_id=1, floors_count=3)
    building_2 = Building(id=2, name="Корпус Б", complex_id=1, floors_count=4)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    entity_graph.add_or_update(building_2)
    
    # Ломаем консистентность - удаляем родителя
    entity_graph._store.remove(COMPLEX, 1)
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is False
    issues = result['issues']
    assert len(issues) == 2  # Две ошибки для двух детей
    
    for issue in issues:
        assert "Родитель" in issue
        assert "complex#1" in issue
        assert "не существует" in issue


def test_consistency_parent_exists_but_wrong_type(monkeypatch, entity_graph):
    """
    Проверяет обнаружение ситуации, когда тип родителя не соответствует схеме.
    Хотя такой ситуации не должно возникать из-за проверок в link().
    """
    # Arrange - создаём связь напрямую через индексы, минуя граф
    complex_1 = Complex(id=1, name="Комплекс", buildings_count=1, address="Адрес")
    building_1 = Building(id=1, name="Корпус", complex_id=1, floors_count=3)
    
    entity_graph.add_or_update(complex_1)
    entity_graph.add_or_update(building_1)
    
    # Ломаем - меняем тип родителя в обратном индексе
    # (такое возможно только при прямом доступе к _relations)
    child_type = BUILDING
    child_id = 1
    # Вместо (COMPLEX, 1) ставим (BUILDING, 1) - неправильный тип
    entity_graph._relations._parents[child_type][child_id] = (BUILDING, 1)
    
    # Act
    result = entity_graph.check_consistency()
    
    # Assert
    assert result['consistent'] is False
    issues = result['issues']
    assert len(issues) >= 1