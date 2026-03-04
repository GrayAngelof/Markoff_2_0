# client/src/ui/main_window.py
"""
Главное окно приложения Markoff
Содержит разделение на левую панель (дерево) и правую панель (информация)
Поддерживает три уровня обновления данных:
- Текущий узел (F5)
- Все раскрытые узлы (Ctrl+F5)
- Полная перезагрузка (Ctrl+Shift+F5)
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, 
    QSplitter, QToolBar, QStatusBar, QMessageBox,
    QMenu, QPushButton, QApplication, QLabel  # Добавлен QLabel
)
from PySide6.QtCore import Qt, Slot, QSize, QTimer
from PySide6.QtGui import QAction, QKeySequence

from src.ui.tree_view import TreeView
from src.ui.details_panel import DetailsPanel
from src.ui.refresh_menu import RefreshMenu


class MainWindow(QMainWindow):
    """
    Главное окно приложения
    
    Компоновка:
    - Используем QSplitter для разделения на две части
    - Левая часть: дерево объектов (TreeView)
    - Правая часть: информационная панель (DetailsPanel)
    
    Панель инструментов:
    - Кнопка с меню для выбора типа обновления
    - Индикатор статуса подключения
    - Счётчик загруженных объектов (опционально)
    
    Горячие клавиши:
    - F5: обновить текущий узел
    - Ctrl+F5: обновить все раскрытые узлы
    - Ctrl+Shift+F5: полная перезагрузка
    """
    
    def __init__(self):
        """Инициализация главного окна"""
        super().__init__()
        
        # Настраиваем окно
        self.setWindowTitle("Markoff - Управление помещениями")
        self.setMinimumSize(1000, 700)  # Чуть больше для комфорта
        
        # Создаём центральный виджет и layout
        self._setup_central_widget()
        
        # Создаём компоненты
        self._create_components()
        
        # Настраиваем панель инструментов
        self._create_toolbar()
        
        # Создаём строку статуса
        self._create_statusbar()
        
        # Настраиваем горячие клавиши
        self._setup_shortcuts()
        
        # Подключаем сигналы
        self._connect_signals()
        
        # Таймер для обновления статуса (периодическая проверка соединения)
        self._setup_status_timer()
        
        print("✅ MainWindow: создано")
    
    def _setup_central_widget(self):
        """Настройка центрального виджета с разделителем"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной горизонтальный layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Создаём разделитель
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(5)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #c0c0c0;
            }
            QSplitter::handle:hover {
                background-color: #808080;
            }
        """)
        
        layout.addWidget(self.splitter)
    
    def _create_components(self):
        """Создание основных компонентов"""
        # Левая панель с деревом
        self.tree_view = TreeView()
        
        # Правая панель с информацией
        self.details_panel = DetailsPanel()
        
        # Добавляем в разделитель
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.details_panel)
        
        # Устанавливаем начальные размеры (30% - дерево, 70% - информация)
        self.splitter.setSizes([300, 700])
    
    def _create_toolbar(self):
        """Создание панели инструментов с меню обновления"""
        toolbar = QToolBar("Панель инструментов")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Создаём меню обновления
        self.refresh_menu = RefreshMenu(self)
        
        # Кнопка с выпадающим меню
        refresh_button = QPushButton("🔄 Обновить")
        refresh_button.setMenu(self.refresh_menu)
        refresh_button.setToolTip("Выберите тип обновления (F5 - меню)")
        toolbar.addWidget(refresh_button)
        
        # Разделитель
        toolbar.addSeparator()
        
        # Индикатор статуса
        self.status_action = QAction("⚪ Проверка...", self)
        self.status_action.setEnabled(False)
        toolbar.addAction(self.status_action)
        
        # Счётчик объектов (будет обновляться)
        self.counter_action = QAction("📊 Объектов: -", self)
        self.counter_action.setEnabled(False)
        toolbar.addAction(self.counter_action)
    
    def _create_statusbar(self):
        """Создание строки статуса"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        
        # Добавляем постоянные индикаторы
        self.connection_label = QLabel("⚪ Соединение...")
        self.status_bar.addPermanentWidget(self.connection_label)
    
    def _setup_shortcuts(self):
        """Настройка горячих клавиш"""
        # F5 - обновить текущий узел
        refresh_current = QAction(self)
        refresh_current.setShortcut(QKeySequence.Refresh)  # F5
        refresh_current.triggered.connect(self._on_refresh_current)
        self.addAction(refresh_current)
        
        # Ctrl+F5 - обновить все раскрытые
        refresh_visible = QAction(self)
        refresh_visible.setShortcut(Qt.CTRL | Qt.Key_F5)
        refresh_visible.triggered.connect(self._on_refresh_visible)
        self.addAction(refresh_visible)
        
        # Ctrl+Shift+F5 - полная перезагрузка
        full_reset = QAction(self)
        full_reset.setShortcut(Qt.CTRL | Qt.SHIFT | Qt.Key_F5)
        full_reset.triggered.connect(self._on_full_reset)
        self.addAction(full_reset)
    
    def _connect_signals(self):
        """Подключение сигналов"""
        # Сигналы от дерева
        self.tree_view.item_selected.connect(self.details_panel.show_item_details)
        self.tree_view.data_loading.connect(self._on_data_loading)
        self.tree_view.data_loaded.connect(self._on_data_loaded)
        self.tree_view.data_error.connect(self._on_data_error)
        
        # Сигналы от меню обновления
        self.refresh_menu.refresh_current.connect(self._on_refresh_current)
        self.refresh_menu.refresh_visible.connect(self._on_refresh_visible)
        self.refresh_menu.full_reset.connect(self._on_full_reset)
    
    def _setup_status_timer(self):
        """Настройка таймера для периодической проверки статуса"""
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._check_connection_status)
        self.status_timer.start(30000)  # Проверка каждые 30 секунд
        
        # Первая проверка через 1 секунду
        QTimer.singleShot(1000, self._check_connection_status)
    
    # ===== Слоты для обновления =====
    
    @Slot()
    def _on_refresh_current(self):
        """Обновить текущий выбранный узел"""
        selected = self.tree_view.get_selected_node_info()
        if selected:
            node_type, node_id, _ = selected
            self.status_bar.showMessage(f"🔄 Обновление {node_type} #{node_id}...")
            self.tree_view.refresh_current()
        else:
            self.status_bar.showMessage("⚠️ Нет выбранного узла для обновления", 3000)
    
    @Slot()
    def _on_refresh_visible(self):
        """Обновить все раскрытые узлы"""
        self.status_bar.showMessage("🔄 Обновление всех раскрытых узлов...")
        self.tree_view.refresh_visible()
    
    @Slot()
    def _on_full_reset(self):
        """Полная перезагрузка"""
        # Спрашиваем подтверждение
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите выполнить полную перезагрузку?\n"
            "Все несохранённые данные будут потеряны.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.status_bar.showMessage("🔄 Полная перезагрузка...")
            self.tree_view.full_reset()
            self.details_panel.clear()
            self.status_bar.showMessage("✅ Полная перезагрузка выполнена", 3000)
    
    # ===== Слоты для отслеживания загрузки =====
    
    @Slot(str, int)
    def _on_data_loading(self, node_type: str, node_id: int):
        """Начало загрузки данных"""
        self.status_bar.showMessage(f"📡 Загрузка {node_type} #{node_id}...")
        # Можно добавить индикатор в статус-бар
    
    @Slot(str, int)
    def _on_data_loaded(self, node_type: str, node_id: int):
        """Завершение загрузки данных"""
        self.status_bar.showMessage(f"✅ Загружен {node_type} #{node_id}", 2000)
        self._update_object_counter()
    
    @Slot(str, int, str)
    def _on_data_error(self, node_type: str, node_id: int, error: str):
        """Ошибка загрузки данных"""
        self.status_bar.showMessage(f"❌ Ошибка загрузки {node_type} #{node_id}", 5000)
        # Можно показать более детальное сообщение
        QMessageBox.warning(
            self,
            "Ошибка загрузки",
            f"Не удалось загрузить {node_type} #{node_id}:\n{error}"
        )
    
    # ===== Вспомогательные методы =====
    
    def _check_connection_status(self):
        """Проверка статуса соединения с сервером"""
        try:
            # Используем silent=True, чтобы не засорять логи
            is_connected = self.tree_view.api_client.check_connection(silent=True)
            
            if is_connected:
                self.status_action.setText("✅ Онлайн")
                self.status_action.setIconText("✅")
                self.connection_label.setText("✅ Сервер доступен")
                self.connection_label.setStyleSheet("color: green;")
            else:
                self._set_offline_status()
        except Exception as e:
            # Даже при ошибке не выводим в логи, только меняем статус
            self._set_offline_status()
    
    def _set_offline_status(self):
        """Установка статуса офлайн"""
        self.status_action.setText("❌ Офлайн")
        self.status_action.setIconText("❌")
        self.connection_label.setText("❌ Сервер недоступен")
        self.connection_label.setStyleSheet("color: red;")
    
    def _update_object_counter(self):
        """Обновление счётчика объектов в тулбаре"""
        # Получаем статистику из кэша
        if hasattr(self.tree_view, 'cache'):
            stats = self.tree_view.cache.get_stats()
            self.counter_action.setText(f"📊 В кэше: {stats['size']} объектов")
    
    # ===== Публичные методы =====
    
    def closeEvent(self, event):
        """
        Обработчик закрытия окна
        Очищаем ресурсы
        """
        print("👋 Завершение работы...")
        
        # Останавливаем таймер
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        
        # Очищаем кэш (он сам очистится, но для порядка)
        if hasattr(self.tree_view, 'cache'):
            self.tree_view.cache.clear()
        
        # Принимаем событие закрытия
        event.accept()
        print("✅ Приложение завершено")


# Для тестирования окна отдельно
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()