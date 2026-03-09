#!/usr/bin/env python3
# run_tests.py
"""
Точка входа в тестер Markoff.
Поддерживает интерактивный режим и командную строку.
"""

import sys
import argparse
import logging
from pathlib import Path

# Добавляем корневую директорию в путь
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from utils.Tester import TestMenu, get_version
from utils.Tester.ui.reporter import ReportConfig
from utils.Tester.core.executor import TestExecutor
from utils.Tester.core.discovery import TestDiscovery
from utils.Tester.core.runner import TestRunner
from utils.Tester.utils.isolation import ShutdownHandler
from utils.Tester.utils.helpers import clear_screen


def setup_logging(level: str = "INFO"):
    """Настраивает логирование"""
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
    }
    
    logging.basicConfig(
        level=levels.get(level.upper(), logging.INFO),
        format='%(levelname)s: %(message)s'
    )


def run_interactive(args):
    """Запускает интерактивный режим"""
    tests_root = Path(args.tests).resolve()
    project_root = Path(args.project).resolve() if args.project else tests_root.parent
    
    if not tests_root.exists():
        print(f"❌ Директория не найдена: {tests_root}")
        return 1
    
    # Создаем и запускаем меню
    menu = TestMenu(tests_root, project_root)
    
    # Настройка UI
    if args.no_color:
        menu.reporter.config.color = False
    if args.no_emoji:
        menu.reporter.config.use_emoji = False
    if args.page_size:
        menu.config.page_size = args.page_size
    
    try:
        menu.run()
    except KeyboardInterrupt:
        print("\n\n👋 До свидания!")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


def run_headless(args):
    """Запускает тесты без UI (для CI/CD)"""
    tests_root = Path(args.tests).resolve()
    project_root = Path(args.project).resolve() if args.project else tests_root.parent
    
    if not tests_root.exists():
        print(f"❌ Директория не найдена: {tests_root}")
        return 1
    
    # Инициализация компонентов
    discovery = TestDiscovery(tests_root, project_root)
    runner = TestRunner(timeout=args.timeout, fail_fast=args.fail_fast)
    shutdown = ShutdownHandler()
    shutdown.register()
    
    # Настройка репортера (без цветов для логов)
    from utils.Tester.ui.reporter import TestReporter
    reporter = TestReporter(ReportConfig(color=False, use_emoji=False))
    
    executor = TestExecutor(runner, reporter, shutdown)
    
    # Загрузка тестов
    print(f"🔍 Сканирование {tests_root}...")
    root = discovery.scan()
    
    # Фильтрация по маркерам или паттерну
    all_tests = root.get_all_tests()
    
    if args.marker:
        filtered = [t for t in all_tests if hasattr(t, 'markers') and args.marker in t.markers]
        print(f"📌 Фильтр по маркеру '{args.marker}': {len(filtered)}/{len(all_tests)} тестов")
        tests_to_run = filtered
    elif args.pattern:
        import fnmatch
        filtered = [t for t in all_tests if fnmatch.fnmatch(t.full_name, args.pattern)]
        print(f"📌 Фильтр по паттерну '{args.pattern}': {len(filtered)}/{len(all_tests)} тестов")
        tests_to_run = filtered
    else:
        tests_to_run = all_tests
    
    if not tests_to_run:
        print("❌ Нет тестов для запуска")
        return 1
    
    # Запуск
    print(f"🚀 Запуск {len(tests_to_run)} тестов...\n")
    session = executor.run_selected(tests_to_run, name="Headless Run")
    
    if not session:
        print("❌ Ошибка выполнения")
        return 1
    
    # Вывод результатов
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
    
    shutdown.restore()
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
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Уровень логирования')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    parser.add_argument('--debug', action='store_true',
                       help='Режим отладки (показывает traceback)')
    
    args = parser.parse_args()
    
    # Настройка логирования
    setup_logging(args.log_level)
    
    # Выбор режима
    if args.headless:
        return run_headless(args)
    else:
        return run_interactive(args)


if __name__ == "__main__":
    sys.exit(main())