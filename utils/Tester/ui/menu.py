# utils/Tester/ui/menu.py
"""
Интерактивное меню - координатор интерфейса.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional
from types import SimpleNamespace

from ..core.discovery import TestDiscovery
from ..core.runner import TestRunner
from ..core.executor import TestExecutor, ProgressInfo
from ..ui.reporter import TestReporter, ReportConfig, print_progress
from ..ui.drawer import ScreenDrawer
from ..ui.commands import CommandHandler
from ..ui.navigation import NavigationStack, PaginatedList, FileTestsManager
from ..utils.isolation import ShutdownHandler
from ..utils.helpers import get_input_line, clear_screen

from utils.logger import Logger, get_logger 

logger = get_logger(__name__)


class TestMenu:
    """
    Координатор интерфейса.
    Связывает executor и reporter.
    """
    
    def __init__(self, tests_root: Path, project_root: Optional[Path] = None):
        self.tests_root = tests_root
        self.project_root = project_root or tests_root.parent
        self.config = SimpleNamespace(page_size=10, max_name_length=50)
        
        # Инициализация компонентов
        self._init_components()
        
        # Сканирование тестов
        self.root_node = self.discovery.scan()
        
        # Навигация
        self.nav_stack = NavigationStack(self.root_node)
        self.tests_manager = FileTestsManager(self.discovery)
        self._update_navigation_list()
        
        # Настройка callback'а для прогресса
        self.executor.set_progress_callback(self._on_progress)
        
        self.running = True
    
    def _init_components(self):
        """Инициализация всех компонентов"""
        self.discovery = TestDiscovery(self.tests_root, self.project_root)
        self.runner = TestRunner(timeout=10, fail_fast=False)
        self.shutdown = ShutdownHandler()
        self.shutdown.register()
        
        # executor НЕ принимает reporter (только runner и shutdown)
        self.executor = TestExecutor(self.runner, self.shutdown)
        
        # reporter используем только в UI
        self.reporter = TestReporter(ReportConfig(color=True, use_emoji=True))
        
        # drawer
        self.drawer = ScreenDrawer(self.config)
    
    def _update_navigation_list(self):
        """Обновляет список навигации"""
        current = self.nav_stack.current
        self.nav_list = PaginatedList(list(current.children), self.config.page_size)
    
    def _on_progress(self, info: ProgressInfo):
        """
        Callback для отображения прогресса.
        Здесь UI встречается с executor'ом.
        """
        print_progress(info.current, info.total, info.result, self.reporter)
    
    def _handle_navigation(self, index: int):
        """
        Обработка навигации.
        index=0 - назад
        index>0 - переход к узлу
        """
        if index == 0:
            # Назад
            if self.nav_stack.can_go_back():
                self.nav_stack.pop()
                self.tests_manager.clear()
                self._update_navigation_list()
            else:
                # Уже в корне - ничего не делаем
                logger.debug("Уже в корне, назад нельзя")
        else:
            # Переход к дочернему узлу
            node = self.nav_list.get_by_global_index(index)
            if node:
                if node.node_type == "file":
                    # Открываем файл с тестами
                    result = self.tests_manager.load_file(node)
                    if result and result.error_message:
                        logger.warning(result.error_message)
                
                # Переходим в директорию (или файл)
                self.nav_stack.push(node)
                self._update_navigation_list()
    
    def _run_all_tests(self):
        """Запускает все тесты в текущей папке"""
        print("\n🔍 ОТЛАДКА: _run_all_tests вызван")  # <-- временно
        
        current_node = self.nav_stack.current
        print(f"🔍 Текущий узел: {current_node.name}")  # <-- временно
        
        tests = current_node.get_all_tests()
        print(f"🔍 Найдено тестов: {len(tests)}")  # <-- временно
        
        if not tests:
            print(f"\n\033[33mВ папке '{current_node.name}' нет тестов\033[0m")
            input("\nНажмите Enter для продолжения...")
            return
        
        print(f"\n\033[33mЗапуск {len(tests)} тестов в '{current_node.name}'...\033[0m")
        
        # Запускаем тесты
        session = self.executor.run_all(tests)
        
        if session:
            print("\n")
            print(self.reporter.format_session(session))
            self.executor.last_session = session
            input("\nНажмите Enter для продолжения...")
    
    def _run_single_test(self, test):
        """Запускает один тест"""
        print(f"\n\033[33mЗапуск теста: {test.name}\033[0m")
        
        session = self.executor.run_single(test)
        
        if session and session.results:
            result = session.results[0]
            print("\n" + self.reporter.format_result(result))
            
            if not result.success and result.traceback:
                print(f"\n\033[33mДетали ошибки:\033[0m")
                print(f"\033[90m{result.traceback}\033[0m")
            
            print(f"\n\033[33mНажмите Enter для продолжения...\033[0m")
            input()
    
    def _reload(self):
        """Перезагрузка тестов"""
        self.discovery.reload()
        self.root_node = self.discovery.scan()
        self.nav_stack.reset()
        self.tests_manager.clear()
        self._update_navigation_list()
    
    def _get_log_level_char(self) -> str:
        """Возвращает символ уровня лога"""
        level = Logger.get_level()  # <-- используем класс Logger для статического метода
        for ch, lvl in CommandHandler.LOG_LEVELS.items():
            if lvl == level:
                return ch
        return 'i'
    
    def _setup_command_handler(self):
        """Создает обработчик команд"""
        self.cmd = CommandHandler(
            discovery=self.discovery,
            executor=self.executor,
            nav_list=self.nav_list,
            tests_manager=self.tests_manager,
            on_exit=lambda: self.running,
            on_reload=self._reload,
            on_navigate=self._handle_navigation,
            on_run_all=self._run_all_tests,
            on_run_test=self._run_single_test
        )
    
    def draw(self):
        """Отрисовка экрана"""
        clear_screen()
        
        current = self.nav_stack.current
        path = self.nav_stack.get_path_string()
        
        self.drawer.draw_header()
        self.drawer.draw_path(path)
        self.drawer.draw_navigation(
            self.nav_list,
            self.discovery,
            self.discovery.get_failed_files()
        )
        
        if self.tests_manager.has_file:
            self.drawer.draw_file_tests(self.tests_manager)
        
        log_level = self._get_log_level_char()
        self.drawer.draw_control_panel(
            self.runner.fail_fast,
            self.runner.default_timeout,
            log_level
        )
        
        if self.executor.last_session:
            self.drawer.draw_last_session(self.executor.last_session)
        
        self.drawer.draw_prompt()
    
    def run(self):
        """Основной цикл"""
        self._setup_command_handler()
        
        try:
            while self.running:
                self.draw()
                
                # Получаем ввод
                key = get_input_line()
                
                # Обрабатываем команду
                self.running = self.cmd.handle(key)
                
        except KeyboardInterrupt:
            print("\n\n\033[33mПрерывание...\033[0m")
        finally:
            self.shutdown.restore()
            self.runner.cleanup()
            print(f"\033[0m")