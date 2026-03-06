# client/src/main.py
"""
Точка входа в клиентское приложение Markoff.
Создаёт главное окно, настраивает окружение и запускает event loop.
"""
import os
import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.utils.logger import get_logger, Logger


# Создаём логгер для этого модуля
log = get_logger(__name__)


# ===== Настройка окружения =====
# Убираем информационные сообщения Qt, оставляем предупреждения и ошибки
os.environ["QT_LOGGING_RULES"] = """
    qt.core.plugin.factoryloader.debug=false;
    qt.core.plugin.loader.debug=false;
    qt.core.library.debug=false;
    *.warning=true;
    *.critical=true;
"""

# Настройка логирования (уровень DEBUG для разработки)
Logger.set_level(Logger.DEBUG)
Logger.enable_colors(True)


def setup_application() -> QApplication:
    """
    Создаёт и настраивает экземпляр QApplication.
    
    Returns:
        QApplication: Настроенное приложение
    """
    app = QApplication(sys.argv)
    
    # Устанавливаем мета-информацию приложения
    app.setApplicationName("Markoff Client")
    app.setApplicationDisplayName("Markoff - Управление помещениями")
    app.setOrganizationName("Markoff")
    app.setOrganizationDomain("markoff.local")
    
    log.debug("QApplication создано и настроено")
    return app


def main() -> None:
    """
    Главная функция запуска приложения.
    
    Последовательность действий:
    1. Настройка окружения (QT_LOGGING_RULES)
    2. Создание QApplication
    3. Создание и отображение главного окна
    4. Запуск event loop
    """
    log.startup("Запуск приложения Markoff")
    
    try:
        # Создаём приложение
        app = setup_application()
        
        # Создаём и показываем главное окно
        window = MainWindow()
        window.show()
        
        log.success("Главное окно отображено")
        
        # Запускаем event loop
        exit_code = app.exec()
        
        log.shutdown(f"Приложение завершено с кодом {exit_code}")
        sys.exit(exit_code)
        
    except Exception as error:
        log.error(f"Критическая ошибка при запуске: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()