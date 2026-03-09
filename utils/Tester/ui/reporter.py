# utils/Tester/ui/reporter.py (исправленная версия)
"""
Формирование отчетов о выполнении тестов с использованием утилит.
"""

from typing import List, Optional, Dict, Any, TextIO, Tuple
from datetime import datetime
import sys
import json
from dataclasses import dataclass

from ..core.runner import TestSession, TestResult, TestOutput

# Импортируем утилиты
from ..utils.helpers import (
    format_duration,
    format_timestamp,
    strip_ansi,
    truncate,
    get_terminal_size,
    print_table,
    group_by
)


class Color:
    """ANSI цвета для терминала"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    
    @classmethod
    def disable(cls):
        for attr in dir(cls):
            if attr.isupper() and isinstance(getattr(cls, attr), str):
                setattr(cls, attr, '')


class Icons:
    """Иконки для разных платформ"""
    ASCII = {
        'success': '[PASS]',
        'fail': '[FAIL]',
        'skip': '[SKIP]',
        'error': '[ERROR]',
        'folder': '[DIR]',
        'file': '[FILE]',
        'test': '[TEST]',
        'arrow': '->',
        'bullet': '*',
        'clock': 'Time:',
        'stats': 'Stats:',
    }
    
    UNICODE = {
        'success': '✓',
        'fail': '✗',
        'skip': '⚠',
        'error': '⚡',
        'folder': '📁',
        'file': '📄',
        'test': '🧪',
        'arrow': '→',
        'bullet': '•',
        'clock': '⏱️',
        'stats': '📊',
    }


@dataclass
class ReportConfig:
    """Конфигурация форматирования отчета"""
    show_output: bool = True
    show_traceback: bool = False
    color: bool = True
    use_emoji: bool = True
    max_output_lines: int = 50
    max_failures: int = 10
    width: Optional[int] = None
    verbose: bool = False  # Добавлено поле verbose


class TestReporter:
    """
    Формирует отчеты о выполнении тестов.
    """
    
    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        
        if self.config.width is None:
            self.config.width, _ = get_terminal_size()
        
        if self.config.color and not sys.stdout.isatty():
            Color.disable()
            self.config.color = False
        
        self.icons = Icons.UNICODE if self.config.use_emoji else Icons.ASCII
    
    def format_result(self, result: TestResult, indent: str = "") -> str:
        """Форматирует результат одного теста."""
        lines = []
        
        status_icon = self.icons['success'] if result.success else self.icons['fail']
        status_color = Color.GREEN if result.success else Color.RED
        
        time_str = format_duration(result.duration)
        
        title = (f"{indent}{status_icon} "
                f"{result.test.name} "
                f"({Color.DIM}{time_str}{Color.RESET})")
        lines.append(title)
        
        if result.test.description and self.config.show_output:
            lines.append(f"{indent}  {Color.DIM}{result.test.description}{Color.RESET}")
        
        if result.error:
            lines.append(f"{indent}  {Color.RED}╰─ {result.error}{Color.RESET}")
            
            if self.config.show_traceback and result.traceback:
                tb_lines = result.traceback.splitlines()[-5:]
                for line in tb_lines:
                    lines.append(f"{indent}     {Color.DIM}{line}{Color.RESET}")
        
        if self.config.show_output and result.output.has_output:
            self._format_output(result.output, lines, indent + "     ")
        
        return '\n'.join(lines)
    
    def _format_output(self, output: TestOutput, lines: List[str], indent: str):
        """Добавляет вывод теста в отчет."""
        lines.append(f"{indent}{Color.DIM}─── Output ───{Color.RESET}")
        
        # Разбиваем stdout и stderr на строки вручную
        stdout_lines = output.stdout.splitlines() if output.stdout else []
        stderr_lines = output.stderr.splitlines() if output.stderr else []
        
        all_lines = []
        for line in stdout_lines:
            all_lines.append(('stdout', line))
        for line in stderr_lines:
            all_lines.append(('stderr', line))
        
        # Обрезаем до максимального количества строк
        if len(all_lines) > self.config.max_output_lines:
            all_lines = all_lines[:self.config.max_output_lines]
            lines.append(f"{indent}{Color.DIM}... truncated ...{Color.RESET}")
        
        for stream, line in all_lines:
            if stream == 'stdout':
                lines.append(f"{indent}  {Color.BLUE}{line}{Color.RESET}")
            else:
                lines.append(f"{indent}  {Color.YELLOW}{line}{Color.RESET}")
    
    def format_session(self, session: TestSession, detailed: bool = True) -> str:
        """Форматирует полную сессию тестирования."""
        lines = []
        
        # Заголовок
        lines.extend(self._format_header(session))
        
        # Детали тестов
        if detailed:
            for result in session.results:
                lines.append(self.format_result(result))
                lines.append("")
        
        # Сводка
        lines.extend(self._format_summary(session))
        
        # Ошибки
        if session.failed > 0:
            lines.extend(self._format_errors(session))
        
        return '\n'.join(lines)
    
    def _format_header(self, session: TestSession) -> List[str]:
        """Форматирует заголовок."""
        return [
            f"{Color.BOLD}{'═' * self.config.width}{Color.RESET}",
            f"{Color.CYAN}{self.icons['stats']} TEST REPORT: {session.name}{Color.RESET}",
            f"{Color.BOLD}{'═' * self.config.width}{Color.RESET}",
            f"{Color.DIM}{format_timestamp(session.start_time)}{Color.RESET}",
            ""
        ]
    
    def _format_summary(self, session: TestSession) -> List[str]:
        """Форматирует сводку."""
        # Прогресс-бар
        bar_width = 40
        if session.total > 0:
            passed_width = int((session.passed / session.total) * bar_width)
            failed_width = bar_width - passed_width
            progress = (f"{Color.GREEN}{'█' * passed_width}{Color.RESET}"
                       f"{Color.RED}{'█' * failed_width}{Color.RESET}")
        else:
            progress = f"{Color.DIM}{'█' * bar_width}{Color.RESET}"
        
        # Общее время выполнения тестов (сумма всех тестов)
        total_exec_time = sum(r.duration for r in session.results)
        
        return [
            f"{Color.BOLD}{self.icons['stats']} SUMMARY{Color.RESET}",
            f"{Color.BOLD}{'─' * self.config.width}{Color.RESET}",
            f"",
            f"  {progress}  {session.passed}/{session.total}",
            f"",
            f"  {Color.GREEN}{self.icons['success']} Passed: {session.passed}{Color.RESET}",
            f"  {Color.RED}{self.icons['fail']} Failed: {session.failed}{Color.RESET}",
            f"  {Color.DIM}{self.icons['clock']} Session: {format_duration(session.duration)} (exec: {format_duration(total_exec_time)}){Color.RESET}",
            f"  {Color.DIM}📈 Rate: {self._colorize_rate(session.success_rate)}{Color.RESET}",
            f"",
            f"{Color.BOLD}{'═' * self.config.width}{Color.RESET}"
        ]
    
    def _format_errors(self, session: TestSession) -> List[str]:
        """Форматирует детали ошибок."""
        lines = [
            f"",
            f"{Color.BOLD}{Color.RED}{self.icons['error']} FAILED TESTS{Color.RESET}",
            f"{Color.BOLD}{'─' * self.config.width}{Color.RESET}",
            f""
        ]
        
        failed = session.get_failed_tests()
        for i, result in enumerate(failed[:self.config.max_failures], 1):
            lines.extend([
                f"{Color.RED}{i}. {result.test.full_name}{Color.RESET}",
                f"   {Color.DIM}Error: {Color.RESET}{result.error}"
            ])
            
            # Используем show_traceback, а не verbose
            if result.traceback and self.config.show_traceback:
                tb = result.traceback.splitlines()[-3:]
                for line in tb:
                    lines.append(f"   {Color.DIM}{line}{Color.RESET}")
            
            lines.append("")
        
        if len(failed) > self.config.max_failures:
            lines.append(f"   ... and {len(failed) - self.config.max_failures} more failures")
        
        # Группировка ошибок
        if failed:
            lines.append(f"{Color.YELLOW}📊 Error Summary:{Color.RESET}")
            error_groups = {}
            for r in failed:
                error_type = r.error_type or "Unknown"
                if error_type not in error_groups:
                    error_groups[error_type] = []
                error_groups[error_type].append(r)
            
            for error_type, results in error_groups.items():
                lines.append(f"  {Color.RED}{error_type}{Color.RESET}: {len(results)} tests")
        
        return lines
    
    def _colorize_rate(self, rate: float) -> str:
        """Цветной процент успеха."""
        rate_str = f"{rate:.1f}%"
        if rate == 100:
            return f"{Color.GREEN}{rate_str}{Color.RESET}"
        elif rate >= 80:
            return f"{Color.YELLOW}{rate_str}{Color.RESET}"
        else:
            return f"{Color.RED}{rate_str}{Color.RESET}"
    
    def to_text(self, session: TestSession, file: Optional[TextIO] = None) -> Optional[str]:
        """Экспорт в plain text."""
        # Сохраняем конфиг
        old_color = self.config.color
        old_emoji = self.config.use_emoji
        
        self.config.color = False
        self.config.use_emoji = False
        self.icons = Icons.ASCII
        
        report = self.format_session(session)
        
        # Восстанавливаем
        self.config.color = old_color
        self.config.use_emoji = old_emoji
        self.icons = Icons.UNICODE if old_emoji else Icons.ASCII
        
        if file:
            file.write(strip_ansi(report))
            file.write('\n')
            return None
        
        return strip_ansi(report)
    
    def to_json(self, session: TestSession) -> Dict[str, Any]:
        """Экспорт в JSON."""
        total_exec_time = sum(r.duration for r in session.results)
        
        return {
            'name': session.name,
            'start_time': session.start_time.isoformat(),
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'duration': session.duration,
            'total_exec_time': total_exec_time,  # Переименовано для ясности
            'summary': {
                'total': session.total,
                'passed': session.passed,
                'failed': session.failed,
                'success_rate': session.success_rate
            },
            'results': [
                {
                    'test': {
                        'name': r.test.name,
                        'full_name': r.test.full_name,
                        'module_path': r.test.module_path,
                        'description': r.test.description
                    },
                    'success': r.success,
                    'duration': r.duration,
                    'error': r.error,
                    'error_type': r.error_type,
                    'output': str(r.output) if r.output.has_output else None
                }
                for r in session.results
            ]
        }


# Утилита для прогресса в реальном времени
def print_progress(current: int, total: int, result: TestResult, reporter: TestReporter):
    """Печатает прогресс выполнения."""
    # Формируем краткую строку прогресса
    status_icon = reporter.icons['success'] if result.success else reporter.icons['fail']
    status_color = Color.GREEN if result.success else Color.RED
    
    line = (f"[{current}/{total}] "
            f"{status_color}{status_icon}{Color.RESET} "
            f"{result.test.name} "
            f"({Color.DIM}{format_duration(result.duration)}{Color.RESET})")
    
    if sys.stdout.isatty():
        sys.stdout.write('\r' + ' ' * reporter.config.width + '\r')
    
    sys.stdout.write(line)
    sys.stdout.flush()
    
    if not result.success:
        sys.stdout.write('\n')
        sys.stdout.write(f"  {Color.RED}→ {result.error}{Color.RESET}\n")
        sys.stdout.flush()


# Утилита для быстрой печати сводки
def print_summary(session: TestSession, reporter: Optional[TestReporter] = None):
    """Печатает только сводку (без деталей тестов)."""
    if reporter is None:
        reporter = TestReporter()
    
    # Временно отключаем детали
    old_show = reporter.config.show_output
    reporter.config.show_output = False
    
    print(reporter.format_session(session, detailed=False))
    
    # Восстанавливаем
    reporter.config.show_output = old_show