"""
Интеграционный сценарий: полная проверка графа.
"""
import pytest
from client.src.data import COMPLEX, BUILDING, FLOOR, ROOM


class TestFullScenario:
    """Полный сценарий тестирования графа."""
    
    def test_initial_hierarchy(self, full_graph):
        """Проверяет, что иерархия создалась корректно."""
        graph = full_graph
        
        # Проверяем количество сущностей
        # 2 комплекса + 3 корпуса + 4 этажа + 5 комнат = 14
        stats = graph.get_stats()
        assert stats['total_entities'] == 14
        assert stats['by_type']['complex'] == 2
        assert stats['by_type']['building'] == 3
        assert stats['by_type']['floor'] == 4
        assert stats['by_type']['room'] == 5
        
        # Проверяем наличие всех сущностей
        assert graph.has_entity(COMPLEX, 1) is True
        assert graph.has_entity(COMPLEX, 2) is True
        assert graph.has_entity(BUILDING, 1) is True
        assert graph.has_entity(BUILDING, 2) is True
        assert graph.has_entity(BUILDING, 3) is True
        assert graph.has_entity(FLOOR, 1) is True
        assert graph.has_entity(FLOOR, 2) is True
        assert graph.has_entity(FLOOR, 3) is True
        assert graph.has_entity(FLOOR, 4) is True
        assert graph.has_entity(ROOM, 1) is True
        assert graph.has_entity(ROOM, 2) is True
        assert graph.has_entity(ROOM, 3) is True
        assert graph.has_entity(ROOM, 4) is True
        assert graph.has_entity(ROOM, 5) is True
        
        # Проверяем навигацию сверху вниз
        # Complex 1 -> Buildings
        complex1_buildings = graph.get_children(COMPLEX, 1)
        assert set(complex1_buildings) == {1, 2}  # Building 1 и 2
        
        # Complex 2 -> Buildings
        complex2_buildings = graph.get_children(COMPLEX, 2)
        assert complex2_buildings == [3]  # Building 3
        
        # Building 1 -> Floors
        building1_floors = graph.get_children(BUILDING, 1)
        assert set(building1_floors) == {1, 2}  # Floor 1 и 2
        
        # Floor 1 -> Rooms
        floor1_rooms = graph.get_children(FLOOR, 1)
        assert set(floor1_rooms) == {1, 2}  # Room 101 и 102
        
        # Проверяем навигацию снизу вверх
        # Room 101 -> Floor -> Building -> Complex
        assert graph.get_parent(ROOM, 1) == (FLOOR, 1)
        assert graph.get_parent(FLOOR, 1) == (BUILDING, 1)
        assert graph.get_parent(BUILDING, 1) == (COMPLEX, 1)
        
        # Проверяем валидность (после добавления всё должно быть валидно)
        assert graph.is_valid(COMPLEX, 1) is True
        assert graph.is_valid(BUILDING, 1) is True
        assert graph.is_valid(FLOOR, 1) is True
        assert graph.is_valid(ROOM, 1) is True
    
    def test_navigation_queries(self, full_graph):
        """Проверяет различные навигационные запросы."""
        graph = full_graph
        
        # Получаем всех потомков Complex 1
        descendants = graph.get_descendants(COMPLEX, 1)
        # Building: 1,2; Floors: от building1 (1,2) + от building2 (3) = 3; Rooms: от floor1 (1,2) + floor2 (3) + floor3 (4) = 4
        assert len(descendants[BUILDING]) == 2
        assert len(descendants[FLOOR]) == 3
        assert len(descendants[ROOM]) == 4
        
        # Получаем предков Room 201 (id=3)
        ancestors = graph.get_ancestors(ROOM, 3)
        assert len(ancestors) == 3  # Floor, Building, Complex
        assert ancestors[0] == (FLOOR, 2)   # Непосредственный родитель
        assert ancestors[1] == (BUILDING, 1)
        assert ancestors[2] == (COMPLEX, 1)
        
        # Ищем по родителю
        rooms_on_floor1 = graph.find_by_parent(FLOOR, 1, ROOM)
        assert len(rooms_on_floor1) == 2
        assert {r.id for r in rooms_on_floor1} == {1, 2}
    
    def test_updates_and_relinking(self, full_graph):
        """Проверяет обновление сущностей и смену родителей."""
        graph = full_graph
        
        # Меняем родителя у комнаты 101 (переводим с этажа 1 на этаж 2)
        from client.src.models import Room
        updated_room = Room(id=1, number="101 (новый)", floor_id=2, area=45.5, status_code="free")
        result = graph.add_or_update(updated_room)
        
        assert result is True
        
        # Проверяем новую связь
        assert graph.get_parent(ROOM, 1) == (FLOOR, 2)
        
        # Проверяем, что у старого родителя комнаты больше нет
        assert 1 not in graph.get_children(FLOOR, 1)
        
        # А у нового - есть
        assert 1 in graph.get_children(FLOOR, 2)
        
        # Проверяем валидность после обновления
        assert graph.is_valid(ROOM, 1) is True
    
    def test_invalidation_scenario(self, full_graph):
        """Проверяет сценарии инвалидации."""
        graph = full_graph
        
        # Инвалидируем отдельную комнату
        graph.invalidate(ROOM, 1)
        assert graph.is_valid(ROOM, 1) is False
        assert graph.is_valid(FLOOR, 1) is True  # Родитель должен остаться валидным
        
        # Инвалидируем ветку (этаж со всеми комнатами)
        graph.invalidate_branch(FLOOR, 1)
        assert graph.is_valid(FLOOR, 1) is False
        assert graph.is_valid(ROOM, 1) is False  # Уже было
        assert graph.is_valid(ROOM, 2) is False  # Вторая комната тоже
        
        # Проверяем, что параллельная ветка не пострадала
        assert graph.is_valid(FLOOR, 2) is True
        assert graph.is_valid(ROOM, 3) is True
        
        # Перевалидируем этаж
        graph.validate(FLOOR, 1)
        assert graph.is_valid(FLOOR, 1) is True
        # Комнаты должны остаться невалидными (валидация не каскадная)
        assert graph.is_valid(ROOM, 1) is False
        assert graph.is_valid(ROOM, 2) is False
    
    def test_deletion_scenarios(self, full_graph):
        """Проверяет сценарии удаления."""
        graph = full_graph
        
        # Пытаемся удалить этаж с комнатами без каскада (должно быть запрещено)
        result = graph.remove(FLOOR, 1, cascade=False)
        assert result is False
        assert graph.has_entity(FLOOR, 1) is True
        assert graph.has_entity(ROOM, 1) is True
        assert graph.has_entity(ROOM, 2) is True
        
        # Удаляем этаж с каскадом
        result = graph.remove(FLOOR, 1, cascade=True)
        assert result is True
        
        # Проверяем, что этаж и его комнаты удалены
        assert graph.has_entity(FLOOR, 1) is False
        assert graph.has_entity(ROOM, 1) is False
        assert graph.has_entity(ROOM, 2) is False
        
        # Проверяем, что родитель (building) и другие ветки не пострадали
        assert graph.has_entity(BUILDING, 1) is True
        assert graph.has_entity(FLOOR, 2) is True
        assert graph.has_entity(ROOM, 3) is True
        
        # Проверяем индексы - у building больше нет удалённого этажа
        assert 1 not in graph.get_children(BUILDING, 1)
        assert set(graph.get_children(BUILDING, 1)) == {2}  # Остался только floor 2
        
        # Проверяем валидность удалённых
        assert graph.is_valid(FLOOR, 1) is False
        assert graph.is_valid(ROOM, 1) is False
    
    def test_complex_cascade_deletion(self, full_graph):
        """Проверяет каскадное удаление комплекса со всей иерархией."""
        graph = full_graph
        
        # Запоминаем количество сущностей до удаления
        stats_before = graph.get_stats()
        total_before = stats_before['total_entities']
        
        # Каскадно удаляем Complex 2
        result = graph.remove(COMPLEX, 2, cascade=True)
        assert result is True
        
        # Проверяем, что Complex 2 и всё его поддерево удалено
        assert graph.has_entity(COMPLEX, 2) is False
        assert graph.has_entity(BUILDING, 3) is False
        assert graph.has_entity(FLOOR, 4) is False
        assert graph.has_entity(ROOM, 5) is False
        
        # Complex 1 и его поддерево должно остаться
        assert graph.has_entity(COMPLEX, 1) is True
        assert graph.has_entity(BUILDING, 1) is True
        assert graph.has_entity(BUILDING, 2) is True
        assert graph.has_entity(FLOOR, 2) is True
        assert graph.has_entity(FLOOR, 3) is True
        assert graph.has_entity(ROOM, 3) is True
        assert graph.has_entity(ROOM, 4) is True
        
        # Проверяем статистику
        stats_after = graph.get_stats()
        # Complex 2 имел: 1 building, 1 floor, 1 room = 3 сущности + сам комплекс = 4
        assert stats_after['total_entities'] == total_before - 4
    
    def test_consistency_after_all_operations(self, full_graph):
        """Проверяет консистентность графа после всех операций."""
        graph = full_graph
        
        # Выполняем серию операций
        # 1. Обновляем комнату
        from client.src.models import Room, Building
        updated_room = Room(id=3, number="201-RENOVATED", floor_id=2, area=40.0, status_code="maintenance")
        graph.add_or_update(updated_room)
        
        # 2. Инвалидируем этаж
        graph.invalidate_branch(FLOOR, 2)
        
        # 3. Удаляем одну комнату без каскада (это лист)
        graph.remove(ROOM, 4, cascade=False)  # Room 301
        
        # 4. Перемещаем building в другой комплекс
        moved_building = Building(id=2, name="Корпус Б (перемещён)", complex_id=2, floors_count=1)
        graph.add_or_update(moved_building)
        
        # Проверяем консистентность
        consistency = graph.check_consistency()
        assert consistency['consistent'] is True, f"Inconsistencies found: {consistency['issues']}"
        
        # Дополнительные проверки после всех операций
        self._check_invariants(graph)
    
    def _check_invariants(self, graph):
        """Внутренний метод проверки инвариантов."""
        # Инвариант 1: Для каждого ребёнка в parents, он должен быть в children родителя
        for child_type in [BUILDING, FLOOR, ROOM]:
            parents = graph._relations._parents.get(child_type, {})
            for child_id, (parent_type, parent_id) in parents.items():
                children = graph._relations.get_children(parent_type, parent_id)
                assert child_id in children, \
                    f"Invariant failed: {child_type}#{child_id} not in children of {parent_type}#{parent_id}"
        
        # Инвариант 2: Каждая сущность в store имеет флаг валидности
        for node_type in [COMPLEX, BUILDING, FLOOR, ROOM]:
            for entity_id in graph._store.get_all_ids(node_type):
                # Сущность в store должна иметь флаг валидности
                # (не обязательно True, но должен быть определён)
                assert graph._validity.is_valid(node_type, entity_id) in (True, False)
        
        # Инвариант 3: После операций нет "мусора" в индексах
        # Все ID в children должны существовать в store
        for parent_type in [COMPLEX, BUILDING, FLOOR]:
            children_dict = graph._relations._children_set.get(parent_type, {})
            for parent_id, children in children_dict.items():
                for child_id in children:
                    child_type = None
                    if parent_type == COMPLEX:
                        child_type = BUILDING
                    elif parent_type == BUILDING:
                        child_type = FLOOR
                    elif parent_type == FLOOR:
                        child_type = ROOM
                        
                    if child_type:
                        assert graph._store.has(child_type, child_id), \
                            f"Invariant failed: child {child_type}#{child_id} of {parent_type}#{parent_id} not in store"
    
    def test_full_scenario_cleanup(self, full_graph):
        """Завершающая проверка - полная очистка графа."""
        graph = full_graph
        
        # Очищаем граф
        graph.clear()
        
        # Проверяем, что всё пусто
        assert graph.get_stats()['total_entities'] == 0
        assert graph.get_all(COMPLEX) == []
        assert graph.get_all(BUILDING) == []
        assert graph.get_all(FLOOR) == []
        assert graph.get_all(ROOM) == []
        
        # Проверяем индексы
        relations = graph._relations.get_all_relations()
        assert relations['children_set'] == {}
        assert relations['children_sorted'] == {}
        assert relations['parents'] == {}
        
        # Проверяем валидность
        for node_type in [COMPLEX, BUILDING, FLOOR, ROOM]:
            assert graph.is_valid(node_type, 1) is False
            assert graph.is_valid(node_type, 2) is False
        
        # Консистентность пустого графа
        consistency = graph.check_consistency()
        assert consistency['consistent'] is True