"""
Тест 1: Перехват stdout.

Проверяет, что тестер корректно перехватывает и сохраняет
вывод в stdout во время выполнения теста.
"""

from utils.Tester.common.test_common import test
import sys


@test("Простой вывод в stdout")
def test_simple_stdout():
    """
    Тест с простым print в stdout.
    """
    print("Это сообщение в stdout")
    print("Еще одно сообщение")
    print("И третье")
    
    # Проверка все еще работает
    assert True


@test("Вывод с разными параметрами print")
def test_stdout_with_params():
    """
    Тест с разными параметрами print.
    """
    print("Без разделителя", "и", "без", "запятых")
    print("С", "разделителем", sep="-")
    print("С", "концом", end="!!!\n")
    print("С", "обоими", sep=":", end="***\n")
    
    # Пустой print
    print()
    
    # Print в одну строку
    for i in range(3):
        print(i, end=" ")
    print()  # Новая строка
    
    assert 1 + 1 == 2


@test("Вывод с форматированием")
def test_stdout_formatting():
    """
    Тест с форматированным выводом.
    """
    name = "Alice"
    age = 30
    score = 95.5
    
    # f-strings
    print(f"Имя: {name}, Возраст: {age}, Баллы: {score}")
    
    # format
    print("Имя: {}, Возраст: {}, Баллы: {}".format(name, age, score))
    
    # % formatting
    print("Имя: %s, Возраст: %d, Баллы: %.1f" % (name, age, score))
    
    # Многострочный f-string
    print(f"""
    Информация о пользователе:
    -------------------------
    Имя: {name}
    Возраст: {age}
    Баллы: {score}
    -------------------------
    """)
    
    assert True


@test("Вывод внутри циклов")
def test_stdout_loops():
    """
    Тест с выводом внутри циклов.
    """
    print("Начинаем цикл:")
    
    for i in range(5):
        print(f"  Итерация {i}: значение = {i * 10}")
        
        if i == 2:
            print("    Специальное сообщение на итерации 2")
    
    print("Цикл завершен")
    
    # Вложенные циклы
    print("\nТаблица умножения 3x3:")
    for i in range(1, 4):
        row = []
        for j in range(1, 4):
            row.append(f"{i*j:2d}")
        print("  " + " ".join(row))
    
    assert True


@test("Вывод с условиями")
def test_stdout_conditional():
    """
    Тест с условным выводом.
    """
    x = 42
    y = 43
    
    print(f"x = {x}, y = {y}")
    
    if x < y:
        print(f"{x} меньше {y}")
    elif x > y:
        print(f"{x} больше {y}")
    else:
        print(f"{x} равно {y}")
    
    # Тернарный оператор
    status = "положительное" if x > 0 else "отрицательное"
    print(f"x - {status} число")
    
    assert True


@test("Вывод из вложенных функций")
def test_stdout_nested():
    """
    Тест с выводом из вложенных функций.
    """
    
    def outer_function(msg):
        print(f"Внешняя функция: {msg}")
        inner_function(msg.upper())
        return "готово"
    
    def inner_function(msg):
        print(f"  Внутренняя функция: {msg}")
        deeper_function(msg * 2)
    
    def deeper_function(msg):
        print(f"    Самая глубокая: {msg}")
    
    result = outer_function("тест")
    print(f"Результат: {result}")


@test("Вывод из обработчиков исключений")
def test_stdout_exception_handling():
    """
    Тест с выводом в блоках try/except.
    """
    print("Начинаем обработку...")
    
    try:
        print("  Попытка выполнить операцию")
        x = 1 / 0  # ZeroDivisionError
        print("  Эта строка не выполнится")
    except ZeroDivisionError:
        print("  ⚠️ Поймано исключение ZeroDivisionError")
    finally:
        print("  Блок finally выполняется всегда")
    
    print("Продолжаем после исключения")
    
    # Несколько уровней
    try:
        try:
            data = {"key": "value"}
            print(f"  Данные: {data}")
            value = data["missing"]  # KeyError
        except KeyError:
            print("  ⚠️ Внутренний блок поймал KeyError")
            raise  # Пробрасываем дальше
    except KeyError:
        print("  ⚠️ Внешний блок тоже поймал KeyError")
    
    print("Завершено")


@test("Очень много вывода")
def test_large_output():
    """
    Тест с большим объемом вывода.
    """
    print("Генерация 100 строк вывода:")
    
    for i in range(100):
        print(f"  Строка #{i+1:3d}: " + "x" * (i % 50))
    
    print("Генерация завершена")
    
    assert True