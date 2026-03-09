# utils/Tester/__init__.py
"""
Markoff Test Runner - система тестирования для проекта Markoff.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь для импорта логгера
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from utils.logger import get_logger, Logger
from .core.models import TestFunction, TestNode
from .core.discovery import TestDiscovery
from .core.runner import TestRunner, TestResult, TestSession
from .core.executor import TestExecutor
from .ui.reporter import TestReporter, ReportConfig
from .ui.menu import TestMenu
from .utils.isolation import reset_environment, set_deterministic_mode
from .utils.helpers import get_version

# Настраиваем логгер для тестера
logger = get_logger(__name__)
logger.startup("🚀 Markoff Test Runner инициализирован")

__version__ = "1.1.0"
__all__ = [
    'TestFunction',
    'TestNode',
    'TestDiscovery',
    'TestRunner',
    'TestResult',
    'TestSession',
    'TestExecutor',
    'TestReporter',
    'ReportConfig',
    'TestMenu',
    'reset_environment',
    'set_deterministic_mode',
    'get_version',
    'get_logger',  # <-- Экспортируем для использования в других модулях
]