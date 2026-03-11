"""
Тест 2: Переход на следующую страницу.

Проверяет корректность перехода на следующую страницу
и обновление отображаемых элементов.
"""

from utils.Tester.common.test_common import test
from utils.Tester.ui.navigation import PaginatedList


@test("Переход на следующую страницу")
def test_next_page_basic():
    """
    Проверяет базовый переход на следующую страницу.
    """
    items = [f"item_{i}" for i in range(30)]
    paginated = PaginatedList(items, page_size=10)
    
    # Первая страница
    assert paginated.current_page == 0
    assert paginated.current_page_items[0] == "item_0"
    assert paginated.current_page_items[9] == "item_9"
    
    # Переход на вторую
    result = paginated.next_page()
    assert result is True
    assert paginated.current_page == 1
    assert paginated.current_page_items[0] == "item_10"
    assert paginated.current_page_items[9] == "item_19"
    
    # Переход на третью
    result = paginated.next_page()
    assert result is True
    assert paginated.current_page == 2
    assert paginated.current_page_items[0] == "item_20"
    assert paginated.current_page_items[9] == "item_29"
    
    print(f"\n📋 Последовательные переходы:")
    print(f"   Страница 1: items 0-9")
    print(f"   Страница 2: items 10-19")
    print(f"   Страница 3: items 20-29")
    
    assert True


@test("Переход на последнюю страницу")
def test_next_to_last_page():
    """
    Проверяет переход на последнюю страницу (неполную).
    """
    items = [f"item_{i}" for i in range(25)]  # 25 элементов, 3 страницы (10,10,5)
    paginated = PaginatedList(items, page_size=10)
    
    # Переходим на вторую
    paginated.next_page()
    assert paginated.current_page == 1
    assert len(paginated.current_page_items) == 10
    
    # Переходим на третью (последнюю)
    result = paginated.next_page()
    assert result is True
    assert paginated.current_page == 2
    assert len(paginated.current_page_items) == 5
    assert paginated.current_page_items[0] == "item_20"
    assert paginated.current_page_items[4] == "item_24"
    
    print(f"\n📋 Последняя страница (неполная):")
    print(f"   Элементов: {len(paginated.current_page_items)}")
    print(f"   Диапазон: {paginated.get_display_range()}")
    
    assert True


@test("Попытка перейти дальше последней страницы")
def test_next_beyond_last():
    """
    Проверяет поведение при попытке перейти дальше последней страницы.
    """
    items = [f"item_{i}" for i in range(15)]  # 15 элементов, 2 страницы (10,5)
    paginated = PaginatedList(items, page_size=10)
    
    # Переходим на вторую страницу
    paginated.next_page()
    assert paginated.current_page == 1
    
    # Пытаемся перейти на третью (не существует)
    result = paginated.next_page()
    assert result is False
    assert paginated.current_page == 1  # Страница не изменилась
    
    print(f"\n📋 Попытка перехода за последнюю страницу:")
    print(f"   Текущая страница: {paginated.current_page + 1}")
    print(f"   Результат: {result} (ожидалось False)")
    
    assert True


@test("Множественные переходы")
def test_multiple_next_pages():
    """
    Проверяет множество последовательных переходов.
    """
    items = list(range(50))  # 50 элементов, 5 страниц по 10
    paginated = PaginatedList(items, page_size=10)
    
    expected_pages = [
        (0, list(range(0, 10))),
        (1, list(range(10, 20))),
        (2, list(range(20, 30))),
        (3, list(range(30, 40))),
        (4, list(range(40, 50))),
    ]
    
    print(f"\n📋 Множественные переходы:")
    
    for page_num, expected_items in expected_pages:
        assert paginated.current_page == page_num
        assert paginated.current_page_items == expected_items
        print(f"   Страница {page_num + 1}: {expected_items[0]}...{expected_items[-1]}")
        
        if page_num < 4:
            result = paginated.next_page()
            assert result is True
    
    # После последней страницы переход невозможен
    result = paginated.next_page()
    assert result is False
    
    assert True


@test("Переход с разными размерами страниц")
def test_next_different_sizes():
    """
    Проверяет переходы при разных размерах страниц.
    """
    items = list(range(20))
    
    test_cases = [
        (5, [0, 1, 2, 3]),     # page_size=5 -> 4 страницы
        (8, [0, 1, 2]),         # page_size=8 -> 3 страницы
        (12, [0, 1]),           # page_size=12 -> 2 страницы
    ]
    
    for page_size, expected_pages in test_cases:
        paginated = PaginatedList(items, page_size=page_size)
        
        print(f"\n📋 Page size = {page_size}:")
        
        for expected_page in expected_pages:
            current = paginated.current_page
            first_item = paginated.current_page_items[0]
            last_item = paginated.current_page_items[-1]
            print(f"   Страница {current + 1}: [{first_item}..{last_item}]")
            
            if current < len(expected_pages) - 1:
                assert paginated.next_page() is True
        
        # После последней страницы
        assert paginated.next_page() is False
    
    assert True