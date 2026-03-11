# utils/Tester/core/runner.py
"""
Модуль выполнения тестов с изоляцией и сбором статистики.
"""

import time
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any, Tuple
import logging
import multiprocessing
import queue

from .models import TestFunction
from ..utils.isolation import reset_environment, set_deterministic_mode
from ..utils.helpers import format_duration

logger = logging.getLogger(__name__)


class TestTimeoutError(Exception):
    """Исключение при превышении таймаута теста"""
    pass


@dataclass
class TestOutput:
    """Раздельный вывод теста"""
    stdout: str = ""
    stderr: str = ""
    
    @property
    def has_output(self) -> bool:
        return bool(self.stdout) or bool(self.stderr)
    
    def __str__(self) -> str:
        if self.stderr:
            return f"{self.stdout}\n--- STDERR ---\n{self.stderr}"
        return self.stdout


@dataclass
class TestResult:
    """Результат выполнения одного теста"""
    test: TestFunction
    success: bool
    duration: float
    output: TestOutput
    error: Optional[str] = None
    traceback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def status_emoji(self) -> str:
        return "✅" if self.success else "❌"
    
    @property
    def status_text(self) -> str:
        return "PASSED" if self.success else "FAILED"
    
    @property
    def brief(self) -> str:
        return f"{self.status_emoji} {self.test.name} ({format_duration(self.duration)})"
    
    @property
    def error_type(self) -> str:
        if not self.error:
            return ""
        return self.error.split(':')[0] if ':' in self.error else self.error


@dataclass
class TestSession:
    """Сессия тестирования — группа результатов"""
    name: str
    results: List[TestResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    def add_result(self, result: TestResult):
        self.results.append(result)
    
    def finish(self):
        self.end_time = datetime.now()
    
    @property
    def duration(self) -> float:
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.success)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.success)
    
    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        return (self.passed / self.total) * 100
    
    @property
    def total_time(self) -> float:
        return sum(r.duration for r in self.results)
    
    def get_failed_tests(self) -> List[TestResult]:
        return [r for r in self.results if not r.success]


# Глобальная функция для запуска в отдельном процессе
def _run_test_in_process(test_func, test_module_path, test_name, queue):
    """
    Запускает тест в отдельном процессе.
    
    Args:
        test_func: Сама тестовая функция (callable)
        test_module_path: Путь к модулю для импорта
        test_name: Имя теста для отладки
        queue: Очередь для возврата результата
    """
    try:
        # Изоляция окружения
        reset_environment()
        set_deterministic_mode(42)
        
        # Перехватываем stdout/stderr
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        start_time = time.time()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                test_func()
            
            duration = time.time() - start_time
            queue.put(('success', stdout_capture.getvalue(), stderr_capture.getvalue(), duration))
            
        except AssertionError as e:
            duration = time.time() - start_time
            queue.put(('assertion', stdout_capture.getvalue(), stderr_capture.getvalue(), 
                      str(e), traceback.format_exc(), duration))
        except Exception as e:
            duration = time.time() - start_time
            queue.put(('error', stdout_capture.getvalue(), stderr_capture.getvalue(),
                      f"{type(e).__name__}: {e}", traceback.format_exc(), duration))
            
    except Exception as e:
        # Ошибка на уровне самого процесса
        queue.put(('process_error', '', '', f"Process error: {e}", traceback.format_exc(), 0.0))


class TestRunner:
    """
    Запускает тесты с использованием multiprocessing.
    """
    
    def __init__(self, timeout: int = 10, fail_fast: bool = False):
        self.default_timeout = timeout
        self.fail_fast = fail_fast
        self._active_processes: List[multiprocessing.Process] = []
    
    def run_test(self, test: TestFunction) -> TestResult:
        """
        Запускает один тест в изолированном процессе.
        """
        logger.debug(f"Запуск теста: {test.full_name}")
        
        timeout = test.timeout if test.timeout is not None else self.default_timeout
        
        # Создаем очередь для получения результата
        ctx = multiprocessing.get_context('spawn')
        queue = ctx.Queue()
        
        # Передаем саму функцию и её имя
        process = ctx.Process(
            target=_run_test_in_process,
            args=(test.func, test.module_path, test.name, queue)
        )
        
        self._active_processes.append(process)
        start_time = time.time()
        process.start()
        
        # Ждем завершения с таймаутом
        process.join(timeout)
        
        result = None
        if process.is_alive():
            # Процесс завис - убиваем
            logger.warning(f"Тест {test.name} превысил таймаут {timeout}с")
            process.terminate()
            process.join(2)
            
            if process.is_alive():
                process.kill()
                process.join()
            
            duration = time.time() - start_time
            result = TestResult(
                test=test,
                success=False,
                duration=duration,
                output=TestOutput(),
                error=f"Timeout after {timeout}s"
            )
        else:
            # Получаем результат из очереди
            try:
                data = queue.get_nowait()
                
                if data[0] == 'success':
                    _, stdout, stderr, duration = data
                    result = TestResult(
                        test=test,
                        success=True,
                        duration=duration,
                        output=TestOutput(stdout=stdout, stderr=stderr)
                    )
                elif data[0] == 'assertion':
                    _, stdout, stderr, error, tb, duration = data
                    result = TestResult(
                        test=test,
                        success=False,
                        duration=duration,
                        output=TestOutput(stdout=stdout, stderr=stderr),
                        error=error,
                        traceback=tb
                    )
                elif data[0] == 'error':
                    _, stdout, stderr, error, tb, duration = data
                    result = TestResult(
                        test=test,
                        success=False,
                        duration=duration,
                        output=TestOutput(stdout=stdout, stderr=stderr),
                        error=error,
                        traceback=tb
                    )
                else:  # process_error
                    _, stdout, stderr, error, tb, duration = data
                    result = TestResult(
                        test=test,
                        success=False,
                        duration=duration,
                        output=TestOutput(stdout=stdout, stderr=stderr),
                        error=error,
                        traceback=tb
                    )
                    
            except queue.Empty:
                duration = time.time() - start_time
                result = TestResult(
                    test=test,
                    success=False,
                    duration=duration,
                    output=TestOutput(),
                    error="No result from test process"
                )
        
        # Очищаем процесс
        if process in self._active_processes:
            self._active_processes.remove(process)
        
        # Обработка expected_failure
        if hasattr(test, 'expected_failure') and test.expected_failure:
            if not result.success:
                # Ожидаемо упал - считаем успехом
                result = TestResult(
                    test=test,
                    success=True,
                    duration=result.duration,
                    output=result.output,
                    error=f"[EXPECTED FAILURE] {result.error}" if result.error else None
                )
            elif result.success:
                # Ожидаемо падал, но прошел - ошибка
                result = TestResult(
                    test=test,
                    success=False,
                    duration=result.duration,
                    output=result.output,
                    error="Test was expected to fail but passed"
                )
        
        return result
    
    def run_tests(self, tests: List[TestFunction]) -> TestSession:
        """Запускает группу тестов"""
        session = TestSession(name="Test Run")
        
        for i, test in enumerate(tests, 1):
            result = self.run_test(test)
            session.add_result(result)
            
            if self.fail_fast and not result.success:
                logger.info("Fail-fast: остановка после первого упавшего теста")
                break
        
        session.finish()
        return session
    
    def cleanup(self):
        """Очищает все активные процессы"""
        for process in self._active_processes[:]:
            if process.is_alive():
                logger.warning(f"Принудительное завершение процесса {process.pid}")
                process.terminate()
                process.join(2)
                if process.is_alive():
                    process.kill()
                    process.join()
            self._active_processes.remove(process)
    
    def __del__(self):
        self.cleanup()