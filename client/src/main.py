# client/src/main.py
"""
Точка входа в клиентское приложение Markoff 2.0.
Минимальная версия — только запуск, вся инициализация в bootstrap.
"""
import os
import sys
import traceback

from PySide6.QtWidgets import QApplication

from src.bootstrap import ApplicationBootstrap
from utils.logger import get_logger, Logger


# Настройка окружения
os.environ["QT_LOGGING_RULES"] = """
    qt.core.plugin.factoryloader.debug=false;
    qt.core.plugin.loader.debug=false;
    qt.core.library.debug=false;
    *.warning=true;
    *.critical=true;
"""

# Настройка логирования
Logger.set_level(Logger.DEBUG)  # При разработке DEBUG, для релиза - INFO
Logger.enable_colors(True)

# Настраиваем уровни для категорий
Logger.set_category_level("performance", Logger.INFO)  # Включаем метрики производительности
Logger.set_category_level("db", Logger.WARNING)       # Логи БД только предупреждения и выше
Logger.set_category_level("api", Logger.INFO)         # Логи API на INFO

log = get_logger(__name__)


def setup_application() -> QApplication:
    """Создаёт и настраивает QApplication."""
    app = QApplication(sys.argv)
    app.setApplicationName("Markoff Client")
    app.setApplicationDisplayName("Markoff 2.0")
    app.setOrganizationName("Markoff")
    
    log.system("QApplication создан и настроен")
    return app


def main() -> None:
    """Точка входа."""
    log.startup("Запуск Markoff 2.0")
    log.debug(f"Версия Python: {sys.version}")
    log.debug(f"Путь к приложению: {os.path.dirname(os.path.abspath(__file__))}")
    
    try:
        # Создаем QApplication
        with log.measure_time("создание QApplication", level=Logger.DEBUG):
            app = setup_application()
        
        # Инициализируем все компоненты (Core, Data, Services, Controllers)
        with log.measure_time("полная инициализация приложения"):
            bootstrap = ApplicationBootstrap(app)
        
        # Получаем главное окно
        window = bootstrap.get_window()
        window.show()
        
        log.system("Главное окно отображено")
        
        # Запускаем event loop
        log.info("Запуск главного цикла приложения")
        
        with log.measure_time("сессия работы приложения"):
            exit_code = app.exec()
        
        # Очищаем ресурсы
        log.info("Очистка ресурсов приложения")
        bootstrap.cleanup()
        
        log.shutdown(f"Приложение завершено с кодом {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        log.exception(f"Критическая ошибка: {e}")
        log.error("Приложение завершено аварийно")
        sys.exit(1)


if __name__ == "__main__":
    main()