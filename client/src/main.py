# client/src/main.py
"""
Точка входа в клиентское приложение Markoff
Создаёт главное окно и запускает event loop
"""
import os
import sys
# Убираем информационные сообщения, но оставляем предупреждения и ошибки
os.environ["QT_LOGGING_RULES"] = """
    qt.core.plugin.factoryloader.debug=false;
    qt.core.plugin.loader.debug=false;
    qt.core.library.debug=false;
    *.warning=true;
    *.critical=true;
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.ui.main_window import MainWindow

def main():
    """
    Главная функция запуска приложения
    
    Шаги:
    1. Создаём QApplication (обязательно для любого Qt приложения)
    2. Настраиваем атрибуты приложения (если нужно)
    3. Создаём и показываем главное окно
    4. Запускаем event loop
    """

    # Создаём приложение
    app = QApplication(sys.argv)
    
    # Устанавливаем имя приложения (будет видно в заголовке окон)
    app.setApplicationName("Markoff Client")
    app.setOrganizationName("Markoff")
    
    # Создаём главное окно
    window = MainWindow()
    window.show()
    
    # Запускаем event loop и завершаем с кодом возврата
    sys.exit(app.exec())

if __name__ == "__main__":
    main()