"""
Тест 1: AssertionError.

Проверяет, что тестер корректно обрабатывает AssertionError
и правильно сохраняет информацию об ошибке.
"""

from utils.Tester.common.test_common import test
import sys


@test("Простой AssertionError с числами")
def test_simple_assertion():
    """
    Тест с простым assert, который должен упасть.
    """
    a = 42
    b = 43
    print(f"Сравниваем {a} и {b}")
    
    # Этот assert упадет
    assert a == b, f"Числа не равны: {a} != {b}"
    
    # Этот код не выполнится
    print("Это сообщение не должно появиться")


@test("AssertionError со сложным выражением")
def test_complex_assertion():
    """
    Тест со сложным assert'ом.
    """
    data = {"users": ["Alice", "Bob", "Charlie"], "count": 3}
    
    print(f"Данные: {data}")
    
    # Проверка, которая упадет
    assert data["count"] == len(data["users"]), \
        f"Количество пользователей ({len(data['users'])}) " \
        f"не соответствует count ({data['count']})"
    
    # Увеличим count для ошибки
    data["count"] = 4
    
    # Этот assert упадет
    assert data["count"] == len(data["users"]), \
        f"После изменения: count={data['count']}, users={len(data['users'])}"


@test("Множественные assert'ы")
def test_multiple_asserts():
    """
    Тест с несколькими assert'ами.
    Первый должен пройти, второй упасть.
    """
    # Первый assert - проходит
    assert 1 + 1 == 2, "Базовая математика сломалась"
    print("✅ Первый assert прошел")
    
    # Второй assert - падает
    x = 10
    y = 20
    assert x > y, f"Ожидалось {x} > {y}, но это не так"
    
    # Третий assert - не должен выполняться
    assert False, "Этот assert не должен достигнуться"


@test("AssertionError с многострочным сообщением")
def test_multiline_assert():
    """
    Тест с многострочным сообщением об ошибке.
    """
    expected = [1, 2, 3, 4, 5]
    actual = [1, 2, 3, 4, 6]
    
    error_msg = (
        f"Списки не совпадают:\n"
        f"  Ожидалось: {expected}\n"
        f"  Получено:  {actual}\n"
        f"  Различие на позиции 4: {expected[4]} != {actual[4]}"
    )
    
    assert expected == actual, error_msg


@test("AssertionError внутри вложенной функции")
def test_nested_assertion():
    """
    Тест с assert'ом внутри вложенной функции.
    Проверяет, что traceback показывает правильную вложенность.
    """
    
    def validate_user(user):
        assert "name" in user, f"Пользователь не имеет имени: {user}"
        assert "age" in user, f"Пользователь {user['name']} не имеет возраста"
        assert user["age"] >= 0, f"Возраст не может быть отрицательным: {user['age']}"
        return True
    
    def process_users(users):
        results = []
        for i, user in enumerate(users):
            print(f"Обработка пользователя {i}: {user.get('name', 'Unknown')}")
            results.append(validate_user(user))
        return results
    
    # Корректные пользователи
    users = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie"},  # Этот вызовет ошибку (нет age)
    ]
    
    process_users(users)


@test("Проверка формата ошибки")
def test_error_format():
    """
    Проверяет, что сообщение об ошибке имеет правильный формат.
    Этот тест не выполняется напрямую, а используется для проверки
    формата отчета.
    """
    # Этот тест должен упасть с понятным сообщением
    import math
    result = math.sqrt(-1)  # В Python это вернет NaN, не ошибку
    
    # Лучше так:
    assert 1 / 0 == 2  # ZeroDivisionError