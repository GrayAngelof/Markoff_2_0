# client/src/ui/details_panel.py
"""
Правая панель с детальной информацией о выбранном объекте
Содержит вкладки: Физика, Юрики, Пожарка
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QGridLayout
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from typing import Optional, Tuple, Any

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class DetailsPanel(QWidget):
    """
    Панель детальной информации с вкладками
    
    Структура для каждого типа объекта:
    
    КОМПЛЕКС:
    - Заголовок: КОМПЛЕКС: Название
    - Иерархия: (пусто)
    - Основная информация: адрес, владелец, описание, планировка
    
    КОРПУС:
    - Заголовок: КОРПУС: Название
    - Иерархия: (в составе комплекса: Название комплекса)
    - Основная информация: адрес, описание, планировка
    
    ЭТАЖ:
    - Заголовок: ЭТАЖ: Номер
    - Иерархия: (в составе корпуса: Название корпуса, комплекс: Название комплекса)
    - Основная информация: описание, планировка, тип этажа
    
    ПОМЕЩЕНИЕ:
    - Заголовок: ПОМЕЩЕНИЕ: Номер
    - Иерархия: (этаж Номер, корпус Название, комплекс: Название комплекса)
    - Основная информация: площадь, тип, описание
    - Для занятых: арендатор, договор, срок действия, арендная плата
    """
    
    def __init__(self, parent=None):
        """Инициализация панели"""
        super().__init__(parent)
        
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Шапка
        self._create_header()
        layout.addWidget(self.header_widget)
        
        # Контейнер для контента
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        
        # Заглушка
        self._create_placeholder()
        
        # Информационные блоки
        self._create_info_blocks()
        
        # Вкладки
        self._create_tabs()
        
        layout.addWidget(self.content_widget)
        layout.addStretch()
        
        # Состояние
        self.current_type = None
        self.current_id = None
        self.current_data = None
        
        print("✅ DetailsPanel: создана")
    
    # ===== Инициализация UI =====
    
    def _create_header(self):
        """Создание шапки панели"""
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 2px solid #d0d0d0;
            }
        """)
        self.header_widget.setFixedHeight(80)
        
        header_layout = QVBoxLayout(self.header_widget)
        header_layout.setContentsMargins(15, 5, 15, 5)
        
        # Верхняя строка: иконка + заголовок + статус
        top_row = QHBoxLayout()
        
        self.icon_label = QLabel("🏢")
        self.icon_label.setStyleSheet("font-size: 24px;")
        top_row.addWidget(self.icon_label)
        
        self.title_label = QLabel("")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.title_label.setFont(title_font)
        top_row.addWidget(self.title_label, 1)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 4px 12px;
                border-radius: 12px;
                background-color: #e0e0e0;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        top_row.addWidget(self.status_label)
        
        header_layout.addLayout(top_row)
        
        # Нижняя строка: иерархия
        self.hierarchy_label = QLabel("")
        self.hierarchy_label.setStyleSheet("color: #666666; font-size: 11px;")
        self.hierarchy_label.setWordWrap(True)
        header_layout.addWidget(self.hierarchy_label)
    
    def _create_placeholder(self):
        """Создание заглушки"""
        self.placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(self.placeholder_widget)
        
        placeholder_text = QLabel("🔍 Выберите объект в дереве слева\nдля просмотра детальной информации")
        placeholder_text.setAlignment(Qt.AlignCenter)
        placeholder_text.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 14px;
                padding: 40px;
                border: 2px dashed #cccccc;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        placeholder_layout.addWidget(placeholder_text)
        
        self.content_layout.addWidget(self.placeholder_widget)
    
    def _create_info_blocks(self):
        """Создание информационных блоков"""
        # Блок основной информации
        self.info_grid = QGridLayout()
        self.info_grid.setVerticalSpacing(8)
        self.info_grid.setHorizontalSpacing(20)
        self.info_grid.setColumnStretch(1, 1)
        
        self.info_widget = QWidget()
        self.info_widget.setLayout(self.info_grid)
        self.info_widget.hide()
        self.content_layout.addWidget(self.info_widget)
        
        # Создаём все возможные поля
        self.fields = {}
        field_names = [
            ("address", "Адрес:"),
            ("owner", "Владелец:"),
            ("tenant", "Арендатор:"),
            ("description", "Описание:"),
            ("plan", "Планировка:"),
            ("type", "Тип:"),
            ("contract", "Договор:"),
            ("valid_until", "Действует до:"),
            ("rent", "Арендная плата:"),
        ]
        
        for i, (key, label) in enumerate(field_names):
            # Лейбл
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold; color: #666666;")
            label_widget.setAlignment(Qt.AlignRight | Qt.AlignTop)
            
            # Значение
            value_widget = QLabel("—")
            value_widget.setWordWrap(True)
            value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
            self.info_grid.addWidget(label_widget, i, 0)
            self.info_grid.addWidget(value_widget, i, 1)
            
            self.fields[key] = value_widget
    
    def _create_tabs(self):
        """Создание вкладок"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                padding: 5px;
                margin-top: 5px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
        # Вкладка Физика
        physics_tab = QWidget()
        physics_layout = QVBoxLayout(physics_tab)
        physics_label = QLabel("📊 Статистика по физике будет здесь")
        physics_label.setAlignment(Qt.AlignCenter)
        physics_label.setStyleSheet("color: #808080; padding: 40px;")
        physics_layout.addWidget(physics_label)
        self.tab_widget.addTab(physics_tab, "📊 Физика")
        
        # Вкладка Юрики
        legal_tab = QWidget()
        legal_layout = QVBoxLayout(legal_tab)
        legal_label = QLabel("⚖️ Информация о юридических лицах будет здесь")
        legal_label.setAlignment(Qt.AlignCenter)
        legal_label.setStyleSheet("color: #808080; padding: 40px;")
        legal_layout.addWidget(legal_label)
        self.tab_widget.addTab(legal_tab, "⚖️ Юрики")
        
        # Вкладка Пожарка
        fire_tab = QWidget()
        fire_layout = QVBoxLayout(fire_tab)
        fire_label = QLabel("🔥 Данные пожарной безопасности будут здесь")
        fire_label.setAlignment(Qt.AlignCenter)
        fire_label.setStyleSheet("color: #808080; padding: 40px;")
        fire_layout.addWidget(fire_label)
        self.tab_widget.addTab(fire_tab, "🔥 Пожарка")
        
        self.content_layout.addWidget(self.tab_widget)
    
    # ===== Вспомогательные методы =====
    
    def _clear_all_fields(self):
        """Очистить все поля"""
        for field in self.fields.values():
            field.setText("—")
    
    def _set_field(self, key: str, value):
        """Установить значение поля с проверкой"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self.fields[key].setText("—")
        else:
            self.fields[key].setText(str(value))
    
    def _set_status_style(self, status: str):
        """Установка стиля статуса"""
        base_style = "padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 12px;"
        
        styles = {
            'free': base_style + "background-color: #c8e6c9; color: #2e7d32;",
            'occupied': base_style + "background-color: #ffcdd2; color: #c62828;",
            'reserved': base_style + "background-color: #fff9c4; color: #f57f17;",
            'maintenance': base_style + "background-color: #ffecb3; color: #ff6f00;",
        }
        self.status_label.setStyleSheet(styles.get(status, base_style + "background-color: #e0e0e0;"))
    
    def _show_all_fields(self, *keys):
        """Показать только указанные поля"""
        # Сначала скрываем все
        for field in self.fields.values():
            field.parent().hide()
        
        # Показываем нужные
        for key in keys:
            if key in self.fields:
                self.fields[key].parent().show()
    
    def _log_hierarchy(self, item_type: str, hierarchy_text: str):
        """Логирование иерархии для отладки"""
        print(f"📋 DetailsPanel: [{item_type}] иерархия: {hierarchy_text}")
    
    # ===== Методы отображения для каждого типа =====
    
    def _show_complex(self, data: Complex):
        """Отображение комплекса"""
        self.title_label.setText(f"КОМПЛЕКС: {data.name}")
        self.hierarchy_label.setText("")
        self.icon_label.setText("🏢")
        
        # Логируем
        self._log_hierarchy("complex", "корневой уровень")
        
        # Статус
        self.status_label.setText("Активен")
        self._set_status_style(None)
        
        # Поля для комплекса
        self._set_field("address", data.address)
        self._set_field("owner", f"ID владельца: {data.owner_id}" if data.owner_id else None)
        self._set_field("description", data.description)
        self._set_field("plan", "[ ссылка на общий план ]")
        
        # Показываем информационный блок
        self.info_widget.show()
        
        # Показываем нужные поля
        self._show_all_fields("address", "owner", "description", "plan")
    
    def _show_building(self, data: Building, complex_name: str):
        """Отображение корпуса"""
        self.title_label.setText(f"КОРПУС: {data.name}")
        hierarchy_text = f"(в составе комплекса: {complex_name})"
        self.hierarchy_label.setText(hierarchy_text)
        self.icon_label.setText("🏭")
        
        # Логируем
        self._log_hierarchy("building", hierarchy_text)
        
        # Статус
        self.status_label.setText("Активен")
        self._set_status_style(None)
        
        # Поля для корпуса
        self._set_field("address", data.address)
        self._set_field("description", data.description)
        self._set_field("plan", "[ ссылка на планы корпуса ]")
        
        # Показываем информационный блок
        self.info_widget.show()
        
        # Показываем нужные поля
        self._show_all_fields("address", "description", "plan")
    
    def _show_floor(self, data: Floor, building_name: str, complex_name: str):
        """Отображение этажа"""
        # Номер этажа
        if data.number < 0:
            floor_text = f"Подвал {abs(data.number)}"
        elif data.number == 0:
            floor_text = "Цокольный этаж"
        else:
            floor_text = f"Этаж {data.number}"
        
        self.title_label.setText(f"ЭТАЖ: {floor_text}")
        hierarchy_text = f"(в составе корпуса: {building_name}, комплекс: {complex_name})"
        self.hierarchy_label.setText(hierarchy_text)
        self.icon_label.setText("🏗️")
        
        # Логируем
        self._log_hierarchy("floor", hierarchy_text)
        
        # Статус
        self.status_label.setText("Активен")
        self._set_status_style(None)
        
        # Поля для этажа
        self._set_field("description", data.description)
        self._set_field("plan", "[ ссылка на план этажа ]")
        self._set_field("type", "Этаж с офисами")
        
        # Показываем информационный блок
        self.info_widget.show()
        
        # Показываем нужные поля
        self._show_all_fields("description", "plan", "type")
    
    def _show_room(self, data: Room, floor_num: int, building_name: str, complex_name: str):
        """Отображение помещения"""
        self.title_label.setText(f"ПОМЕЩЕНИЕ: {data.number}")
        
        # Формируем строку иерархии
        if floor_num < 0:
            floor_text = f"подвал {abs(floor_num)}"
        elif floor_num == 0:
            floor_text = "цокольный этаж"
        else:
            floor_text = f"этаж {floor_num}"
        
        hierarchy_text = f"(этаж {floor_num}, корпус {building_name}, комплекс: {complex_name})"
        self.hierarchy_label.setText(hierarchy_text)
        self.icon_label.setText("🚪")
        
        # Логируем
        self._log_hierarchy("room", hierarchy_text)
        
        # Статус
        status_map = {
            'free': 'СВОБОДНО',
            'occupied': 'ЗАНЯТО',
            'reserved': 'ЗАРЕЗЕРВИРОВАНО',
            'maintenance': 'РЕМОНТ'
        }
        status_text = status_map.get(data.status_code, data.status_code or "НЕИЗВЕСТНО")
        self.status_label.setText(status_text)
        self._set_status_style(data.status_code)
        
        # Площадь
        if data.area:
            self._set_field("address", f"Площадь: {data.area} м²")
        else:
            self._set_field("address", "Площадь не указана")
        
        # Тип помещения
        type_map = {
            1: "Офисное помещение",
            2: "Архив",
            3: "Склад",
            4: "Техническое помещение",
        }
        room_type = type_map.get(data.physical_type_id, "Неизвестный тип")
        self._set_field("type", room_type)
        
        # Описание
        self._set_field("description", data.description or "Описание отсутствует")
        
        # Планировка (пока нет)
        self._set_field("plan", None)
        
        # Показываем информационный блок
        self.info_widget.show()
        
        # Базовые поля для всех помещений
        base_fields = ["address", "type", "description", "plan"]
        
        # Для занятых помещений добавляем поля аренды
        if data.status_code == 'occupied':
            # TODO: брать реальные данные из БД
            self._set_field("tenant", "Арендатор: ООО \"Ромашка\" (ИНН 7712345678)")
            self._set_field("contract", "Договор: №А-2024-001 от 01.01.2024")
            self._set_field("valid_until", "Действует до: 31.12.2025")
            self._set_field("rent", "Арендная плата: 45 000 ₽/мес")
            
            # Показываем все поля
            self._show_all_fields(*(base_fields + ["tenant", "contract", "valid_until", "rent"]))
        else:
            # Для свободных и других статусов
            self._set_field("tenant", None)
            self._set_field("contract", None)
            self._set_field("valid_until", None)
            self._set_field("rent", None)
            
            # Показываем только базовые поля
            self._show_all_fields(*base_fields)
    
    # ===== Публичные методы =====
    
    @Slot(str, int, object, dict)
    def show_item_details(self, item_type: str, item_id: int, item_data, context: dict):
        """
        Показать информацию о выбранном объекте с контекстом из родительских узлов
        
        Args:
            item_type: тип элемента
            item_id: идентификатор
            item_data: объект модели
            context: словарь с именами родительских узлов
        """
        self.current_type = item_type
        self.current_id = item_id
        self.current_data = item_data
        
        print(f"\n📋 DetailsPanel: выбран {item_type} #{item_id}")
        print(f"   Контекст: {context}")
        
        # Скрываем заглушку
        self.placeholder_widget.hide()
        
        # Очищаем поля
        self._clear_all_fields()
        
        # Отображаем соответствующий тип с контекстом из узла
        if item_type == 'complex' and isinstance(item_data, Complex):
            self._show_complex(item_data)
            
        elif item_type == 'building' and isinstance(item_data, Building):
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            self._show_building(item_data, complex_name)
            
        elif item_type == 'floor' and isinstance(item_data, Floor):
            building_name = context.get('building_name', 'Неизвестный корпус')
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            self._show_floor(item_data, building_name, complex_name)
            
        elif item_type == 'room' and isinstance(item_data, Room):
            floor_num = context.get('floor_num', 0)
            building_name = context.get('building_name', 'Неизвестный корпус')
            complex_name = context.get('complex_name', 'Неизвестный комплекс')
            self._show_room(item_data, floor_num, building_name, complex_name)
            
        else:
            self.clear()
    
    def clear(self):
        """Очистить панель (показать заглушку)"""
        self.current_type = None
        self.current_id = None
        self.current_data = None
        
        self.placeholder_widget.show()
        self.info_widget.hide()
        
        self.title_label.setText("")
        self.hierarchy_label.setText("")
        self.status_label.setText("")
        self.icon_label.setText("🏢")
    
    def get_current_selection(self) -> Tuple[Optional[str], Optional[int], Optional[Any]]:
        """Получить текущий выбранный объект"""
        return self.current_type, self.current_id, self.current_data