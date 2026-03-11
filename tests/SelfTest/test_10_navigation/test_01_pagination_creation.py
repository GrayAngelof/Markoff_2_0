"""
Тест 1: Создание пагинированного списка.

Проверяет корректное создание PaginatedList с разными параметрами.
"""

from utils.Tester.common.test_common import test
from utils.Tester.ui.navigation import PaginatedList


@test("Создание пустого списка")
def test_empty_list():
    """
    Проверяет создание пагинированного списка без элементов.
    """
    paginated = PaginatedList([])
    
    assert paginated.total_pages == 1
    assert paginated.current_page == 0
    assert paginated.current_page_items == []
    assert paginated.global_start_index == 1
    assert paginated.global_end_index == 0
    assert paginated.get_display_range() == "0/0"
    
    # Проверяем навигацию
    assert not paginated.next_page()
    assert not paginated.prev_page()
    
    # Проверяем получение элементов
    assert paginated.get_by_global_index(1) is None
    assert paginated.get_by_local_index(1) is None
    
    print(f"✅ Пустой список: {paginated.get_display_range()}")
    assert True


@test("Создание списка с элементами")
def test_filled_list():
    """
    Проверяет создание списка с элементами.
    """
    items = [f"item_{i}" for i in range(25)]
    paginated = PaginatedList(items, page_size=10)
    
    # Проверяем базовые параметры
    assert paginated.total_pages == 3  # 25 элементов, страницы по 10 -> 3 страницы
    assert paginated.current_page == 0
    assert len(paginated.items) == 25
    
    # Проверяем первую страницу
    first_page = paginated.current_page_items
    assert len(first_page) == 10
    assert first_page[0] == "item_0"
    assert first_page[9] == "item_9"
    
    # Проверяем индексы
    assert paginated.global_start_index == 1
    assert paginated.global_end_index == 10
    assert paginated.get_display_range() == "1-10/25"
    
    print(f"\n📋 PaginatedList (25 items, page_size=10):")
    print(f"   Всего страниц: {paginated.total_pages}")
    print(f"   Текущая страница: {paginated.current_page + 1}")
    print(f"   Диапазон: {paginated.get_display_range()}")
    print(f"   Элементы: {[str(x) for x in first_page[:3]]}...")
    
    assert True


@test("Создание с разными размерами страниц")
def test_different_page_sizes():
    """
    Проверяет создание с разными размерами страниц.
    """
    items = list(range(50))
    
    test_cases = [
        (5, 10),   # page_size=5 -> 10 страниц
        (10, 5),   # page_size=10 -> 5 страниц
        (20, 3),   # page_size=20 -> 3 страницы
        (25, 2),   # page_size=25 -> 2 страницы
        (50, 1),   # page_size=50 -> 1 страница
        (100, 1),  # page_size=100 -> 1 страница (больше чем элементов)
    ]
    
    for page_size, expected_pages in test_cases:
        paginated = PaginatedList(items, page_size=page_size)
        
        assert paginated.total_pages == expected_pages
        print(f"   page_size={page_size:3d} -> страниц: {paginated.total_pages}")
        
        # Проверяем размер первой страницы
        first_page = paginated.current_page_items
        expected_first_size = min(page_size, len(items))
        assert len(first_page) == expected_first_size
    
    assert True


@test("Создание с нестандартными размерами")
def test_edge_page_sizes():
    """
    Проверяет создание с граничными размерами страниц.
    """
    items = list(range(10))
    
    # page_size = 1
    paginated = PaginatedList(items, page_size=1)
    assert paginated.total_pages == 10
    assert len(paginated.current_page_items) == 1
    assert paginated.current_page_items[0] == 0
    
    # page_size = len(items)
    paginated = PaginatedList(items, page_size=10)
    assert paginated.total_pages == 1
    assert len(paginated.current_page_items) == 10
    
    # page_size > len(items)
    paginated = PaginatedList(items, page_size=20)
    assert paginated.total_pages == 1
    assert len(paginated.current_page_items) == 10
    
    print(f"\n✅ Граничные размеры страниц работают корректно")
    assert True


@test("Проверка валидации параметров")
def test_parameter_validation():
    """
    Проверяет валидацию входных параметров.
    """
    # page_size должен быть положительным
    try:
        PaginatedList([1, 2, 3], page_size=0)
        assert False, "Должно быть исключение при page_size=0"
    except ValueError as e:
        print(f"✅ Корректная валидация: {e}")
    
    try:
        PaginatedList([1, 2, 3], page_size=-5)
        assert False, "Должно быть исключение при page_size<0"
    except ValueError as e:
        print(f"✅ Корректная валидация: {e}")
    
    # None как items
    try:
        PaginatedList(None)  # type: ignore
        assert False, "Должно быть исключение при items=None"
    except TypeError:
        print(f"✅ Корректная валидация: items=None")
    
    assert True


@test("Проверка глобальных и локальных индексов")
def test_index_conversion():
    """
    Проверяет преобразование между глобальными и локальными индексами.
    """
    items = [f"item_{i}" for i in range(25)]
    paginated = PaginatedList(items, page_size=10)
    
    # Первая страница
    assert paginated.global_start_index == 1
    assert paginated.global_end_index == 10
    
    # Получаем элементы по глобальному индексу
    assert paginated.get_by_global_index(1) == "item_0"
    assert paginated.get_by_global_index(10) == "item_9"
    assert paginated.get_by_global_index(11) is None
    
    # Переходим на вторую страницу
    paginated.next_page()
    assert paginated.global_start_index == 11
    assert paginated.global_end_index == 20
    
    assert paginated.get_by_global_index(11) == "item_10"
    assert paginated.get_by_global_index(20) == "item_19"
    
    # Переходим на третью страницу
    paginated.next_page()
    assert paginated.global_start_index == 21
    assert paginated.global_end_index == 25
    
    assert paginated.get_by_global_index(21) == "item_20"
    assert paginated.get_by_global_index(25) == "item_24"
    
    print(f"\n📊 Преобразование индексов работает корректно")
    assert True