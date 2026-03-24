"""
Точка входа в клиентское приложение Markoff 2.0.
Минимальная версия — только запуск, вся инициализация в bootstrap.
"""
import os
import sys

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
Logger.set_level(Logger.DEBUG)
Logger.enable_colors(True)

log = get_logger(__name__)


def setup_application() -> QApplication:
    """Создаёт и настраивает QApplication."""
    app = QApplication(sys.argv)
    app.setApplicationName("Markoff Client")
    app.setApplicationDisplayName("Markoff 2.0")
    app.setOrganizationName("Markoff")
    return app


def main() -> None:
    """Точка входа."""
    log.startup("Запуск Markoff 2.0")
    
    try:
        # Создаем QApplication
        app = setup_application()
        
        # Инициализируем все компоненты (Core, Data, Services, Controllers)
        bootstrap = ApplicationBootstrap(app)
        
        # Получаем главное окно
        window = bootstrap.get_window()
        window.show()
        
        log.success("Главное окно отображено")
        
        # Запускаем event loop
        exit_code = app.exec()
        
        # Очищаем ресурсы
        bootstrap.cleanup()
        
        log.shutdown(f"Приложение завершено с кодом {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        log.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()