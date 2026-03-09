# utils/Tester/utils/helpers.py
"""
Вспомогательные функции для тестера.
Чистые утилиты без состояния.
"""

import os
import sys
import time
import hashlib
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Set, Callable
from datetime import datetime
import inspect
import fnmatch


# ========== 1. Работа с путями и файлами ==========

def ensure_dir(path: Path) -> Path:
    """
    Создает директорию, если её нет.
    
    Args:
        path: Путь к директории
        
    Returns:
        Path: Созданный путь
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_files(root: Path, pattern: str = "*.py", recursive: bool = True) -> List[Path]:
    """
    Находит файлы по паттерну.
    
    Args:
        root: Корневая директория
        pattern: Паттерн для поиска (например, "test_*.py")
        recursive: Искать рекурсивно
        
    Returns:
        List[Path]: Список найденных файлов
    """
    if recursive:
        return list(root.rglob(pattern))
    else:
        return list(root.glob(pattern))


def is_test_file(path: Path) -> bool:
    """
    Проверяет, является ли файл тестовым.
    
    Критерии:
    - Имя начинается с test_
    - Расширение .py
    - Не __init__.py
    """
    return (path.name.startswith('test_') and 
            path.suffix == '.py' and 
            path.name != '__init__.py')


def path_to_module(path: Path, root: Path) -> str:
    """
    Преобразует путь к файлу в имя модуля Python.
    
    Args:
        path: Полный путь к файлу
        root: Корневая директория проекта
        
    Returns:
        str: Имя модуля (например, 'tests.client.core.bus.test_01_basic')
    """
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        # Если файл вне проекта, используем абсолютный путь
        rel_path = path
    
    # Убираем расширение .py и преобразуем разделители в точки
    module_name = rel_path.with_suffix('').as_posix().replace('/', '.')
    return module_name


# ========== 2. Форматирование времени ==========

def format_duration(seconds: float) -> str:
    """
    Форматирует длительность в человекочитаемый вид.
    
    Examples:
        0.12 -> "120ms"
        1.5 -> "1.50s"
        125.3 -> "2m 5s"
    """
    if seconds < 0.001:
        return f"{seconds*1_000_000:.0f}µs"
    elif seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Форматирует временную метку.
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_size(bytes: int) -> str:
    """
    Форматирует размер в байтах.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}TB"


# ========== 3. Работа со строками ==========

def strip_ansi(text: str) -> str:
    """
    Удаляет ANSI escape последовательности из строки.
    """
    ansi_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_pattern.sub('', text)


def truncate(text: str, max_length: int = 100, ellipsis: str = "...") -> str:
    """
    Обрезает строку до максимальной длины.
    """
    if len(text) <= max_length:
        return text
    
    half = (max_length - len(ellipsis)) // 2
    return text[:half] + ellipsis + text[-half:]


def camel_to_snake(name: str) -> str:
    """
    Преобразует CamelCase в snake_case.
    
    Example:
        camel_to_snake("TestFunction") -> "test_function"
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name: str) -> str:
    """
    Преобразует snake_case в CamelCase.
    
    Example:
        snake_to_camel("test_function") -> "TestFunction"
    """
    return ''.join(word.capitalize() for word in name.split('_'))


# ========== 4. Хеширование и идентификаторы ==========

def compute_hash(obj: Any) -> str:
    """
    Вычисляет хеш объекта.
    Полезно для кэширования.
    """
    if isinstance(obj, (str, bytes)):
        data = obj if isinstance(obj, bytes) else obj.encode('utf-8')
    else:
        data = str(obj).encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()[:16]


def generate_test_id(module_path: str, test_name: str) -> str:
    """
    Генерирует уникальный ID теста.
    
    Format: "module_path::test_name"
    """
    return f"{module_path}::{test_name}"


def parse_test_id(test_id: str) -> tuple[str, str]:
    """
    Разбирает test_id на компоненты.
    
    Returns:
        tuple[module_path, test_name]
    """
    parts = test_id.split('::', 1)
    if len(parts) != 2:
        raise ValueError(f"Неверный формат test_id: {test_id}")
    return parts[0], parts[1]


# ========== 5. Фильтрация и группировка ==========

def filter_by_patterns(items: List[str], patterns: List[str]) -> List[str]:
    """
    Фильтрует список строк по паттернам (fnmatch).
    
    Args:
        items: Список строк
        patterns: Список паттернов (поддерживает * и ?)
        
    Returns:
        List[str]: Отфильтрованные строки
    """
    if not patterns:
        return items
    
    result = []
    for item in items:
        if any(fnmatch.fnmatch(item, p) for p in patterns):
            result.append(item)
    
    return result


def group_by(items: List[Any], key_func: Callable) -> Dict[Any, List[Any]]:
    """
    Группирует элементы по ключу.
    
    Example:
        group_by(results, lambda r: r.status)
    """
    groups = {}
    for item in items:
        key = key_func(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups


def unique(sequence: List[Any]) -> List[Any]:
    """
    Возвращает уникальные элементы, сохраняя порядок.
    """
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


# ========== 6. Загрузка/сохранение конфигов ==========

def load_json_config(path: Path) -> Dict[str, Any]:
    """
    Загружает JSON конфиг.
    """
    if not path.exists():
        return {}
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки конфига {path}: {e}")
        return {}


def save_json_config(path: Path, data: Dict[str, Any]) -> bool:
    """
    Сохраняет JSON конфиг.
    """
    try:
        ensure_dir(path.parent)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения конфига {path}: {e}")
        return False


# ========== 7. Интроспекция ==========

def get_function_info(func: Callable) -> Dict[str, Any]:
    """
    Извлекает информацию о функции.
    """
    try:
        source_lines, line_no = inspect.getsourcelines(func)
        source_file = inspect.getsourcefile(func)
        
        return {
            'name': func.__name__,
            'module': func.__module__,
            'file': source_file,
            'line': line_no,
            'docstring': inspect.getdoc(func),
            'signature': str(inspect.signature(func)),
            'source': ''.join(source_lines).strip()
        }
    except Exception as e:
        return {
            'name': func.__name__,
            'module': func.__module__,
            'error': str(e)
        }


def is_coroutine(func: Callable) -> bool:
    """Проверяет, является ли функция корутиной (async def)"""
    return inspect.iscoroutinefunction(func)


def get_callable_name(obj: Any) -> str:
    """Возвращает имя вызываемого объекта"""
    if hasattr(obj, '__name__'):
        return obj.__name__
    if hasattr(obj, '__class__'):
        return obj.__class__.__name__
    return str(obj)


# ========== 8. Терминал ==========

def get_terminal_size() -> tuple[int, int]:
    """
    Возвращает размер терминала (ширина, высота).
    """
    try:
        import shutil
        size = shutil.get_terminal_size()
        return size.columns, size.lines
    except Exception:
        return 80, 24


def clear_screen():
    """Очищает экран терминала"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_centered(text: str, width: Optional[int] = None):
    """Печатает текст по центру"""
    if width is None:
        width, _ = get_terminal_size()
    
    lines = text.split('\n')
    for line in lines:
        print(line.center(width))


def print_table(headers: List[str], rows: List[List[str]], max_width: int = 80):
    """
    Печатает простую таблицу.
    
    Example:
        print_table(['Test', 'Status'], [['test1', '✓'], ['test2', '✗']])
    """
    if not rows:
        return
    
    # Вычисляем ширину колонок
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Ограничиваем общую ширину
    total_width = sum(col_widths) + 3 * (len(headers) - 1)
    if total_width > max_width:
        # Уменьшаем колонки пропорционально
        scale = max_width / total_width
        col_widths = [int(w * scale) for w in col_widths]
    
    # Печатаем заголовки
    header_line = ' | '.join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print('-' * len(header_line))
    
    # Печатаем строки
    for row in rows:
        line = ' | '.join(str(cell).ljust(w) for cell, w in zip(row, col_widths))
        print(line)


# ========== 9. Версионирование ==========

def get_version() -> str:
    """
    Возвращает версию тестера.
    """
    return "1.1.0"


def get_python_version() -> str:
    """Возвращает версию Python"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


# ========== 10. Декораторы ==========

def memoize(func: Callable) -> Callable:
    """
    Декоратор для кэширования результатов функции.
    """
    cache = {}
    
    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Декоратор для повторных попыток выполнения функции.
    
    Example:
        @retry(max_attempts=3, delay=0.5)
        def flaky_function():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            raise last_error
        return wrapper
    return decorator
    
def get_input_line() -> str:
    """
    Читает строку ввода с поддержкой backspace.
    Кроссплатформенная версия.
    """
    import sys
    import os
    
    chars = []
    
    if os.name == 'nt':  # Windows
        import msvcrt
        while True:
            ch = msvcrt.getch().decode('utf-8', errors='ignore')
            if ch == '\r':  # Enter
                print()
                break
            elif ch == '\b' and chars:  # Backspace
                chars.pop()
                print('\b \b', end='', flush=True)
            elif ch.isprintable():
                chars.append(ch)
                print(ch, end='', flush=True)
    else:  # Unix
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ('\r', '\n'):
                    print()
                    break
                elif ord(ch) == 127:  # Backspace
                    if chars:
                        chars.pop()
                        print('\b \b', end='', flush=True)
                else:
                    chars.append(ch)
                    print(ch, end='', flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    
    return ''.join(chars)