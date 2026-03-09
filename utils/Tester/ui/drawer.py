# utils/Tester/ui/drawer.py
"""
Отрисовка экрана меню.
"""

from typing import Optional, List
import sys

from ..core.models import TestNode
from ..core.executor import TestExecutor
from ..utils.helpers import get_terminal_size, format_duration


class Color:
    """ANSI цвета"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


class Icons:
    """Иконки для UI"""
    FOLDER = "📁"
    FILE = "📄"
    TEST = "🧪"
    SUCCESS = "✓"
    FAIL = "✗"
    ERROR = "⚠️"
    STATS = "📊"
    CLOCK = "⏱️"


class ScreenDrawer:
    """
    Отрисовка экрана меню.
    """
    
    def __init__(self, config):
        self.config = config
    
    def draw_error(self, message: str):
        """Рисует сообщение об ошибке"""
        width, _ = get_terminal_size()
        print(f"{Color.RED}⚠️ {message}{Color.RESET}")
        print(f"{Color.RED}{'─' * width}{Color.RESET}\n")
    
    def draw_header(self):
        """Рисует шапку"""
        width, _ = get_terminal_size()
        header = "🧪 MARKOFF TESTER v1.1"
        print(f"{Color.BOLD}{Color.CYAN}{header.center(width)}{Color.RESET}")
        print(f"{Color.BOLD}{Color.CYAN}{'═' * width}{Color.RESET}")
    
    def draw_path(self, path: str):
        """Рисует текущий путь"""
        width, _ = get_terminal_size()
        display_path = path or "tests"
        
        if len(display_path) > width - 20:
            display_path = "..." + display_path[-(width - 23):]
        
        print(f"\n📁 {Color.BOLD}{display_path}{Color.RESET}")
        print(f"{Color.DIM}{'─' * width}{Color.RESET}")
    
    def draw_navigation(self, nav_list, discovery, failed_files):
        """Рисует список навигации"""
        items = nav_list.current_page_items
        start_idx = nav_list.global_start_index  # <-- ИСПРАВЛЕНО: было start_index
        
        for i, node in enumerate(items, start_idx):
            icon = Icons.FOLDER if node.node_type == "directory" else Icons.FILE
            
            name = node.name
            if len(name) > self.config.max_name_length:
                name = name[:self.config.max_name_length-3] + "..."
            
            status = ""
            if node.node_type == "file":
                if node.path in discovery._module_cache:
                    tests = len(discovery._module_cache[node.path].tests)
                    status = f" {Color.GREEN}[{tests}]{Color.RESET}"
                elif node.path in failed_files:
                    status = f" {Color.RED}[❌]{Color.RESET}"
            
            print(f"  {Color.BOLD}{i:2d}{Color.RESET} - {icon} {name}{status}")
        
        if nav_list.total_pages > 1:
            range_str = nav_list.get_display_range()
            print(f"\n  {Color.DIM}[{range_str}] n:след p:пред{Color.RESET}")
        
        print()
    
    def draw_file_tests(self, tests_manager):
        """Рисует тесты в файле"""
        if not tests_manager or not tests_manager.tests_list:
            return
        
        print(f"\n  {Color.BOLD}📋 Тесты:{Color.RESET}")
        
        items = tests_manager.tests_list.current_page_items
        start_idx = tests_manager.tests_list.global_start_index  # <-- ИСПРАВЛЕНО
        
        for i, test in enumerate(items, start_idx):
            markers = ""
            if hasattr(test, 'markers') and test.markers:
                marker_list = list(test.markers)[:3]
                marker_str = " ".join(f"[{m.name if hasattr(m, 'name') else m}]" for m in marker_list)
                markers = f" {Color.DIM}{marker_str}{Color.RESET}"
            
            desc = ""
            if test.description:
                desc = f" {Color.DIM}- {test.description[:30]}...{Color.RESET}"
            
            print(f"    {Color.BOLD}{i:2d}{Color.RESET} - {test.name}{markers}{desc}")
        
        if tests_manager.tests_list.total_pages > 1:
            range_str = tests_manager.tests_list.get_display_range()
            print(f"\n    {Color.DIM}[{range_str}] n:след p:пред (тесты){Color.RESET}")
        
        print()
    
    def draw_control_panel(self, fail_fast: bool, timeout: int, log_level: str):
        """Рисует панель управления"""
        width, _ = get_terminal_size()
        
        ff_status = "✅" if fail_fast else "❌"
        
        controls = [
            f"q:выход  r:перезагрузить  h:помощь  c:очистить",
            f"f:fail-fast [{ff_status}]  t:таймаут [{timeout}s]  l:лог [{log_level}]",
            f"0:назад/все  n:след  p:пред"
        ]
        
        print(f"{Color.DIM}{'─' * width}{Color.RESET}")
        for line in controls:
            print(f"  {Color.DIM}{line}{Color.RESET}")
    
    def draw_last_session(self, session):
        """Рисует статистику последнего запуска"""
        if not session:
            return
        
        width, _ = get_terminal_size()
        bar_width = min(40, width - 20)
        
        print(f"\n  {Color.BOLD}📊 Последний запуск: {session.name}{Color.RESET}")
        
        if session.total > 0:
            passed_w = int((session.passed / session.total) * bar_width)
            failed_w = bar_width - passed_w
            bar = (f"{Color.GREEN}{'█' * passed_w}{Color.RESET}"
                   f"{Color.RED}{'█' * failed_w}{Color.RESET}")
        else:
            bar = f"{Color.DIM}{'█' * bar_width}{Color.RESET}"
        
        print(f"    {bar}  {session.passed}/{session.total}")
        print(f"    {Color.GREEN}✓ {session.passed}{Color.RESET} "
              f"{Color.RED}✗ {session.failed}{Color.RESET} "
              f"{Color.DIM}({format_duration(session.duration)}){Color.RESET}")
    
    def draw_prompt(self):
        """Рисует приглашение ввода"""
        print(f"\n{Color.BOLD}👉 Введите номер или команду:{Color.RESET} ", end='', flush=True)