"""
Тест 4: Граничные условия пагинации.

Проверяет корректную обработку выхода за границы страниц
и граничные случаи.
"""

from utils.Tester.common.test_common import test
from utils.Tester.ui.navigation import PaginatedList


@test("Границы при пустом списке")
def test_empty_bounds():
    """
    Проверяет граничные условия для пустого списка.
    """
    paginated = PaginatedList([])
    
    # Проверяем все навигационные методы
    assert not paginated.next_page()
    assert not paginated.prev_page()
    assert not paginated.go_to_page(0)
    assert not paginated.go_to_page(1)
    
    # Проверяем получение элементов
    assert paginated.get_by_global_index(1) is None
    assert paginated.get_by_local_index(1) is None
    
    # Проверяем свойства
    assert paginated.total_pages == 1
    assert paginated.current_page == 0
    assert paginated.current_page_items == []
    assert paginated.get_display_range() == "0/0"
    
    print(f"✅ Пустой список корректно обрабатывает границы")
    assert True


@test("Границы при одном элементе")
def test_single_item_bounds():
    """
    Проверяет граничные условия для списка с одним элементом.
    """
    paginated = PaginatedList(["only_one"])
    
    assert paginated.total_pages == 1
    assert paginated.current_page == 0
    assert paginated.current_page_items == ["only_one"]
    assert paginated.get_display_range() == "1-1/1"
    
    # Переходы не должны работать
    assert not paginated.next_page()
    assert not paginated.prev_page()
    
    # Получение элемента
    assert paginated.get_by_global_index(1) == "only_one"
    assert paginated.get_by_global_index(2) is None
    assert paginated.get_by_local_index(1) == "only_one"
    assert paginated.get_by_local_index(2) is None
    
    print(f"✅ Список с одним элементом: {paginated.get_display_range()}")
    assert True


@test("Границы при ровном количестве страниц")
def test_even_pages():
    """
    Проверяет границы при ровном количестве страниц.
    """
    items = list(range(30))  # 30 элементов, ровно 3 страницы по 10
    paginated = PaginatedList(items, page_size=10)
    
    # Переходим на последнюю страницу
    paginated.next_page()
    paginated.next_page()
    assert paginated.current_page == 2
    assert len(paginated.current_page_items) == 10
    assert paginated.current_page_items == list(range(20, 30))
    
    # Дальше перейти нельзя
    assert not paginated.next_page()
    assert paginated.current_page == 2
    
    # Назад можно
    assert paginated.prev_page()
    assert paginated.current_page == 1
    
    print(f"\n📋 Ровно 3 страницы по 10 элементов:")
    print(f"   Последняя страница полная: {paginated.get_display_range()}")
    
    assert True


@test("Границы при неполной последней странице")
def test_odd_pages():
    """
    Проверяет границы при неполной последней странице.
    """
    items = list(range(27))  # 27 элементов, 3 страницы (10,10,7)
    paginated = PaginatedList(items, page_size=10)
    
    # Проверяем размеры страниц
    assert len(paginated.current_page_items) == 10
    
    paginated.next_page()
    assert len(paginated.current_page_items) == 10
    
    paginated.next_page()
    assert len(paginated.current_page_items) == 7
    assert paginated.current_page_items == list(range(20, 27))
    
    # Проверяем диапазон последней страницы
    assert paginated.global_start_index == 21
    assert paginated.global_end_index == 27
    assert paginated.get_display_range() == "21-27/27"
    
    # Получение элементов на последней странице
    assert paginated.get_by_global_index(21) == 20
    assert paginated.get_by_global_index(27) == 26
    assert paginated.get_by_global_index(28) is None
    
    print(f"\n📋 Неполная последняя страница (7 элементов):")
    print(f"   {paginated.get_display_range()}")
    
    assert True


@test("Границы при большом количестве страниц")
def test_many_pages():
    """
    Проверяет границы при большом количестве страниц.
    """
    items = list(range(1000))  # 1000 элементов
    paginated = PaginatedList(items, page_size=10)
    
    assert paginated.total_pages == 100
    
    # Переходим на последнюю страницу
    for _ in range(99):
        paginated.next_page()
    
    assert paginated.current_page == 99
    assert len(paginated.current_page_items) == 10
    assert paginated.current_page_items == list(range(990, 1000))
    
    # Проверяем, что дальше нельзя
    assert not paginated.next_page()
    
    # Возвращаемся на первую
    paginated.reset()
    assert paginated.current_page == 0
    assert paginated.current_page_items == list(range(0, 10))
    
    print(f"\n📋 100 страниц по 10 элементов:")
    print(f"   Первая: 0-9")
    print(f"   Последняя: 990-999")
    
    assert True


@test("Границы при page_size = 1")
def test_page_size_one():
    """
    Проверяет границы при размере страницы в 1 элемент.
    """
    items = list(range(5))
    paginated = PaginatedList(items, page_size=1)
    
    assert paginated.total_pages == 5
    
    # Проверяем каждую страницу
    expected_items = [[i] for i in range(5)]
    
    for i in range(5):
        assert paginated.current_page == i
        assert paginated.current_page_items == expected_items[i]
        assert paginated.get_display_range() == f"{i+1}-{i+1}/5"
        
        if i < 4:
            assert paginated.next_page()
    
    # После последней
    assert not paginated.next_page()
    
    # Идем назад
    for i in range(4, -1, -1):
        assert paginated.current_page == i
        if i > 0:
            assert paginated.prev_page()
    
    # Перед первой
    assert not paginated.prev_page()
    
    print(f"\n📋 Page size = 1: 5 страниц по 1 элементу")
    
    assert True


@test("Получение элементов за границами")
def test_out_of_bounds_access():
    """
    Проверяет получение элементов за границами страниц.
    """
    items = list(range(15))
    paginated = PaginatedList(items, page_size=10)
    
    # Глобальные индексы
    assert paginated.get_by_global_index(0) is None  # Индекс с 0 (должен быть 1)
    assert paginated.get_by_global_index(16) is None  # За пределами
    
    # Локальные индексы на первой странице
    assert paginated.get_by_local_index(1) == 0
    assert paginated.get_by_local_index(10) == 9
    assert paginated.get_by_local_index(11) is None
    
    # Переходим на вторую страницу
    paginated.next_page()
    
    # Локальные индексы на второй странице
    assert paginated.get_by_local_index(1) == 10
    assert paginated.get_by_local_index(5) == 14
    assert paginated.get_by_local_index(6) is None
    
    print(f"\n📋 Доступ за границами возвращает None")
    
    assert True


@test("Сброс и повторная навигация")
def test_reset_and_navigate():
    """
    Проверяет сброс и повторную навигацию.
    """
    items = list(range(20))
    paginated = PaginatedList(items, page_size=10)
    
    # Навигация вперед-назад несколько раз
    for cycle in range(3):
        print(f"\n📋 Цикл {cycle + 1}:")
        
        # Вперед
        paginated.next_page()
        print(f"   После next: страница {paginated.current_page + 1}")
        
        # Назад
        paginated.prev_page()
        print(f"   После prev: страница {paginated.current_page + 1}")
        
        # Проверяем, что вернулись
        assert paginated.current_page == 0
        assert paginated.current_page_items == list(range(0, 10))
    
    # Сброс
    paginated.next_page()
    paginated.reset()
    assert paginated.current_page == 0
    
    print(f"\n✅ Сброс работает корректно после навигации")
    
    assert True