"""
Тест 3: Переход на предыдущую страницу.

Проверяет корректность перехода на предыдущую страницу
и возврат к ранее просмотренным элементам.
"""

from utils.Tester.common.test_common import test
from utils.Tester.ui.navigation import PaginatedList


@test("Переход на предыдущую страницу")
def test_prev_page_basic():
    """
    Проверяет базовый переход на предыдущую страницу.
    """
    items = [f"item_{i}" for i in range(30)]
    paginated = PaginatedList(items, page_size=10)
    
    # Сначала переходим на третью страницу
    paginated.next_page()
    paginated.next_page()
    assert paginated.current_page == 2
    assert paginated.current_page_items[0] == "item_20"
    
    # Переход на вторую
    result = paginated.prev_page()
    assert result is True
    assert paginated.current_page == 1
    assert paginated.current_page_items[0] == "item_10"
    
    # Переход на первую
    result = paginated.prev_page()
    assert result is True
    assert paginated.current_page == 0
    assert paginated.current_page_items[0] == "item_0"
    
    print(f"\n📋 Последовательные переходы назад:")
    print(f"   Страница 3 -> 2 -> 1")
    
    assert True


@test("Попытка перейти перед первой страницей")
def test_prev_before_first():
    """
    Проверяет поведение при попытке перейти перед первой страницей.
    """
    items = [f"item_{i}" for i in range(20)]
    paginated = PaginatedList(items, page_size=10)
    
    # Пытаемся перейти назад с первой страницы
    result = paginated.prev_page()
    assert result is False
    assert paginated.current_page == 0
    
    # Переходим на вторую и возвращаемся
    paginated.next_page()
    assert paginated.current_page == 1
    
    result = paginated.prev_page()
    assert result is True
    assert paginated.current_page == 0
    
    # Снова пытаемся перейти назад
    result = paginated.prev_page()
    assert result is False
    assert paginated.current_page == 0
    
    print(f"\n📋 Попытка перехода перед первой страницей:")
    print(f"   Результат: {result} (ожидалось False)")
    
    assert True


@test("Навигация вперед-назад")
def test_back_and_forth():
    """
    Проверяет навигацию вперед и назад в разных комбинациях.
    """
    items = list(range(30))  # 30 элементов, 3 страницы
    paginated = PaginatedList(items, page_size=10)
    
    # Сценарий навигации
    actions = [
        ('next', 1, list(range(10, 20))),
        ('next', 2, list(range(20, 30))),
        ('prev', 1, list(range(10, 20))),
        ('prev', 0, list(range(0, 10))),
        ('next', 1, list(range(10, 20))),
        ('next', 2, list(range(20, 30))),
        ('prev', 1, list(range(10, 20))),
    ]
    
    print(f"\n📋 Навигация вперед-назад:")
    
    for action, expected_page, expected_items in actions:
        if action == 'next':
            result = paginated.next_page()
        else:
            result = paginated.prev_page()
        
        assert result is True
        assert paginated.current_page == expected_page
        assert paginated.current_page_items == expected_items
        
        print(f"   {action}: страница {expected_page + 1}, "
              f"элементы {expected_items[0]}-{expected_items[-1]}")
    
    assert True


@test("Возврат к началу после перехода на последнюю")
def test_return_from_last():
    """
    Проверяет возврат к началу после перехода на последнюю страницу.
    """
    items = [f"item_{i}" for i in range(17)]  # 17 элементов, 2 страницы (10,7)
    paginated = PaginatedList(items, page_size=10)
    
    # Переходим на последнюю страницу
    paginated.next_page()
    assert paginated.current_page == 1
    last_items = paginated.current_page_items
    assert len(last_items) == 7
    
    # Возвращаемся назад
    paginated.prev_page()
    assert paginated.current_page == 0
    assert len(paginated.current_page_items) == 10
    
    # Снова вперед
    paginated.next_page()
    assert paginated.current_page == 1
    assert paginated.current_page_items == last_items
    
    print(f"\n📋 Возврат с последней страницы:")
    print(f"   Страница 2 -> 1 -> 2")
    
    assert True


@test("Сброс на первую страницу")
def test_reset_to_first():
    """
    Проверяет сброс на первую страницу.
    """
    items = list(range(25))
    paginated = PaginatedList(items, page_size=10)
    
    # Уходим на последнюю страницу
    paginated.next_page()
    paginated.next_page()
    assert paginated.current_page == 2
    
    # Сбрасываем
    paginated.reset()
    assert paginated.current_page == 0
    assert paginated.current_page_items == list(range(0, 10))
    
    print(f"\n📋 Сброс на первую страницу:")
    print(f"   Была страница 3, стала страница 1")
    
    assert True


@test("Переход на конкретную страницу")
def test_go_to_page():
    """
    Проверяет прямой переход на указанную страницу.
    """
    items = list(range(35))  # 35 элементов, 4 страницы (10,10,10,5)
    paginated = PaginatedList(items, page_size=10)
    
    test_cases = [
        (0, True, list(range(0, 10))),    # Первая
        (2, True, list(range(20, 30))),   # Третья
        (3, True, list(range(30, 35))),   # Последняя
        (1, True, list(range(10, 20))),   # Вторая
        (4, False, None),                  # За пределами
        (-1, False, None),                  # Отрицательная
    ]
    
    print(f"\n📋 Прямые переходы на страницы:")
    
    for page, expected_result, expected_items in test_cases:
        result = paginated.go_to_page(page)
        assert result == expected_result
        
        if expected_result:
            assert paginated.current_page == page
            assert paginated.current_page_items == expected_items
            print(f"   Страница {page + 1}: {expected_result}")
        else:
            print(f"   Страница {page + 1}: {expected_result} (не существует)")
    
    assert True