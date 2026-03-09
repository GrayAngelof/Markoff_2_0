# utils/Tester/core/runner.py
"""
Модуль выполнения тестов с изоляцией и сбором статистики.
"""

import time
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Callable, Any, Tuple, Dict
import logging
import multiprocessing

from ..common.test_common import TestMarker
from .models import TestFunction

# Импортируем утилиты изоляции
from ..utils.isolation import (
    reset_environment, 
    set_deterministic_mode,
    capture_output,
    run_with_timeout,
    ShutdownHandler,
    TimeoutError,
    OutputCapture
)
from ..utils.helpers import format_duration, generate_test_id

logger = logging.getLogger(__name__)


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
    
    def get_failed_tests(self) -> List[TestResult]:
        return [r for r in self.results if not r.success]


def run_test_in_process(test: TestFunction, timeout: int, seed: int) -> Tuple[bool, str, str, str, str, float]:
    """
    Запускает тест в отдельном процессе с использованием утилит изоляции.
    """
    start_time = time.time()
    
    try:
        # Полная изоляция окружения
        reset_environment()
        set_deterministic_mode(seed)
        
        # Перехватываем вывод
        with capture_output() as (stdout, stderr):
            test()
        
        duration = time.time() - start_time
        return True, stdout.getvalue(), stderr.getvalue(), "", "", duration
        
    except AssertionError as e:
        duration = time.time() - start_time
        return False, "", "", str(e), traceback.format_exc(), duration
    except Exception as e:
        duration = time.time() - start_time
        return False, "", "", f"{type(e).__name__}: {e}", traceback.format_exc(), duration


class TestRunner:
    """
    Запускает тесты с использованием утилит изоляции.
    """
    
    def __init__(self, timeout: int = 10, fail_fast: bool = False):
        self.default_timeout = timeout
        self.fail_fast = fail_fast
        self._current_session: Optional[TestSession] = None
        self._seed = 42
        self._active_processes: List[multiprocessing.Process] = []
        
        # Инициализируем обработчик сигналов для graceful shutdown
        self._shutdown_handler = ShutdownHandler()
        self._shutdown_handler.register()
    
    def run_test(self, test: TestFunction) -> TestResult:
        """Запускает один тест в изолированном процессе."""
        
        # Проверяем, не получили ли сигнал остановки
        if self._shutdown_handler.should_stop:
            logger.warning("Пропуск теста из-за сигнала остановки")
            return TestResult(
                test=test,
                success=False,
                duration=0.0,
                output=TestOutput(),
                error="Test skipped due to shutdown signal"
            )
        
        logger.debug(f"Запуск теста: {test.full_name}")
        timeout = test.timeout if test.timeout is not None else self.default_timeout
        
        # Создаем процесс для теста
        ctx = multiprocessing.get_context('spawn')
        queue = ctx.Queue()
        
        def target():
            try:
                result = run_test_in_process(test, timeout, self._seed)
                queue.put(result)
            except Exception as e:
                queue.put((False, "", "", f"Process error: {e}", traceback.format_exc(), 0.0))
        
        process = ctx.Process(target=target)
        self._active_processes.append(process)
        start_time = time.time()
        process.start()
        
        # Ждем завершения с таймаутом
        process.join(timeout)
        
        success = False
        stdout = ""
        stderr = ""
        error_msg = None
        traceback_str = None
        duration = 0.0
        
        if process.is_alive():
            # Процесс все еще выполняется - убиваем
            logger.warning(f"Тест {test.name} превысил таймаут {timeout}с, убиваем процесс")
            process.terminate()
            process.join(2)
            
            if process.is_alive():
                process.kill()
                process.join()
            
            duration = time.time() - start_time
            error_msg = f"Timeout ({timeout}s)"
            success = False
            
        else:
            # Процесс завершился, получаем результат
            try:
                result = queue.get_nowait()
                success, stdout, stderr, error_msg, traceback_str, duration = result
            except Exception as e:
                duration = time.time() - start_time
                error_msg = f"Failed to get result: {e}"
                traceback_str = traceback.format_exc()
        
        # Очищаем процесс
        if process in self._active_processes:
            self._active_processes.remove(process)
        
        # Обработка ожидаемых падений
        if hasattr(test, 'expected_failure') and test.expected_failure:
            if not success:
                # Тест ожидаемо упал - считаем успехом
                success = True
                error_msg = f"[EXPECTED FAILURE] {error_msg}"
            elif success:
                # Тест ожидаемо падал, но прошел - это ошибка
                success = False
                error_msg = "Test was expected to fail but passed"
        
        return TestResult(
            test=test,
            success=success,
            duration=duration,
            output=TestOutput(stdout=stdout, stderr=stderr),
            error=error_msg,
            traceback=traceback_str
        )
    
    def run_tests(self, tests: List[TestFunction], session_name: str = "Test Session") -> TestSession:
        """Запускает группу тестов с поддержкой graceful shutdown."""
        
        # Проверяем флаг остановки перед началом
        if self._shutdown_handler.should_stop:
            logger.warning("Тестирование прервано пользователем")
            empty_session = TestSession(name=session_name)
            empty_session.finish()
            return empty_session
        
        logger.info(f"Запуск сессии '{session_name}' с {len(tests)} тестами")
        
        session = TestSession(name=session_name)
        self._current_session = session
        
        try:
            for i, test in enumerate(tests, 1):
                # Проверяем остановку перед каждым тестом
                if self._shutdown_handler.should_stop:
                    logger.warning("Получен сигнал остановки, завершаем сессию досрочно")
                    break
                
                logger.debug(f"Тест {i}/{len(tests)}: {test.name}")
                result = self.run_test(test)
                session.add_result(result)
                
                # Проверяем fail-fast
                if self.fail_fast and not result.success:
                    logger.info(f"Fail-fast: остановка после первого упавшего теста")
                    break
                    
        finally:
            session.finish()
            self._current_session = None
            self.cleanup()
        
        logger.info(f"Сессия завершена: {session.passed}/{session.total} passed")
        return session
    
    def run_selected(self, tests: List[TestFunction], markers: Optional[List[TestMarker]] = None) -> TestSession:
        """Запускает выбранные тесты с фильтрацией по маркерам."""
        if markers:
            filtered = [t for t in tests if any(m in t.markers for m in markers)]
            logger.info(f"Фильтрация по маркерам {markers}: {len(filtered)}/{len(tests)} тестов")
            tests = filtered
        
        if not tests:
            logger.warning("Нет тестов для запуска")
            empty_session = TestSession(name="Empty Session")
            empty_session.finish()
            return empty_session
        
        return self.run_tests(tests, f"Selected Tests ({len(tests)})")
    
    def abort(self):
        """Прерывает текущую сессию (вызывается из UI)"""
        logger.warning("Прерывание текущей сессии по запросу пользователя")
        self.cleanup()
    
    def cleanup(self):
        """Принудительно завершает все активные процессы"""
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
        """Деструктор для гарантированной очистки"""
        self.cleanup()
        self._shutdown_handler.restore()