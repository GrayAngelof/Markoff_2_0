# utils/Tester/core/executor.py
"""
Логика запуска тестов с обработкой ошибок.
"""

import logging
import traceback
from typing import List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .models import TestFunction
from .runner import TestRunner, TestSession, TestResult, TestOutput
from ..utils.isolation import ShutdownHandler

logger = logging.getLogger(__name__)


@dataclass
class ProgressInfo:
    """Информация о прогрессе для callback'а"""
    current: int
    total: int
    result: TestResult
    session: TestSession


class TestExecutor:
    """
    Исполнитель тестов.
    Не зависит от UI, только возвращает данные.
    """
    
    def __init__(self, runner: TestRunner, shutdown: ShutdownHandler):
        self.runner = runner
        self.shutdown = shutdown
        self.last_session: Optional[TestSession] = None
        self._progress_callback: Optional[Callable[[ProgressInfo], None]] = None
    
    def set_progress_callback(self, callback: Optional[Callable[[ProgressInfo], None]]):
        """Устанавливает callback для отображения прогресса"""
        self._progress_callback = callback
    
    def _run_loop(self, tests: List[TestFunction], session_name: str) -> Optional[TestSession]:
        """
        Универсальный метод для запуска любого списка тестов.
        
        Returns:
            Optional[TestSession]: Сессия с результатами
        """
        if not tests:
            logger.warning("Нет тестов для запуска")
            return None
        
        session = TestSession(name=session_name)
        
        for i, test in enumerate(tests, 1):
            if self.shutdown.should_stop:
                logger.warning("Тестирование прервано пользователем")
                break
            
            try:
                result = self.runner.run_test(test)
            except Exception as e:
                logger.error(f"Критическая ошибка при запуске {test.name}: {e}")
                result = TestResult(
                    test=test,
                    success=False,
                    duration=0.0,
                    output=TestOutput(),
                    error=f"Executor error: {e}",
                    traceback=traceback.format_exc()
                )
            
            session.add_result(result)
            
            # Вызываем callback, если он есть
            if self._progress_callback:
                self._progress_callback(ProgressInfo(
                    current=i,
                    total=len(tests),
                    result=result,
                    session=session
                ))
            
            if self.runner.fail_fast and not result.success:
                logger.info("Fail-fast: остановка после первого упавшего теста")
                break
        
        session.finish()
        self.last_session = session
        return session
    
    def run_all(self, tests: List[TestFunction]) -> Optional[TestSession]:
        """Запускает все тесты"""
        return self._run_loop(tests, "All Tests")
    
    def run_single(self, test: TestFunction) -> Optional[TestSession]:
        """Запускает один тест"""
        return self._run_loop([test], f"Single: {test.name}")
    
    def run_selected(self, tests: List[TestFunction], name: str = "Selected") -> Optional[TestSession]:
        """Запускает выбранные тесты"""
        return self._run_loop(tests, name)