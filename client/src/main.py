# client/src/main.py
"""
Точка входа в клиентское приложение Markoff 2.0.

Минимальная версия — только запуск, вся инициализация в bootstrap.
"""

# ===== ИМПОРТЫ =====
import os
import sys

from PySide6.QtWidgets import QApplication

from src.bootstrap import ApplicationBootstrap
from utils.logger import Logger, get_logger


# ===== КОНСТАНТЫ =====
# Настройка Qt логирования (подавление шума от плагинов)
_QT_LOGGING_RULES = """
    qt.core.plugin.factoryloader.debug=false;
    qt.core.plugin.loader.debug=false;
    qt.core.library.debug=false;
    *.warning=true;
    *.critical=true;
"""

log = get_logger(__name__)


# ===== ФУНКЦИИ =====
def setup_application() -> QApplication:
    """Создаёт и настраивает QApplication."""
    app = QApplication(sys.argv)
    app.setApplicationName("Markoff Client")
    app.setApplicationDisplayName("Markoff 2.0")
    app.setOrganizationName("Markoff")

    log.success("QApplication создан и настроен")
    return app


def setup_logging() -> None:
    """Настраивает уровни логирования."""
    Logger.set_level(Logger.DEBUG)  # При разработке DEBUG, для релиза - INFO
    Logger.enable_colors(True)

    # Настраиваем уровни для категорий
    Logger.set_category_level("performance", Logger.INFO)   # Метрики производительности
    Logger.set_category_level("db", Logger.WARNING)        # Логи БД только предупреждения
    Logger.set_category_level("api", Logger.INFO)          # Логи API на INFO


def main() -> None:
    """Точка входа в приложение."""
    # Настройка окружения
    os.environ["QT_LOGGING_RULES"] = _QT_LOGGING_RULES

    # Настройка логирования
    setup_logging()

    log.startup("Запуск Markoff 2.0")
    log.debug(f"Версия Python: {sys.version}")
    log.debug(f"Путь к приложению: {os.path.dirname(os.path.abspath(__file__))}")

    try:
        with log.measure_time("создание QApplication", level=Logger.DEBUG):
            app = setup_application()

        with log.measure_time("полная инициализация приложения"):
            bootstrap = ApplicationBootstrap(app)

        window = bootstrap.get_window()
        window.show()

        log.success("Главное окно отображено")

        log.startup("Запуск главного цикла приложения")

        with log.measure_time("сессия работы приложения"):
            exit_code = app.exec()

        log.info("Очистка ресурсов приложения")
        bootstrap.cleanup()

        log.shutdown(f"Приложение завершено с кодом {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        log.exception(f"Критическая ошибка: {e}")
        log.error("Приложение завершено аварийно")
        sys.exit(1)


# ===== ТОЧКА ВХОДА =====
if __name__ == "__main__":
    main()