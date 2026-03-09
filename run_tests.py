#!/usr/bin/env python3
# run_tests.py
"""
Точка входа в тестер Markoff.
Поддерживает интерактивный режим и командную строку.
"""

import sys
import argparse
from pathlib import Path

# Добавляем корневую директорию в путь
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Импортируем логгер
from utils.logger import Logger, get_logger

# Импортируем компоненты тестера
from utils.Tester import TestMenu, get_version
from utils.Tester.ui.reporter import ReportConfig
from utils.Tester.core.executor import TestExecutor
from utils.Tester.core.discovery import TestDiscovery
from utils.Tester.core.runner import TestRunner
from utils.Tester.utils.isolation import ShutdownHandler
from utils.Tester.utils.helpers import clear_screen

# Создаем логгер для главного модуля
logger = get_logger(__name__)


def setup_logging(level: str = "INFO"):
    """
    Настраивает логирование через профессиональный логгер.
    
    Args:
        level: Уровень логирования (ERROR, WARNING, INFO, DEBUG)
    """
    levels = {
        'ERROR': Logger.ERROR,
        'WARNING': Logger.WARNING,
        'INFO': Logger.INFO,
        'DEBUG': Logger.DEBUG,
    }
    
    # Устанавливаем уровень
    Logger.set_level(levels.get(level.upper(), Logger.INFO))
    
    # Включаем цвета (если терминал поддерживает)
    Logger.enable_colors(sys.stdout.isatty())
    
    logger.startup(f"Логгер инициализирован, уровень: {level}")


def run_interactive(args):
    """
    Запускает интерактивный режим.
    
    Args:
        args: Аргументы командной строки
        
    Returns:
        int: Код возврата (0 - успех, 1 - ошибка)
    """
    tests_root = Path(args.tests).resolve()
    project_root = Path(args.project).resolve() if args.project else tests_root.parent
    
    if not tests_root.exists():
        logger.error(f"Директория не найдена: {tests_root}")
        print(f"❌ Директория не найдена: {tests_root}")
        return 1
    
    logger.info(f"Запуск интерактивного режима, тесты: {tests_root}")
    
    # Создаем и запускаем меню
    menu = TestMenu(tests_root, project_root)
    
    # Настройка UI
    if args.no_color:
        menu.reporter.config.color = False
        logger.debug("Цвета отключены")
    if args.no_emoji:
        menu.reporter.config.use_emoji = False
        logger.debug("Эмодзи отключены")
    if args.page_size:
        menu.config.page_size = args.page_size
        logger.debug(f"Размер страницы: {args.page_size}")
    
    try:
        menu.run()
    except KeyboardInterrupt:
        logger.info("Завершение по Ctrl+C")
        print("\n\n👋 До свидания!")
    except Exception as e:
        # Убираем exc_info=True
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    logger.success("Интерактивный режим завершен")
    return 0


def run_headless(args):
    """
    Запускает тесты без UI (для CI/CD).
    
    Args:
        args: Аргументы командной строки
        
    Returns:
        int: Код возврата (0 - все тесты пройдены, 1 - есть ошибки)
    """
    tests_root = Path(args.tests).resolve()
    project_root = Path(args.project).resolve() if args.project else tests_root.parent
    
    if not tests_root.exists():
        logger.error(f"Директория не найдена: {tests_root}")
        print(f"❌ Директория не найдена: {tests_root}")
        return 1
    
    logger.info(f"Запуск headless режима, тесты: {tests_root}")
    
    # Инициализация компонентов
    discovery = TestDiscovery(tests_root, project_root)
    runner = TestRunner(timeout=args.timeout, fail_fast=args.fail_fast)
    shutdown = ShutdownHandler()
    shutdown.register()
    
    # Настройка репортера (без цветов для логов)
    from utils.Tester.ui.reporter import TestReporter
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    executor = TestExecutor(runner, shutdown)
    
    # Загрузка тестов
    logger.info(f"Сканирование {tests_root}")
    print(f"🔍 Сканирование {tests_root}...")
    root = discovery.scan()
    
    # Получаем все тесты
    all_tests = root.get_all_tests()
    logger.info(f"Найдено {len(all_tests)} тестов")
    
    # Фильтрация по маркерам или паттерну
    if args.marker:
        filtered = [t for t in all_tests if hasattr(t, 'markers') and args.marker in t.markers]
        logger.info(f"Фильтр по маркеру '{args.marker}': {len(filtered)}/{len(all_tests)} тестов")
        print(f"📌 Фильтр по маркеру '{args.marker}': {len(filtered)}/{len(all_tests)} тестов")
        tests_to_run = filtered
    elif args.pattern:
        import fnmatch
        filtered = [t for t in all_tests if fnmatch.fnmatch(t.full_name, args.pattern)]
        logger.info(f"Фильтр по паттерну '{args.pattern}': {len(filtered)}/{len(all_tests)} тестов")
        print(f"📌 Фильтр по паттерну '{args.pattern}': {len(filtered)}/{len(all_tests)} тестов")
        tests_to_run = filtered
    else:
        tests_to_run = all_tests
    
    if not tests_to_run:
        logger.warning("Нет тестов для запуска")
        print("❌ Нет тестов для запуска")
        shutdown.restore()
        return 1
    
    # Запуск
    logger.info(f"Запуск {len(tests_to_run)} тестов")
    print(f"🚀 Запуск {len(tests_to_run)} тестов...\n")
    session = executor.run_selected(tests_to_run, name="Headless Run")
    
    if not session:
        logger.error("Ошибка выполнения тестов")
        print("❌ Ошибка выполнения")
        shutdown.restore()
        return 1
    
    # Вывод результатов
    logger.info(f"Тестирование завершено: пройдено {session.passed}, провалено {session.failed}")
    print("\n" + "="*60)
    print(f"ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60)
    print(f"Всего: {session.total}")
    print(f"✅ Пройдено: {session.passed}")
    print(f"❌ Провалено: {session.failed}")
    print(f"⏱️  Время: {session.duration:.2f}с")
    print(f"📊 Успешность: {session.success_rate:.1f}%")
    
    # Детали ошибок для CI
    if session.failed > 0 and args.verbose:
        print("\n❌ Детали ошибок:")
        for r in session.get_failed_tests():
            print(f"\n  {r.test.full_name}")
            print(f"  {r.error}")
            if r.traceback and args.debug:
                print(f"  {r.traceback}")
    
    shutdown.restore()
    logger.success(f"Headless режим завершен, код возврата: {0 if session.failed == 0 else 1}")
    return 0 if session.failed == 0 else 1


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description=f"🧪 Markoff Test Runner v{get_version()}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Интерактивный режим
  python run_tests.py
  
  # Запуск всех тестов (headless)
  python run_tests.py --headless
  
  # Запуск с фильтром по маркеру
  python run_tests.py --headless --marker smoke
  
  # Запуск конкретного теста
  python run_tests.py --headless --pattern "*test_basic*"
  
  # С таймаутом и fail-fast
  python run_tests.py --headless --timeout 5 --fail-fast
"""
    )
    
    # Основные параметры
    parser.add_argument('--tests', type=str, default='tests',
                       help='Путь к директории с тестами (по умолчанию: tests)')
    parser.add_argument('--project', type=str, default='.',
                       help='Корень проекта (по умолчанию: родитель tests)')
    
    # Режимы запуска
    parser.add_argument('--headless', action='store_true',
                       help='Запуск без UI (для CI/CD)')
    
    # Параметры для headless режима
    parser.add_argument('--marker', type=str,
                       help='Запустить только тесты с указанным маркером')
    parser.add_argument('--pattern', type=str,
                       help='Запустить тесты, соответствующие паттерну (fnmatch)')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Таймаут для тестов в секундах (по умолчанию: 10)')
    parser.add_argument('--fail-fast', action='store_true',
                       help='Остановиться при первой ошибке')
    
    # Параметры для интерактивного режима
    parser.add_argument('--no-color', action='store_true',
                       help='Отключить цвета (интерактивный режим)')
    parser.add_argument('--no-emoji', action='store_true',
                       help='Отключить эмодзи (интерактивный режим)')
    parser.add_argument('--page-size', type=int, default=10,
                       help='Количество элементов на странице (интерактивный режим)')
    
    # Общие параметры
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
                       help='Уровень логирования (по умолчанию: INFO)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод (для headless режима)')
    parser.add_argument('--debug', action='store_true',
                       help='Режим отладки (показывает traceback)')
    
    args = parser.parse_args()
    
    # Настройка логирования
    setup_logging(args.log_level)
    
    # Логируем параметры запуска
    logger.debug(f"Параметры запуска: {args}")
    
    # Выбор режима
    if args.headless:
        logger.info("Выбран headless режим")
        return run_headless(args)
    else:
        logger.info("Выбран интерактивный режим")
        return run_interactive(args)


if __name__ == "__main__":
    sys.exit(main())