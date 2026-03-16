# tests/client/core/bus/test_04_error_handling/test_invalid_data_types.py
"""Тест обработки невалидных типов данных в EventBus."""
import pytest
from unittest.mock import Mock, patch

from client.src.core.event_bus import EventBus
from client.src.core.events import UIEvents, SystemEvents


class TestInvalidDataTypes:
    """Тестирует поведение EventBus с невалидными типами данных."""

    def test_emit_with_none_data(self):
        """Проверяет emit с data=None."""
        # Arrange
        event_bus = EventBus()
        received_data = None
        
        def handler(event):
            nonlocal received_data
            received_data = event['data']
        
        event_bus.subscribe('none_test', handler)
        
        # Act
        event_bus.emit('none_test', data=None)
        
        # Assert - data должен быть преобразован в пустой словарь
        assert received_data == {}, "data=None должен быть преобразован в {}"

    def test_emit_without_data_param(self):
        """Проверяет emit без указания параметра data."""
        # Arrange
        event_bus = EventBus()
        received_data = None
        
        def handler(event):
            nonlocal received_data
            received_data = event['data']
        
        event_bus.subscribe('no_data_test', handler)
        
        # Act
        event_bus.emit('no_data_test')
        
        # Assert - должен быть пустой словарь
        assert received_data == {}, "При отсутствии data должен быть {}"

    def test_emit_with_non_dict_data(self):
        """Проверяет emit с data не словарного типа."""
        # Arrange
        event_bus = EventBus()
        received_data = None
        
        def handler(event):
            nonlocal received_data
            received_data = event['data']
        
        event_bus.subscribe('non_dict_test', handler)
        
        # Act
        # Используем ignore, так как намеренно передаём не-словарь
        event_bus.emit('non_dict_test', data="строка вместо словаря")  # type: ignore
        
        # Assert - данные передаются как есть
        assert received_data == "строка вместо словаря", \
            "Несловарные данные должны передаваться как есть"

    def test_emit_with_none_source(self):
        """Проверяет emit с source=None."""
        # Arrange
        event_bus = EventBus()
        received_source = "not_none"
        
        def handler(event):
            nonlocal received_source
            received_source = event['source']
        
        event_bus.subscribe('source_test', handler)
        
        # Act
        event_bus.emit('source_test', source=None)
        
        # Assert
        assert received_source is None, "source=None должен оставаться None"

    def test_emit_without_source_param(self):
        """Проверяет emit без указания параметра source."""
        # Arrange
        event_bus = EventBus()
        received_source = "not_none"
        
        def handler(event):
            nonlocal received_source
            received_source = event['source']
        
        event_bus.subscribe('no_source_test', handler)
        
        # Act
        event_bus.emit('no_source_test')
        
        # Assert
        assert received_source is None, "При отсутствии source должен быть None"

    def test_emit_with_non_string_event_type(self):
        """Проверяет emit с нестроковым типом события."""
        # Arrange
        event_bus = EventBus()
        
        # Act & Assert - должно работать с любым хешируемым типом
        try:
            # Используем ignore для нестроковых типов
            event_bus.emit(123, {"test": "data"})  # type: ignore
            event_bus.emit(("tuple", "type"), {"test": "data"})  # type: ignore
        except Exception as e:
            pytest.fail(f"Нестроковые типы событий вызвали ошибку: {e}")

    def test_handler_receives_various_data_types(self):
        """Проверяет получение обработчиком различных типов данных."""
        # Arrange
        event_bus = EventBus()
        received_types = []
        
        def handler(event):
            received_types.append((type(event['data']), event['data']))
        
        event_bus.subscribe('type_collector', handler)
        
        # Act - испускаем с разными типами данных
        test_cases = [
            {"key": "value"},  # dict
            [1, 2, 3],         # list
            "string data",      # str
            42,                 # int
            3.14,               # float
            True,               # bool
            (1, 2),             # tuple
            {1, 2, 3},          # set
        ]
        
        # Отдельно тестируем None, так как он преобразуется
        none_case = None
        
        for data in test_cases:
            event_bus.emit('type_collector', data)  # type: ignore
        
        # Тестируем None отдельно
        event_bus.emit('type_collector', none_case)  # type: ignore
        
        # Assert
        assert len(received_types) == len(test_cases) + 1, \
            f"Ожидалось {len(test_cases) + 1} вызовов, получено {len(received_types)}"
        
        # Проверяем обычные случаи
        for i, (data_type, data_value) in enumerate(received_types[:len(test_cases)]):
            assert data_value == test_cases[i], \
                f"Значение {i} не совпадает. Ожидалось {test_cases[i]}, получено {data_value}"
        
        # Проверяем None отдельно
        none_type, none_value = received_types[-1]
        assert none_value == {}, f"None должен быть преобразован в {{}}, получено {none_value}"
        assert none_type == dict, f"Тип для None должен быть dict, получен {none_type}"
    def test_emit_with_complex_nested_data(self):
        """Проверяет emit со сложными вложенными структурами данных."""
        # Arrange
        event_bus = EventBus()
        received_data = None
        
        def handler(event):
            nonlocal received_data
            received_data = event['data']
        
        event_bus.subscribe('complex_test', handler)
        
        # Act
        complex_data = {
            "users": [
                {"name": "Alice", "age": 30, "tags": ["admin", "power"]},
                {"name": "Bob", "age": 25, "tags": ["user"]}
            ],
            "metadata": {
                "count": 2,
                "active": True,
                "ratio": 0.75
            },
            "settings": None
        }
        
        event_bus.emit('complex_test', complex_data)
        
        # Assert
        assert received_data == complex_data, \
            "Сложные вложенные структуры должны передаваться корректно"

    def test_emit_with_data_containing_objects(self):
        """Проверяет emit с данными, содержащими объекты."""
        # Arrange
        event_bus = EventBus()
        
        class CustomObject:
            def __init__(self, value):
                self.value = value
        
        obj = CustomObject(42)
        received_obj = None
        
        def handler(event):
            nonlocal received_obj
            received_obj = event['data']['object']  # type: ignore
        
        event_bus.subscribe('object_test', handler)
        
        # Act
        event_bus.emit('object_test', {"object": obj})
        
        # Assert
        assert received_obj is not None, "Объект должен быть получен"
        assert received_obj is obj, "Объекты должны передаваться по ссылке"
        assert received_obj.value == 42, "Значение объекта должно сохраняться"

    def test_emit_with_empty_data(self):
        """Проверяет emit с пустым словарём данных."""
        # Arrange
        event_bus = EventBus()
        received_data = None
        
        def handler(event):
            nonlocal received_data
            received_data = event['data']
        
        event_bus.subscribe('empty_test', handler)
        
        # Act
        event_bus.emit('empty_test', {})
        
        # Assert
        assert received_data == {}, "Пустой словарь должен передаваться корректно"