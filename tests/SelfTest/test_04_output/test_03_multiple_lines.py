"""
Тест 3: Многострочный вывод.

Проверяет, что тестер корректно перехватывает и сохраняет
многострочный вывод в обоих потоках.
"""

from utils.Tester.common.test_common import test
import sys


@test("Многострочный текст в stdout")
def test_multiline_stdout():
    """
    Тест с многострочным текстом в stdout.
    """
    multiline = """
Это первая строка
Это вторая строка
Это третья строка
    С отступом
        И еще с отступом
    
    Пустая строка выше
    
И последняя строка
"""
    print(multiline)
    
    assert True


@test("Многострочный текст в stderr")
def test_multiline_stderr():
    """
    Тест с многострочным текстом в stderr.
    """
    error_message = """
╔════════════════════════════════════╗
║       МНОГОСТРОЧНАЯ ОШИБКА         ║
╠════════════════════════════════════╣
║  • Пункт 1                         ║
║  • Пункт 2                         ║
║  • Пункт 3                         ║
╚════════════════════════════════════╝
"""
    print(error_message, file=sys.stderr)
    
    assert True


@test("Смешанный многострочный вывод")
def test_mixed_multiline():
    """
    Тест с многострочным выводом в оба потока.
    """
    # Сначала несколько строк в stdout
    print("STDOUT строка 1")
    print("STDOUT строка 2")
    print("STDOUT строка 3")
    
    # Потом несколько строк в stderr
    print("STDERR строка 1", file=sys.stderr)
    print("STDERR строка 2", file=sys.stderr)
    print("STDERR строка 3", file=sys.stderr)
    
    # Перемежающийся вывод
    print("STDOUT после stderr 1")
    print("STDERR после stdout 2", file=sys.stderr)
    print("STDOUT еще один")
    print("STDERR последний", file=sys.stderr)
    
    assert True


@test("Многострочный вывод из циклов")
def test_loop_multiline():
    """
    Тест с многострочным выводом из циклов.
    """
    print("Генерация таблицы:")
    print("-" * 40)
    
    for i in range(1, 6):
        row = []
        for j in range(1, 6):
            row.append(f"{i*j:4d}")
        print(" ".join(row))
    
    print("-" * 40)
    print("Таблица сгенерирована")
    
    assert True


@test("Многострочный вывод с форматированием")
def test_formatted_multiline():
    """
    Тест с форматированным многострочным выводом.
    """
    data = [
        {"name": "Alice", "age": 30, "score": 95.5},
        {"name": "Bob", "age": 25, "score": 87.0},
        {"name": "Charlie", "age": 35, "score": 92.3},
        {"name": "Diana", "age": 28, "score": 98.7},
    ]
    
    # Заголовок таблицы
    print("=" * 50)
    print(f"{'Имя':<10} {'Возраст':<10} {'Баллы':<10} {'Статус':<10}")
    print("=" * 50)
    
    # Строки таблицы
    for person in data:
        status = "✅" if person["score"] >= 90 else "⚠️"
        print(f"{person['name']:<10} {person['age']:<10} "
              f"{person['score']:<10.1f} {status:<10}")
    
    print("=" * 50)
    print(f"Всего записей: {len(data)}")
    
    # То же самое в stderr
    print("\n" + "=" * 50, file=sys.stderr)
    print("ЛОГ ВЫПОЛНЕНИЯ:", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    
    for i, person in enumerate(data, 1):
        print(f"  {i}. {person['name']} обработан", file=sys.stderr)
    
    print("=" * 50, file=sys.stderr)
    
    assert True


@test("Многострочный вывод с разделителями")
def test_multiline_with_separators():
    """
    Тест с многострочным выводом и разными разделителями.
    """
    # Разные стили разделителей
    separators = [
        ("=", 50),
        ("-", 40),
        ("*", 30),
        (".", 20),
        ("#", 25),
    ]
    
    for char, length in separators:
        print(char * length)
        print(f"Разделитель '{char}' длиной {length}")
        print(char * length)
        print()
    
    # Вложенные блоки
    print("┌─────────────────────┐")
    print("│  Блок 1             │")
    print("│  ┌─────────────────┐│")
    print("│  │  Блок 1.1       ││")
    print("│  │  ┌─────────────┐││")
    print("│  │  │  Блок 1.1.1 │││")
    print("│  │  └─────────────┘││")
    print("│  └─────────────────┘│")
    print("└─────────────────────┘")
    
    assert True


@test("Очень большой многострочный вывод")
def test_very_large_multiline():
    """
    Тест с очень большим объемом многострочного вывода.
    """
    print("Начинаем генерацию большого вывода...")
    
    # 100 строк в stdout
    for i in range(100):
        print(f"STDOUT строка {i+1:3d}: " + "X" * (i % 50 + 10))
    
    # 50 строк в stderr
    for i in range(50):
        print(f"STDERR строка {i+1:3d}: " + "!" * (i % 30 + 5), 
              file=sys.stderr)
    
    # Перемежающийся вывод
    for i in range(20):
        print(f"OUT {i:2d}")
        print(f"ERR {i:2d}", file=sys.stderr)
    
    print("Генерация завершена")
    
    assert True


@test("Многострочный вывод с escape-последовательностями")
def test_escape_sequences():
    """
    Тест с escape-последовательностями в выводе.
    """
    # Табуляция
    print("С\tтабуляцией\tмежду\tсловами")
    
    # Новая строка внутри строки
    print("Строка с\nпереносом\nстроки")
    
    # Возврат каретки (может не работать в захвате)
    print("С возвратом каретки\rНовое начало")
    
    # Управляющие символы ANSI (цвета)
    print("\033[91mКрасный текст\033[0m")
    print("\033[92mЗеленый текст\033[0m")
    print("\033[93mЖелтый текст\033[0m")
    
    # Комбинации
    print("\033[1;94mЖирный синий текст\033[0m")
    print("\033[4;31mПодчеркнутый красный\033[0m")
    
    assert True


@test("Проверка захвата вывода")
def test_output_capture():
    """
    Проверяет, что вывод действительно захватывается.
    Этот тест должен показать весь вывод в отчете.
    """
    import sys
    
    # Сохраняем оригинальный stdout
    original_stdout = sys.stdout
    
    print("1. Этот текст должен быть в отчете")
    print("2. И этот тоже", file=sys.stderr)
    print("3. И даже этот с табуляцией:\t\tтабуляция")
    print("4. Многострочный\nвывод\nработает")
    
    # Проверяем, что stdout не равен оригинальному
    # (должен быть перенаправлен тестером)
    assert sys.stdout != original_stdout
    
    # Возвращаем обратно для чистоты
    sys.stdout = original_stdout
    
    print("5. А это уже напрямую в консоль")
    
    assert True