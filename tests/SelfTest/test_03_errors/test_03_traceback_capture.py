"""
Тест 3: Traceback capture.

Проверяет, что traceback ошибки корректно сохраняется
в результатах теста.
"""

from utils.Tester.common.test_common import test
import traceback


@test("Глубокий traceback")
def test_deep_traceback():
    """
    Тест с глубокой вложенностью для проверки traceback.
    """
    
    def level1(x):
        print(f"level1({x})")
        return level2(x + 1)
    
    def level2(x):
        print(f"level2({x})")
        return level3(x * 2)
    
    def level3(x):
        print(f"level3({x})")
        return level4(x - 5)
    
    def level4(x):
        print(f"level4({x})")
        return level5(x / 0)  # Здесь будет ZeroDivisionError
    
    def level5(x):
        print(f"level5({x})")
        return x * 2
    
    # Запускаем цепочку
    result = level1(10)
    print(f"Результат: {result}")


@test("Traceback с лямбда-функциями")
def test_lambda_traceback():
    """
    Тест с лямбда-функциями в traceback.
    """
    functions = [
        lambda x: x * 2,
        lambda x: x + 1,
        lambda x: x / 0,  # Здесь ошибка
        lambda x: x ** 2,
    ]
    
    def apply_all(x):
        print(f"Начальное значение: {x}")
        for i, func in enumerate(functions):
            print(f"Применяем функцию {i}")
            x = func(x)
            print(f"  результат: {x}")
        return x
    
    apply_all(42)


@test("Traceback с декораторами")
def test_decorator_traceback():
    """
    Тест с декорированными функциями.
    """
    
    def log_call(func):
        def wrapper(*args, **kwargs):
            print(f"Вызов {func.__name__} с args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                print(f"  результат: {result}")
                return result
            except Exception as e:
                print(f"  ошибка: {e}")
                raise
        return wrapper
    
    def validate_positive(func):
        def wrapper(x):
            if x <= 0:
                raise ValueError(f"Аргумент должен быть положительным, получен {x}")
            return func(x)
        return wrapper
    
    @log_call
    @validate_positive
    def compute_square(x):
        return x * x
    
    @log_call
    @validate_positive
    def compute_reciprocal(x):
        return 1 / x
    
    # Эти вызовы работают
    print("=== Нормальные вызовы ===")
    compute_square(5)
    compute_reciprocal(2)
    
    # Этот вызов вызовет ошибку в декораторе
    print("\n=== Вызов с ошибкой в декораторе ===")
    compute_square(-3)
    
    # Этот вызов вызовет ошибку в функции
    print("\n=== Вызов с ошибкой в функции ===")
    compute_reciprocal(0)


@test("Traceback с генераторами")
def test_generator_traceback():
    """
    Тест с генераторами в traceback.
    """
    
    def number_generator(n):
        for i in range(n):
            print(f"Генератор: yielding {i}")
            yield i
    
    def filter_even(gen):
        for x in gen:
            print(f"Фильтр: проверяем {x}")
            if x % 2 == 0:
                print(f"  четное -> пропускаем")
                yield x
            else:
                print(f"  нечетное -> фильтруем")
    
    def process_numbers(gen):
        for x in gen:
            print(f"Обработка: {x}")
            if x == 4:
                # Ошибка при обработке
                raise RuntimeError(f"Ошибка при обработке числа {x}")
            yield x * 10
    
    # Создаем цепочку генераторов
    numbers = number_generator(10)
    even = filter_even(numbers)
    processed = process_numbers(even)
    
    # Итерируем
    result = list(processed)
    print(f"Результат: {result}")


@test("Traceback с многопоточностью")
def test_thread_traceback():
    """
    Тест с потоками (если раннер поддерживает).
    """
    import threading
    import time
    
    def worker(thread_id):
        print(f"Поток {thread_id} запущен")
        time.sleep(0.1)
        
        if thread_id == 2:
            # Ошибка во втором потоке
            raise ValueError(f"Ошибка в потоке {thread_id}")
        
        print(f"Поток {thread_id} завершен")
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()


@test("Проверка сохранения traceback")
def test_traceback_content():
    """
    Проверяет, что traceback содержит правильные имена файлов и номера строк.
    """
    import inspect
    
    def get_current_line():
        return inspect.currentframe().f_lineno
    
    def error_function():
        line = get_current_line() + 1  # Следующая строка
        raise RuntimeError(f"Ошибка на линии {line}")
    
    try:
        error_function()
    except Exception as e:
        # Сохраняем traceback
        tb = traceback.format_exc()
        print(f"Traceback:\n{tb}")
        
        # Проверяем, что в traceback есть наш файл
        assert __file__ in tb, "Traceback не содержит имя файла"
        assert "error_function" in tb, "Traceback не содержит имя функции"
        
        # Передаем ошибку дальше, чтобы тест упал
        raise