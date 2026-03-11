# utils/Tester/ui/commands.py
"""
Обработка команд пользователя в интерактивном меню.
Поддерживает навигацию, запуск тестов, настройки и управление логгером.
"""

import sys
from typing import Optional, Callable

from utils.logger import Logger, get_logger
from ..core.executor import TestExecutor
from ..core.discovery import TestDiscovery
from ..core.models import TestFunction
from .navigation import PaginatedList, FileTestsManager

# Создаем логгер для этого модуля
logger = get_logger(__name__)


class CommandHandler:
    """
    Обработчик команд меню.
    
    Поддерживает:
    - Навигация (числа, 0, n, p)
    - Управление тестами (запуск, перезагрузка)
    - Настройки (fail-fast, таймаут, уровень лога)
    - Системные команды (выход, помощь, статистика)
    """
    
    # Маппинг клавиш на уровни логирования (E W I D)
    LOG_LEVELS = {
        'e': Logger.ERROR,      # Только ошибки
        'w': Logger.WARNING,    # Ошибки и предупреждения
        'i': Logger.INFO,       # Основная информация (по умолчанию)
        'd': Logger.DEBUG,      # Всё, включая отладку
    }
    
    # Названия уровней для отображения
    LEVEL_NAMES = {
        Logger.ERROR: 'ERROR',
        Logger.WARNING: 'WARNING',
        Logger.INFO: 'INFO',
        Logger.DEBUG: 'DEBUG',
    }
    
    def __init__(self, 
                 discovery: TestDiscovery,
                 executor: TestExecutor,
                 nav_list: PaginatedList,
                 tests_manager: FileTestsManager,
                 on_exit: Callable[[], bool],
                 on_reload: Callable[[], None],
                 on_navigate: Callable[[int], None],
                 on_run_all: Callable[[], None],      # <-- НОВЫЙ
                 on_run_test: Callable[[TestFunction], None]):
        """
        Инициализирует обработчик команд.
        
        Args:
            discovery: Обнаружитель тестов
            executor: Исполнитель тестов
            nav_list: Пагинированный список для навигации
            tests_manager: Менеджер тестов текущего файла
            on_exit: Callback при выходе (возвращает bool: продолжать ли)
            on_reload: Callback при перезагрузке
            on_navigate: Callback при навигации (принимает индекс)
            on_run_test: Callback при запуске теста
        """
        self.discovery = discovery
        self.executor = executor
        self.nav_list = nav_list
        self.tests_manager = tests_manager
        self.on_exit = on_exit
        self.on_reload = on_reload
        self.on_navigate = on_navigate
        self.on_run_all = on_run_all
        self.on_run_test = on_run_test
        
        # Текущие настройки (синхронизируются с executor.runner)
        self.fail_fast = executor.runner.fail_fast
        self.timeout = executor.runner.default_timeout
        self.log_level = Logger.get_level()
        
        logger.debug("CommandHandler инициализирован")
    
    def handle(self, key: str) -> bool:
        """
        Обрабатывает команду пользователя.
        
        Args:
            key: Введенная строка (может быть пустой)
            
        Returns:
            bool: True для продолжения работы, False для выхода
        """
        if not key:
            return True
        
        key = key.strip().lower()
        logger.debug(f"Получена команда: '{key}'")
        
        # Системные команды (односимвольные)
        if len(key) == 1:
            if key == 'q':
                return self._handle_exit()
            elif key == 'r':
                self._handle_reload()
            elif key == 'h':
                self._handle_help()
            elif key == 'c':
                self._handle_clear()
            elif key == 'f':
                self._handle_toggle_fail_fast()
            elif key == 't':
                self._handle_change_timeout()
            elif key in self.LOG_LEVELS:
                self._handle_change_log_level(key)
            elif key == 's':
                self._handle_statistics()
            elif key == 'n':
                self._handle_next_page()
            elif key == 'p':
                self._handle_prev_page()
            elif key == 'b':  # <-- НОВАЯ КОМАНДА
                self._handle_back()
            elif key == '0':
                self._handle_run_all()  # <-- ТЕПЕРЬ ТОЛЬКО ЗАПУСК
            elif key.isdigit():
                # Однозначное число (1-9)
                self._handle_number(int(key))
            else:
                logger.debug(f"Неизвестная команда: {key}")
        
        # Многозначные числа (10, 11, 42...)
        elif key.isdigit():
            self._handle_number(int(key))
        
        else:
            logger.debug(f"Неизвестная команда: {key}")
        
        return True
    
    # ========== Системные команды ==========
    
    def _handle_exit(self) -> bool:
        """Обрабатывает выход из программы"""
        print("\n\033[33mВыйти? (y/N): \033[0m", end='', flush=True)
        confirm = sys.stdin.readline().strip().lower()
        
        if confirm == 'y':
            logger.info("Завершение работы по запросу пользователя")
            return False  # Завершаем цикл
        
        logger.debug("Выход отменен")
        return True  # Продолжаем работу
    
    def _handle_reload(self):
        """Перезагрузка дерева тестов"""
        print("\n\033[33mПерезагрузка дерева тестов...\033[0m")
        logger.info("Перезагрузка по запросу пользователя")
        self.on_reload()
        print("\033[32m✓ Перезагрузка завершена\033[0m")
    
    def _handle_help(self):
        """Показывает справку по командам"""
        from .drawer import Color
        
        logger.info("Показ справки")
        
        print(f"\n{Color.BOLD}{Color.CYAN}📚 ПОМОЩЬ ПО КОМАНДАМ{Color.RESET}")
        print(f"{Color.CYAN}════════════════════════{Color.RESET}\n")
        
        print(f"{Color.BOLD}Навигация:{Color.RESET}")
        print("  Числа       - перейти в директорию / открыть файл / запустить тест")
        print("  b           - назад на уровень выше")
        print("  0           - запустить все тесты в текущей папке")
        print("  n / p       - следующая/предыдущая страница")
        
        print(f"\n{Color.BOLD}Управление тестами:{Color.RESET}")
        print("  r           - перезагрузить дерево тестов")
        print("  s           - показать статистику")
        
        print(f"\n{Color.BOLD}Настройки:{Color.RESET}")
        print("  f           - переключить fail-fast")
        print("  t           - изменить таймаут")
        print("  e/w/i/d     - уровень логирования")
        
        print(f"\n{Color.BOLD}Системные:{Color.RESET}")
        print("  q           - выход")
        print("  c           - очистить экран")
        print("  h           - эта справка")
        
        print(f"\n{Color.BOLD}{Color.GREEN}Нажмите Enter для продолжения...{Color.RESET}")
        input()
    
    def _handle_clear(self):
        """Очистка экрана"""
        from ..utils.helpers import clear_screen
        logger.debug("Очистка экрана")
        clear_screen()
    
    # ========== Настройки ==========
    
    def _handle_toggle_fail_fast(self):
        """Переключение режима fail-fast"""
        self.fail_fast = not self.fail_fast
        self.executor.runner.fail_fast = self.fail_fast
        
        status = "включен" if self.fail_fast else "выключен"
        print(f"\n\033[33mFail-fast {status}\033[0m")
        logger.info(f"Fail-fast {status}")
    
    def _handle_change_timeout(self):
        """Изменение таймаута выполнения тестов"""
        print(f"\n\033[33mТекущий таймаут: {self.timeout}с\033[0m")
        print("Новый таймаут (сек): ", end='', flush=True)
        
        try:
            new_timeout = int(sys.stdin.readline().strip())
            if new_timeout > 0:
                self.timeout = new_timeout
                self.executor.runner.default_timeout = new_timeout
                print(f"\033[32m✓ Таймаут установлен: {new_timeout}с\033[0m")
                logger.info(f"Таймаут изменен на {new_timeout}с")
            else:
                print("\033[31mОшибка: таймаут должен быть положительным числом\033[0m")
                logger.warning(f"Попытка установить неверный таймаут: {new_timeout}")
        except ValueError:
            print("\033[31mОшибка: введите число\033[0m")
            logger.warning("Неверный формат таймаута")
    
    def _handle_change_log_level(self, key: str):
        """Изменение уровня логирования"""
        level = self.LOG_LEVELS.get(key)
        if level:
            self.log_level = level
            Logger.set_level(level)
            
            level_name = self.LEVEL_NAMES.get(level, 'UNKNOWN')
            print(f"\n\033[33mУровень логирования: {level_name} ({key})\033[0m")
            logger.info(f"Уровень логирования изменен на {level_name}")
            
            # Небольшая пауза, чтобы пользователь увидел сообщение
            import time
            time.sleep(0.5)
    
    # ========== Навигация по страницам ==========
    
    def _handle_next_page(self):
        """Переход на следующую страницу"""
        # Сначала пробуем в тестах текущего файла
        if self.tests_manager and self.tests_manager.has_tests:
            if self.tests_manager.next_page():
                logger.debug("Следующая страница тестов")
                return
        
        # Затем в навигации по папкам
        if self.nav_list and self.nav_list.next_page():
            logger.debug("Следующая страница навигации")
            return
        
        print("\n\033[33mНет следующей страницы\033[0m")
        logger.debug("Попытка перехода на несуществующую страницу")
    
    def _handle_prev_page(self):
        """Переход на предыдущую страницу"""
        # Сначала пробуем в тестах текущего файла
        if self.tests_manager and self.tests_manager.has_tests:
            if self.tests_manager.prev_page():
                logger.debug("Предыдущая страница тестов")
                return
        
        # Затем в навигации по папкам
        if self.nav_list and self.nav_list.prev_page():
            logger.debug("Предыдущая страница навигации")
            return
        
        print("\n\033[33mНет предыдущей страницы\033[0m")
        logger.debug("Попытка перехода на несуществующую страницу")

    def _handle_back(self):
        """Возврат на уровень выше"""
        logger.debug("Команда b: назад")
        self.on_navigate(0)  # Используем тот же callback с 0 для навигации
    
    # ========== Числовые команды ==========
    
    def _handle_run_all(self):
        """Запуск всех тестов в текущей папке"""
        logger.debug("Команда 0: запустить все тесты")
        
        # Проверяем, есть ли тесты в текущем узле
        current_node = self.nav_list  # но нам нужен текущий узел из menu
        
        # Вызываем callback из menu
        self.on_run_all()
    
    def _handle_number(self, num: int):
        """Обрабатывает числовую команду"""
        if num == 0:
            self._handle_zero()
            return
        
        logger.debug(f"Числовая команда: {num}")
        
        # Сначала ищем в тестах текущего файла
        if self.tests_manager and self.tests_manager.has_tests:
            test = self.tests_manager.get_test_by_global_index(num)
            if test:
                logger.info(f"Запуск теста по индексу {num}: {test.name}")
                self._handle_run_test(test)
                return
        
        # Затем в навигации по папкам
        if self.nav_list:
            node = self.nav_list.get_by_global_index(num)
            if node:
                logger.info(f"Навигация по индексу {num}: {node.name}")
                self.on_navigate(num)
                return
        
        # Элемент не найден
        print(f"\n\033[31mЭлемент с номером {num} не найден\033[0m")
        logger.warning(f"Элемент с индексом {num} не найден")
    
    # ========== Запуск тестов ==========
    
    def _handle_run_test(self, test: TestFunction):
        """Запускает указанный тест"""
        logger.info(f"Запуск теста: {test.full_name}")
        self.on_run_test(test)
    
    # ========== Статистика ==========
    
    def _handle_statistics(self):
        """Показывает подробную статистику по тестам"""
        logger.info("Запрос статистики")
        
        stats = self.discovery.get_statistics()
        
        print(f"\n\033[1;36m📊 СТАТИСТИКА ТЕСТОВ\033[0m")
        print(f"\033[1;36m══════════════════\033[0m\n")
        
        print(f"📁 Всего файлов с тестами: {stats['total_files']}")
        print(f"📂 Загружено файлов: {stats['loaded_files']}")
        print(f"❌ Файлов с ошибками: {stats['failed_files']}")
        print(f"🧪 Всего тестов: {stats['total_tests']}")
        print(f"💾 Модулей в кэше: {stats['cached_modules']}")
        
        # Показываем проблемные файлы, если есть
        if stats.get('failed_files_list'):
            print(f"\n\033[31m⚠️  Проблемные файлы:\033[0m")
            for i, file_path in enumerate(stats['failed_files_list'][:5], 1):
                print(f"  {i}. {file_path.name}")
            
            if len(stats['failed_files_list']) > 5:
                print(f"  ... и еще {len(stats['failed_files_list']) - 5}")
        
        # Показываем последнюю сессию, если есть
        if self.executor.last_session:
            session = self.executor.last_session
            print(f"\n\033[1;36m📋 Последний запуск: {session.name}\033[0m")
            print(f"  ✓ Пройдено: {session.passed}")
            print(f"  ✗ Провалено: {session.failed}")
            print(f"  ⏱️  Время: {session.duration:.2f}с")
            print(f"  📊 Успешность: {session.success_rate:.1f}%")
        
        print(f"\n\033[90mУровень логирования: {self.LEVEL_NAMES.get(self.log_level, 'INFO')}\033[0m")
        print(f"\033[90mFail-fast: {'включен' if self.fail_fast else 'выключен'}\033[0m")
        print(f"\033[90mТаймаут: {self.timeout}с\033[0m")
        
        print(f"\n\033[1;32mНажмите Enter для продолжения...\033[0m")
        input()
    
    # ========== Свойства для доступа из меню ==========
    
    @property
    def current_log_level_char(self) -> str:
        """Возвращает символ текущего уровня логирования"""
        for ch, lvl in self.LOG_LEVELS.items():
            if lvl == self.log_level:
                return ch
        return 'i'
    
    @property
    def current_log_level_name(self) -> str:
        """Возвращает название текущего уровня логирования"""
        return self.LEVEL_NAMES.get(self.log_level, 'INFO')