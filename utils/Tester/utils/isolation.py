# utils/Tester/utils/isolation.py
"""
Механизмы изоляции тестов друг от друга и от окружения.

Обеспечивает:
- Сброс глобального состояния проекта
- Фиксацию случайности (детерминизм)
- Перехват вывода (stdout/stderr)
- Таймауты и защиту от зависаний
- Graceful shutdown
"""

import os
import sys
import random
import gc
import signal
import threading
import io
import contextlib
from typing import Optional, Callable, Any, Tuple, Dict, List
from pathlib import Path
import logging
import importlib
import traceback

logger = logging.getLogger(__name__)


# ========== 1. Сброс глобального состояния ==========

# Реестр глобальных объектов, которые нужно сбрасывать
# Расширяется по мере добавления новых синглтонов в проект
_GLOBAL_STATE_RESETTERS: List[Callable[[], None]] = []


def register_resetter(resetter: Callable[[], None]):
    """
    Регистрирует функцию для сброса глобального состояния.
    
    Используется компонентами проекта для добавления своих сбросчиков.
    
    Example:
        def reset_event_bus():
            EventBus._instance = None
        
        register_resetter(reset_event_bus)
    """
    _GLOBAL_STATE_RESETTERS.append(resetter)
    logger.debug(f"Зарегистрирован сбросчик состояния: {resetter.__name__}")


def reset_environment():
    """
    Полный сброс глобального состояния проекта.
    
    Сбрасывает:
    - Зарегистрированные синглтоны
    - Случайные seed'ы
    - Сборщик мусора
    - Кэши модулей (опционально)
    - Переменные окружения (опционально)
    """
    logger.debug("Сброс глобального состояния")
    
    # 1. Вызываем все зарегистрированные сбросчики
    for resetter in _GLOBAL_STATE_RESETTERS:
        try:
            resetter()
        except Exception as e:
            logger.warning(f"Ошибка при сбросе {resetter.__name__}: {e}")
    
    # 2. Принудительная сборка мусора
    gc.collect()
    
    # 3. Сброс random (на всякий случай, хотя set_deterministic_mode сделает то же)
    random.seed(0)


def reset_modules(keep_modules: Optional[List[str]] = None):
    """
    Сбрасывает кэш импортированных модулей.
    
    Args:
        keep_modules: Список модулей, которые нужно сохранить
                     (например, базовые библиотеки)
    """
    keep = keep_modules or ['utils', 'tests', 'client', 'backend']
    
    to_reload = []
    for name, module in list(sys.modules.items()):
        # Пропускаем встроенные модули и указанные для сохранения
        if name.startswith('_') or name in sys.builtin_module_names:
            continue
        
        # Проверяем, не является ли модуль частью проекта
        if any(name.startswith(k) for k in keep):
            to_reload.append(module)
    
    # Перезагружаем модули
    for module in to_reload:
        try:
            importlib.reload(module)
            logger.debug(f"Перезагружен модуль: {module.__name__}")
        except Exception as e:
            logger.warning(f"Не удалось перезагрузить {module.__name__}: {e}")


# ========== 2. Детерминированность ==========

def set_deterministic_mode(seed: int = 42):
    """
    Фиксирует все источники случайности для воспроизводимости тестов.
    
    Args:
        seed: Зерно для генератора случайных чисел
    """
    # 1. Стандартный random
    random.seed(seed)
    
    # 2. hash randomization (Python 3)
    os.environ['PYTHONHASHSEED'] = str(seed)
    
    # 3. numpy (если используется)
    try:
        import numpy as np
        np.random.seed(seed)
        logger.debug("Установлен seed для numpy")
    except ImportError:
        pass
    
    # 4. torch (если используется)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        logger.debug("Установлен seed для torch")
    except ImportError:
        pass
    
    # 5. tensorflow (если используется)
    try:
        import tensorflow as tf
        tf.random.set_seed(seed)
        logger.debug("Установлен seed для tensorflow")
    except ImportError:
        pass
    
    logger.debug(f"Установлен детерминированный режим с seed={seed}")


# ========== 3. Перехват вывода ==========

@contextlib.contextmanager
def capture_output():
    """
    Контекстный менеджер для перехвата stdout/stderr.
    
    Example:
        with capture_output() as (stdout, stderr):
            print("Hello")
            print("Error", file=sys.stderr)
        
        print(f"STDOUT: {stdout.getvalue()}")
        print(f"STDERR: {stderr.getvalue()}")
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    with contextlib.redirect_stdout(stdout_capture), \
         contextlib.redirect_stderr(stderr_capture):
        yield stdout_capture, stderr_capture


class OutputCapture:
    """
    Класс для перехвата вывода с возможностью восстановления.
    Полезно для временного отключения вывода.
    """
    
    def __init__(self):
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
        self._old_stdout = None
        self._old_stderr = None
    
    def start(self):
        """Начинает перехват"""
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
    
    def stop(self):
        """Прекращает перехват и возвращает захваченный вывод"""
        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr
        
        return self.stdout_capture.getvalue(), self.stderr_capture.getvalue()
    
    def clear(self):
        """Очищает захваченный вывод"""
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args):
        self.stop()


def suppress_output(func: Callable) -> Callable:
    """
    Декоратор для подавления вывода функции.
    Полезно для тестов, которые слишком шумят.
    
    Example:
        @suppress_output
        def noisy_function():
            print("This won't be seen")
    """
    def wrapper(*args, **kwargs):
        with capture_output():
            return func(*args, **kwargs)
    return wrapper


# ========== 4. Таймауты и защита от зависаний ==========

class TimeoutError(Exception):
    """Исключение при превышении таймаута"""
    pass


def timeout(seconds: int, error_message: str = "Function call timed out"):
    """
    Декоратор для установки таймаута на выполнение функции.
    
    Args:
        seconds: Максимальное время выполнения в секундах
        error_message: Сообщение об ошибке при таймауте
        
    Example:
        @timeout(5)
        def slow_function():
            time.sleep(10)  # Будет прервано через 5 секунд
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = []
            error = []
            
            def target():
                try:
                    result.append(func(*args, **kwargs))
                except Exception as e:
                    error.append(e)
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                raise TimeoutError(error_message)
            
            if error:
                raise error[0]
            
            return result[0]
        
        return wrapper
    return decorator


def run_with_timeout(func: Callable, timeout_sec: int, *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
    """
    Запускает функцию с таймаутом.
    
    Args:
        func: Функция для запуска
        timeout_sec: Таймаут в секундах
        *args, **kwargs: Аргументы функции
        
    Returns:
        Tuple[success, result, error_message]
    """
    result = []
    error = []
    
    def target():
        try:
            result.append(func(*args, **kwargs))
        except Exception as e:
            error.append(e)
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_sec)
    
    if thread.is_alive():
        return False, None, f"Timeout after {timeout_sec}s"
    
    if error:
        return False, None, str(error[0])
    
    return True, result[0], None


# ========== 5. Graceful Shutdown ==========

class ShutdownHandler:
    """
    Обработчик сигналов для корректного завершения.
    
    Пример:
        handler = ShutdownHandler()
        handler.register()
        
        # В долгой операции:
        if handler.should_stop:
            break
    """
    
    def __init__(self):
        self._stop = False
        self._original_handlers = {}
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигнала"""
        signal_name = signal.Signals(signum).name
        logger.warning(f"Получен сигнал {signal_name}, начинаем корректное завершение...")
        self._stop = True
        
        # Выводим информацию о том, где мы находились
        if frame:
            filename = frame.f_code.co_filename
            lineno = frame.f_lineno
            func = frame.f_code.co_name
            logger.warning(f"  В момент сигнала: {filename}:{lineno} в {func}()")
    
    def register(self):
        """Регистрирует обработчики сигналов"""
        signals = [signal.SIGINT, signal.SIGTERM]
        
        for sig in signals:
            try:
                self._original_handlers[sig] = signal.signal(sig, self._signal_handler)
                logger.debug(f"Зарегистрирован обработчик для {signal.Signals(sig).name}")
            except (ValueError, RuntimeError) as e:
                # Может не работать в потоках
                logger.debug(f"Не удалось зарегистрировать обработчик для {sig}: {e}")
    
    def restore(self):
        """Восстанавливает оригинальные обработчики"""
        for sig, handler in self._original_handlers.items():
            try:
                signal.signal(sig, handler)
                logger.debug(f"Восстановлен обработчик для {signal.Signals(sig).name}")
            except (ValueError, RuntimeError) as e:
                pass
    
    @property
    def should_stop(self) -> bool:
        """Проверяет, был ли получен сигнал остановки"""
        return self._stop
    
    def reset(self):
        """Сбрасывает флаг остановки"""
        self._stop = False
    
    def __enter__(self):
        self.register()
        return self
    
    def __exit__(self, *args):
        self.restore()


# ========== 6. Изоляция процессов ==========

def run_in_isolation(func: Callable, *args, **kwargs):
    """
    Запускает функцию в полностью изолированном окружении.
    Использует multiprocessing для максимальной изоляции.
    
    Args:
        func: Функция для запуска
        *args, **kwargs: Аргументы функции
        
    Returns:
        Tuple[success, result, error]
    """
    import multiprocessing
    import queue
    
    ctx = multiprocessing.get_context('spawn')
    result_queue = ctx.Queue()
    
    def target():
        try:
            # Полная изоляция окружения
            reset_environment()
            set_deterministic_mode(42)
            
            with capture_output() as (stdout, stderr):
                result = func(*args, **kwargs)
            
            result_queue.put(('success', result, stdout.getvalue(), stderr.getvalue()))
        except Exception as e:
            result_queue.put(('error', str(e), traceback.format_exc(), ''))
    
    process = ctx.Process(target=target)
    process.start()
    process.join(30)  # Максимальное время
    
    if process.is_alive():
        process.terminate()
        process.join()
        return False, None, "Process timeout"
    
    try:
        status, data, out, err = result_queue.get_nowait()
        if status == 'success':
            return True, data, None
        else:
            return False, None, f"{data}\n{err}"
    except queue.Empty:
        return False, None, "No result from process"


# ========== 7. Вспомогательные утилиты ==========

def get_environment_snapshot() -> Dict[str, Any]:
    """
    Создает снимок текущего состояния окружения.
    Полезно для сравнения до/после теста.
    """
    return {
        'modules': set(sys.modules.keys()),
        'random_state': random.getstate(),
        'env_vars': dict(os.environ),
        'gc_objects': len(gc.get_objects()),
    }


def compare_snapshots(before: Dict, after: Dict) -> Dict[str, Any]:
    """
    Сравнивает два снимка окружения и возвращает различия.
    """
    diff = {}
    
    # Новые модули
    new_modules = after['modules'] - before['modules']
    if new_modules:
        diff['new_modules'] = list(new_modules)
    
    # Изменения в переменных окружения
    env_diff = {}
    all_keys = set(before['env_vars']) | set(after['env_vars'])
    for key in all_keys:
        if before['env_vars'].get(key) != after['env_vars'].get(key):
            env_diff[key] = {
                'before': before['env_vars'].get(key),
                'after': after['env_vars'].get(key)
            }
    if env_diff:
        diff['env_changes'] = env_diff
    
    # Изменения в GC
    if before['gc_objects'] != after['gc_objects']:
        diff['gc_objects_diff'] = after['gc_objects'] - before['gc_objects']
    
    return diff


# Предопределенные сбросчики для общих компонентов
def register_common_resetters():
    """
    Регистрирует сбросчики для часто используемых компонентов.
    Вызывается при инициализации тестера.
    """
    # Пример для EventBus (будет добавлен позже)
    try:
        from client.src.core.event_bus import EventBus
        
        def reset_event_bus():
            if hasattr(EventBus, '_instance'):
                EventBus._instance = None
            logger.debug("Сброс EventBus")
        
        register_resetter(reset_event_bus)
    except ImportError:
        logger.debug("EventBus не найден, сбросчик не зарегистрирован")
    
    # Пример для логгера
    from utils.logger import logger as project_logger
    
    def reset_logger():
        if hasattr(project_logger, 'handlers'):
            # Очищаем обработчики, но оставляем базовые
            pass
    
    register_resetter(reset_logger)
    logger.info("Зарегистрированы стандартные сбросчики состояния")


# Инициализация при импорте
register_common_resetters()