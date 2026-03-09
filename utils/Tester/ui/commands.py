# utils/Tester/ui/commands.py
"""
Обработка команд пользователя.
"""

import sys
import logging
from typing import Optional, Callable

from .navigation import PaginatedList
from ..core.executor import TestExecutor
from ..core.discovery import TestDiscovery
from ..core.models import TestFunction


class CommandHandler:
    """
    Обработчик команд меню.
    """
    
    LOG_LEVELS = {
        'e': logging.ERROR,
        'w': logging.WARNING,
        'i': logging.INFO,
        'd': logging.DEBUG
    }
    
    def __init__(self, 
                 discovery: TestDiscovery,
                 executor: TestExecutor,
                 nav_list: PaginatedList,
                 tests_manager,
                 on_exit: Callable,
                 on_reload: Callable,
                 on_navigate: Callable,
                 on_run_test: Callable):  # <-- Добавляем callback для запуска теста
        
        self.discovery = discovery
        self.executor = executor
        self.nav_list = nav_list
        self.tests_manager = tests_manager
        self.on_exit = on_exit
        self.on_reload = on_reload
        self.on_navigate = on_navigate
        self.on_run_test = on_run_test  # <-- Сохраняем
        
        self.fail_fast = False
        self.timeout = 10
        self.log_level = logging.INFO
    
    def handle(self, key: str) -> bool:
        """
        Обрабатывает команду.
        Returns: True для продолжения, False для выхода
        """
        if not key:
            return True
        
        key = key.strip().lower()
        
        # Системные команды
        if key == 'q':
            return self._exit()
        elif key == 'r':
            self._reload()
        elif key == 'h':
            self._help()
        elif key == 'c':
            pass  # очистка экрана
        elif key == 'f':
            self._toggle_fail_fast()
        elif key == 't':
            self._change_timeout()
        elif key in self.LOG_LEVELS:
            self._change_log_level(key)
        elif key == 's':
            self._statistics()
        elif key == 'n':
            self._next_page()
        elif key == 'p':
            self._prev_page()
        elif key == '0':
            self._handle_zero()
        elif key.isdigit():
            self._handle_number(int(key))
        
        return True
    
    def _exit(self) -> bool:
        """Выход из программы"""
        print("\n\033[33mВыйти? (y/N): \033[0m", end='', flush=True)
        confirm = sys.stdin.readline().strip().lower()
        return confirm != 'y'
    
    def _reload(self):
        """Перезагрузка тестов"""
        print("\n\033[33mПерезагрузка...\033[0m")
        self.on_reload()
        print("\033[32mГотово\033[0m")
    
    def _help(self):
        """Справка"""
        from .drawer import Color
        print(f"\n{Color.BOLD}{Color.CYAN}📚 ПОМОЩЬ{Color.RESET}")
        print(f"{Color.CYAN}════════{Color.RESET}\n")
        
        help_text = """
Навигация:
  Числа       - перейти в директорию / открыть файл / запустить тест
  0           - назад / запустить все тесты
  n / p       - следующая/предыдущая страница

Команды:
  q           - выход
  r           - перезагрузить
  f           - fail-fast (вкл/выкл)
  t           - изменить таймаут
  l (e/w/i/d) - уровень лога
  s           - статистика
  c           - очистить экран
  h           - эта справка
"""
        print(help_text)
        input("\nНажмите Enter...")
    
    def _toggle_fail_fast(self):
        """Переключение fail-fast"""
        self.fail_fast = not self.fail_fast
        self.executor.runner.fail_fast = self.fail_fast  # <-- Обновляем в runner
        status = "включен" if self.fail_fast else "выключен"
        print(f"\n\033[33mFail-fast {status}\033[0m")
    
    def _change_timeout(self):
        """Изменение таймаута"""
        print(f"\n\033[33mТекущий таймаут: {self.timeout}с\033[0m")
        print("Новый таймаут (сек): ", end='', flush=True)
        
        try:
            new = int(sys.stdin.readline().strip())
            if new > 0:
                self.timeout = new
                self.executor.runner.default_timeout = new  # <-- Обновляем в runner
                print(f"\033[32mТаймаут: {new}с\033[0m")
            else:
                print("\033[31mТаймаут > 0\033[0m")
        except ValueError:
            print("\033[31mНеверное значение\033[0m")
    
    def _change_log_level(self, key: str):
        """Изменение уровня лога"""
        level = self.LOG_LEVELS[key]
        self.log_level = level
        logging.getLogger().setLevel(level)
        print(f"\n\033[33mУровень лога: {key}\033[0m")
    
    def _statistics(self):
        """Показ статистики"""
        stats = self.discovery.get_statistics()
        
        print(f"\n\033[1;36m📊 СТАТИСТИКА\033[0m")
        print(f"\033[1;36m═══════════\033[0m\n")
        
        print(f"Всего файлов: {stats['total_files']}")
        print(f"Загружено: {stats['loaded_files']}")
        print(f"Ошибок: {stats['failed_files']}")
        print(f"Всего тестов: {stats['total_tests']}")
        
        if stats.get('failed_files_list'):
            print(f"\n\033[31mПроблемные файлы:\033[0m")
            for f in stats['failed_files_list'][:5]:
                print(f"  ❌ {f.name}")
        
        input("\nНажмите Enter...")
    
    def _next_page(self):
        """Следующая страница"""
        if self.tests_manager and self.tests_manager.next_page():
            return
        if self.nav_list and self.nav_list.next_page():
            return
        print("\n\033[33mНет следующей страницы\033[0m")
    
    def _prev_page(self):
        """Предыдущая страница"""
        if self.tests_manager and self.tests_manager.prev_page():
            return
        if self.nav_list and self.nav_list.prev_page():
            return
        print("\n\033[33mНет предыдущей страницы\033[0m")
    
    def _handle_zero(self):
        """Команда 0"""
        self.on_navigate(0)
    
    def _handle_number(self, num: int):
        """Числовая команда"""
        if num == 0:
            self._handle_zero()
            return
        
        # Сначала ищем в тестах
        if self.tests_manager and self.tests_manager.has_tests:
            # Используем правильный метод получения теста
            test = self.tests_manager.get_test_by_global_index(num)  # <-- ИСПРАВЛЕНО
            if test:
                self._run_test(test)
                return
        
        # Потом в навигации
        if self.nav_list:
            node = self.nav_list.get_by_global_index(num)  # <-- ИСПРАВЛЕНО
            if node:
                self.on_navigate(num)
                return
        
        print(f"\n\033[31mЭлемент {num} не найден\033[0m")
    
    def _run_test(self, test: TestFunction):
        """Запуск теста"""
        # Вызываем callback из menu.py
        self.on_run_test(test)