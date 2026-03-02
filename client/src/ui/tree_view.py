# client/src/ui/tree_view.py
"""
Компонент дерева объектов
Отображает иерархию: Комплексы → Корпуса → Этажи → Помещения
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QLabel,
    QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, Signal, Slot
from PySide6.QtGui import QFont, QColor, QBrush
from typing import List, Optional

from src.core.api_client import ApiClient
from src.models.complex import Complex

class ComplexTreeModel(QAbstractItemModel):
    """
    Модель данных для дерева комплексов
    
    Реализует интерфейс QAbstractItemModel для отображения
    иерархических данных в QTreeView
    
    Пока поддерживает только корневые элементы (комплексы)
    В будущем расширим для поддержки вложенных узлов
    """
    
    # Кастомные роли для данных
    ItemIdRole = Qt.UserRole + 1  # Для хранения ID объекта
    ItemTypeRole = Qt.UserRole + 2  # Тип объекта (complex/building/etc)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.complexes: List[Complex] = []  # Список комплексов
        self._items = []  # Внутреннее представление для дерева
    
    def set_complexes(self, complexes: List[Complex]):
        """
        Устанавливает список комплексов и обновляет модель
        
        Args:
            complexes: список комплексов для отображения
        """
        self.beginResetModel()  # Начинаем сброс модели
        self.complexes = complexes
        self._items = complexes  # Пока просто храним как список
        self.endResetModel()  # Заканчиваем сброс (вызовет обновление view)
    
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """
        Создаёт индекс для элемента по строке и колонке
        
        Args:
            row: строка (позиция среди siblings)
            column: колонка (в дереве обычно одна колонка)
            parent: родительский индекс
            
        Returns:
            QModelIndex: индекс элемента или пустой индекс
        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        if not parent.isValid():
            # Корневой уровень - комплексы
            if 0 <= row < len(self.complexes):
                return self.createIndex(row, column, self.complexes[row])
        
        return QModelIndex()
    
    def parent(self, index: QModelIndex) -> QModelIndex:
        """
        Возвращает родительский индекс для данного индекса
        
        У комплексов нет родителей (корневой уровень)
        """
        return QModelIndex()  # Все элементы пока на корневом уровне
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Возвращает количество строк (дочерних элементов) для родителя
        
        Args:
            parent: родительский индекс
            
        Returns:
            int: количество дочерних элементов
        """
        if not parent.isValid():
            # Корневой уровень - считаем комплексы
            return len(self.complexes)
        
        # У комплексов пока нет дочерних элементов
        return 0
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """В дереве всегда одна колонка"""
        return 1
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """
        Возвращает данные для отображения
        
        Args:
            index: индекс элемента
            role: роль данных (DisplayRole, UserRole, etc.)
            
        Returns:
            Данные для указанной роли
        """
        if not index.isValid():
            return None
        
        # Получаем объект комплекса из индекса
        item = index.internalPointer()
        if not isinstance(item, Complex):
            return None
        
        if role == Qt.DisplayRole:
            # Что показываем в дереве - название комплекса
            return item.name
            
        elif role == Qt.FontRole:
            # Шрифт (можно сделать жирным для комплексов)
            font = QFont()
            font.setBold(True)
            return font
            
        elif role == Qt.ForegroundRole:
            # Цвет текста
            return QBrush(QColor(0, 0, 0))  # Чёрный
            
        elif role == self.ItemIdRole:
            # ID объекта для идентификации
            return item.id
            
        elif role == self.ItemTypeRole:
            # Тип объекта
            return "complex"
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        """Заголовок для колонки"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return "Объекты"
        return None

class TreeView(QWidget):
    """
    Виджет дерева объектов
    
    Сигналы:
        item_selected: испускается при выборе элемента в дереве
    """
    
    # Сигнал о выборе элемента (передаём тип и ID)
    item_selected = Signal(str, int)  # type, id
    
    def __init__(self):
        """Инициализация виджета дерева"""
        super().__init__()
        
        # Создаём layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаём заголовок с индикатором загрузки
        self.title_layout = QVBoxLayout()
        self.title_layout.setSpacing(2)
        
        self.title_label = QLabel("Объекты")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #c0c0c0;
            }
        """)
        
        # Индикатор загрузки (прогресс-бар)
        self.loading_bar = QProgressBar()
        self.loading_bar.setMaximum(0)  # Бесконечная анимация
        self.loading_bar.setMinimum(0)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setFixedHeight(3)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)
        self.loading_bar.hide()  # Скрыт по умолчанию
        
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.loading_bar)
        
        layout.addLayout(self.title_layout)
        
        # Создаём само дерево
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)  # Скрываем заголовок (у нас свой)
        self.tree_view.setAlternatingRowColors(True)  # Чередование цветов строк
        self.tree_view.setAnimated(True)  # Анимация раскрытия
        self.tree_view.setIndentation(20)  # Отступ для вложенных элементов
        
        # Стили для дерева
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: white;
                border: none;
                outline: none;
            }
            QTreeView::item {
                padding: 4px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTreeView::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QTreeView::item:hover {
                background-color: #f5f5f5;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                image: url(none);
                border-image: none;
            }
        """)
        
        # Создаём модель данных
        self.model = ComplexTreeModel()
        self.tree_view.setModel(self.model)
        
        # Подключаем сигнал выбора элемента
        selection_model = self.tree_view.selectionModel()
        selection_model.selectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.tree_view)
        
        # Создаём клиент API
        self.api_client = ApiClient()
        
        # Загружаем комплексы при инициализации
        self.load_complexes()
        
        print("✅ Виджет дерева создан")
    
    def show_loading(self, show: bool = True):
        """
        Показать/скрыть индикатор загрузки
        
        Args:
            show: True - показать, False - скрыть
        """
        if show:
            self.loading_bar.show()
            self.title_label.setText("Объекты (загрузка...)")
        else:
            self.loading_bar.hide()
            self.title_label.setText("Объекты")
        
        # Обновляем отображение
        self.loading_bar.repaint()
    
    def load_complexes(self):
        """
        Загружает список комплексов с сервера
        """
        self.show_loading(True)
        
        try:
            # Загружаем комплексы
            complexes = self.api_client.get_complexes()
            
            # Обновляем модель
            self.model.set_complexes(complexes)
            
            # Разворачиваем все элементы (опционально)
            self.tree_view.expandAll()
            
            print(f"✅ Комплексы отображены в дереве: {len(complexes)} шт.")
            
        except Exception as e:
            # Показываем ошибку пользователю
            QMessageBox.critical(
                self,
                "Ошибка загрузки",
                f"Не удалось загрузить список комплексов:\n{str(e)}"
            )
            print(f"❌ Ошибка загрузки комплексов: {e}")
            
        finally:
            self.show_loading(False)
    
    def _on_selection_changed(self, selected, deselected):
        """
        Обработчик изменения выбора в дереве
        
        Args:
            selected: новые выбранные индексы
            deselected: снятые выделения
        """
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]  # Берём первый выбранный индекс
            # Получаем тип и ID элемента через кастомные роли
            item_type = index.data(ComplexTreeModel.ItemTypeRole)
            item_id = index.data(ComplexTreeModel.ItemIdRole)
            
            if item_type and item_id:
                print(f"🔹 Выбран элемент: {item_type} (ID: {item_id})")
                # Испускаем сигнал для правой панели
                self.item_selected.emit(item_type, item_id)
    
    def refresh(self):
        """
        Обновить данные (перезагрузить с сервера)
        Вызывается при нажатии кнопки "Обновить"
        """
        print("🔄 Обновление данных...")
        self.load_complexes()