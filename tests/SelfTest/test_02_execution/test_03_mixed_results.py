"""
Тест 3: Смесь успешных и падающих тестов.

Проверяет, что тестер корректно обрабатывает ситуацию,
когда одни тесты проходят, а другие падают.
"""

from utils.Tester.common.test_common import test
import random


# Счетчики для статистики
_passed_count = 0
_failed_count = 0


@test("Успешный тест #1")
def test_pass_1():
    """
    Первый успешный тест.
    """
    global _passed_count
    _passed_count += 1
    print(f"✅ Успешный тест #1 (всего успешно: {_passed_count})")
    assert 1 == 1


@test("Падающий тест #1")
def test_fail_1():
    """
    Первый падающий тест (AssertionError).
    """
    global _failed_count
    _failed_count += 1
    print(f"❌ Падающий тест #1 (всего падений: {_failed_count})")
    
    # Этот тест должен упасть
    expected = 42
    actual = 43
    assert expected == actual, f"Ожидалось {expected}, получено {actual}"


@test("Успешный тест #2")
def test_pass_2():
    """
    Второй успешный тест.
    """
    global _passed_count
    _passed_count += 1
    print(f"✅ Успешный тест #2 (всего успешно: {_passed_count})")
    assert "hello".isalpha() is True


@test("Падающий тест #2 (исключение)")
def test_fail_2_exception():
    """
    Второй падающий тест (исключение).
    """
    global _failed_count
    _failed_count += 1
    print(f"❌ Падающий тест #2 (всего падений: {_failed_count})")
    
    # Генерируем исключение
    raise ValueError("Это тестовое исключение")


@test("Успешный тест #3")
def test_pass_3():
    """
    Третий успешный тест.
    """
    global _passed_count
    _passed_count += 1
    print(f"✅ Успешный тест #3 (всего успешно: {_passed_count})")
    assert [1, 2, 3].count(2) == 1


@test("Падающий тест #3 (сложный)")
def test_fail_3_complex():
    """
    Третий падающий тест со сложной проверкой.
    """
    global _failed_count
    _failed_count += 1
    print(f"❌ Падающий тест #3 (всего падений: {_failed_count})")
    
    # Сложная проверка, которая упадет
    data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
    
    # Намеренная ошибка
    assert len(data["users"]) == 3, f"Ожидалось 3 пользователя, найдено {len(data['users'])}"


@test("Проверка итоговой статистики")
def test_check_mixed_results():
    """
    Проверяет, что статистика смешанных результатов корректна.
    """
    global _passed_count, _failed_count
    
    print(f"\n📊 Итоговая статистика:")
    print(f"   ✅ Успешных тестов: {_passed_count}")
    print(f"   ❌ Падающих тестов: {_failed_count}")
    
    # Должно быть 3 успешных и 3 падающих
    assert _passed_count == 3, f"Ожидалось 3 успешных, получено {_passed_count}"
    assert _failed_count == 3, f"Ожидалось 3 падающих, получено {_failed_count}"
    assert _passed_count + _failed_count == 6


@test("Тест с вероятностным поведением")
def test_probabilistic():
    """
    Тест, который может как пройти, так и упасть
    (для проверки детерминизма).
    """
    # Если seed фиксирован, этот тест всегда будет проходить
    # или всегда падать в зависимости от seed
    value = random.randint(1, 10)
    print(f"🎲 Случайное значение: {value}")
    
    # При seed=42 это всегда 2
    assert value <= 10, "Значение должно быть в диапазоне"