# client/src/ui/details_panel.py
"""
Правая панель с детальной информацией о выбранном объекте
Содержит вкладки: Физика, Юрики, Пожарка
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QFrame, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont

from src.models.complex import Complex
from src.models.building import Building
from src.models.floor import Floor
from src.models.room import Room


class DetailsPanel(QWidget):
    """
    Панель детальной информации с вкладками
    
    Структура:
    - Шапка: тип объекта, название, статус
    - Основная информация: адрес, описание, даты
    - Вкладки: Физика, Юрики, Пожарка
    """
    
    def __init__(self):
        """Инициализация панели информации"""
        super().__init__()
        
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаём шапку (она будет добавлена в layout отдельно)
        self._create_header()
        layout.addWidget(self.header_widget)
        
        # Создаём контейнер для контента
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)
        
        # Создаём блок основной информации
        self._create_info_block()
        
        # Создаём вкладки
        self._create_tabs()
        
        layout.addWidget(self.content_widget)
        
        # Добавляем растяжение в конце
        layout.addStretch()
        
        # Текущий выбранный объект
        self.current_type = None
        self.current_id = None
        self.current_data = None
        
        print("✅ DetailsPanel: создана с вкладками")
    
    def _create_header(self):
        """Создание шапки панели"""
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 2px solid #d0d0d0;
            }
        """)
        self.header_widget.setFixedHeight(60)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(15, 5, 15, 5)
        
        # Тип объекта (иконка + текст)
        self.type_label = QLabel("🏢")
        self.type_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(self.type_label)
        
        # Название объекта
        self.title_label = QLabel("Выберите объект")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label, 1)
        
        # Статус объекта
        self.status_label = QLabel("—")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 4px 12px;
                border-radius: 12px;
                background-color: #e0e0e0;
                font-weight: bold;
            }
        """)
        header_layout.addWidget(self.status_label)
    
    def _create_info_block(self):
        """Создание блока с основной информацией"""
        info_group = QGroupBox("Основная информация")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        grid = QGridLayout(info_group)
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(20)
        
        # Адрес
        grid.addWidget(QLabel("Адрес:"), 0, 0, Qt.AlignRight)
        self.address_label = QLabel("—")
        self.address_label.setWordWrap(True)
        grid.addWidget(self.address_label, 0, 1)
        
        # Владелец
        grid.addWidget(QLabel("Владелец:"), 1, 0, Qt.AlignRight)
        self.owner_label = QLabel("—")
        grid.addWidget(self.owner_label, 1, 1)
        
        # Описание
        grid.addWidget(QLabel("Описание:"), 2, 0, Qt.AlignRight)
        self.description_label = QLabel("—")
        self.description_label.setWordWrap(True)
        grid.addWidget(self.description_label, 2, 1)
        
        # Даты
        grid.addWidget(QLabel("Создан:"), 3, 0, Qt.AlignRight)
        self.created_label = QLabel("—")
        grid.addWidget(self.created_label, 3, 1)
        
        grid.addWidget(QLabel("Обновлён:"), 4, 0, Qt.AlignRight)
        self.updated_label = QLabel("—")
        grid.addWidget(self.updated_label, 4, 1)
        
        self.content_layout.addWidget(info_group)
    
    def _create_tabs(self):
        """Создание вкладок"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                padding: 5px;
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
        self.physics_tab = self._create_placeholder_tab("📊 Статистика по физике будет здесь")
        self.tab_widget.addTab(self.physics_tab, "📊 Физика")
        
        # Вкладка Юрики
        self.legal_tab = self._create_placeholder_tab("⚖️ Информация о юридических лицах будет здесь")
        self.tab_widget.addTab(self.legal_tab, "⚖️ Юрики")
        
        # Вкладка Пожарка
        self.fire_tab = self._create_placeholder_tab("🔥 Данные пожарной безопасности будут здесь")
        self.tab_widget.addTab(self.fire_tab, "🔥 Пожарка")
        
        self.content_layout.addWidget(self.tab_widget)
    
    def _create_placeholder_tab(self, text: str) -> QWidget:
        """Создать виджет-заглушку для вкладки"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #808080;
                padding: 40px;
                font-size: 12px;
            }
        """)
        
        layout.addWidget(label)
        return widget
    
    def _format_datetime(self, dt) -> str:
        """Форматирование даты и времени"""
        if not dt:
            return "—"
        if hasattr(dt, 'strftime'):
            return dt.strftime("%d.%m.%Y %H:%M")
        return str(dt)
    
    def _clear_info(self):
        """Очистить всю информацию"""
        self.title_label.setText("Выберите объект")
        self.status_label.setText("—")
        self.address_label.setText("—")
        self.owner_label.setText("—")
        self.description_label.setText("—")
        self.created_label.setText("—")
        self.updated_label.setText("—")
        self.type_label.setText("🏢")
    
    def _set_complex_info(self, complex_data: Complex):
        """Заполнить информацию для комплекса"""
        self.title_label.setText(complex_data.name)
        
        # Статус (пока заглушка, в модели Complex нет status_id, но есть в БД)
        # TODO: получить статус по status_id
        self.status_label.setText("Активен")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 4px 12px;
                border-radius: 12px;
                background-color: #e0e0e0;
                font-weight: bold;
            }
        """)
        
        self.address_label.setText(complex_data.address or "Не указан")
        self.owner_label.setText(f"ID владельца: {complex_data.owner_id}" if complex_data.owner_id else "Не указан")
        self.description_label.setText(complex_data.description or "Нет описания")
        self.created_label.setText(self._format_datetime(complex_data.created_at))
        self.updated_label.setText(self._format_datetime(complex_data.updated_at))
        self.type_label.setText("🏢")
    
    def _set_building_info(self, building_data: Building):
        """Заполнить информацию для корпуса"""
        self.title_label.setText(building_data.name)
        
        # Статус (пока заглушка)
        self.status_label.setText("Активен")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 4px 12px;
                border-radius: 12px;
                background-color: #e0e0e0;
                font-weight: bold;
            }
        """)
        
        self.address_label.setText(building_data.address or "Не указан")
        self.owner_label.setText("—")  # У корпуса нет отдельного владельца
        self.description_label.setText(building_data.description or "Нет описания")
        self.created_label.setText(self._format_datetime(building_data.created_at))
        self.updated_label.setText(self._format_datetime(building_data.updated_at))
        self.type_label.setText("🏭")
    
    def _set_floor_info(self, floor_data: Floor):
        """Заполнить информацию для этажа"""
        # Формируем номер этажа с учётом подвала/цоколя
        floor_num = floor_data.number
        if floor_num < 0:
            floor_text = f"Подвал {abs(floor_num)}"
        elif floor_num == 0:
            floor_text = "Цокольный этаж"
        else:
            floor_text = f"Этаж {floor_num}"
        
        self.title_label.setText(floor_text)
        
        # Статус (пока заглушка)
        self.status_label.setText("Активен")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 4px 12px;
                border-radius: 12px;
                background-color: #e0e0e0;
                font-weight: bold;
            }
        """)
        
        self.address_label.setText("—")
        self.owner_label.setText("—")
        self.description_label.setText(floor_data.description or "Нет описания")
        self.created_label.setText(self._format_datetime(floor_data.created_at))
        self.updated_label.setText(self._format_datetime(floor_data.updated_at))
        self.type_label.setText("🏗️")
    
    def _set_room_info(self, room_data: Room):
        """Заполнить информацию для помещения"""
        self.title_label.setText(f"Помещение {room_data.number}")
        
        # Статус с цветом
        status_map = {
            'free': 'СВОБОДНО',
            'occupied': 'ЗАНЯТО',
            'reserved': 'ЗАРЕЗЕРВИРОВАНО',
            'maintenance': 'РЕМОНТ'
        }
        status_text = status_map.get(room_data.status_code or '', room_data.status_code or 'НЕИЗВЕСТНО')
        
        self.status_label.setText(status_text)
        
        # Цвет статуса
        if room_data.status_code == 'free':
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 4px 12px;
                    border-radius: 12px;
                    background-color: #c8e6c9;
                    color: #2e7d32;
                    font-weight: bold;
                }
            """)
        elif room_data.status_code == 'occupied':
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 4px 12px;
                    border-radius: 12px;
                    background-color: #ffcdd2;
                    color: #c62828;
                    font-weight: bold;
                }
            """)
        elif room_data.status_code == 'reserved':
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 4px 12px;
                    border-radius: 12px;
                    background-color: #fff9c4;
                    color: #f57f17;
                    font-weight: bold;
                }
            """)
        else:
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 4px 12px;
                    border-radius: 12px;
                    background-color: #e0e0e0;
                    color: #000000;
                    font-weight: bold;
                }
            """)
        
        self.address_label.setText("—")
        
        # Для занятых помещений показываем арендатора (пока заглушка)
        if room_data.status_code == 'occupied':
            self.owner_label.setText("Арендатор: ООО \"Ромашка\" (будет из БД)")
        else:
            self.owner_label.setText("Нет арендатора")
        
        # Добавляем информацию о площади, если есть
        description_parts = []
        if room_data.description:
            description_parts.append(room_data.description)
        if room_data.area:
            description_parts.append(f"Площадь: {room_data.area} м²")
        
        self.description_label.setText("\n".join(description_parts) if description_parts else "Нет описания")
        self.created_label.setText(self._format_datetime(room_data.created_at))
        self.updated_label.setText(self._format_datetime(room_data.updated_at))
        self.type_label.setText("🚪")
    
    # ===== Публичные методы =====
    
    @Slot(str, int)
    def show_item_details(self, item_type: str, item_id: int):
        """
        Показать информацию о выбранном объекте
        
        Args:
            item_type: тип элемента ('complex', 'building', 'floor', 'room')
            item_id: идентификатор элемента
        """
        # Сохраняем текущий объект
        self.current_type = item_type
        self.current_id = item_id
        
        print(f"📋 DetailsPanel: запрос информации для {item_type} #{item_id}")
        
        # В реальности здесь данные будут приходить из дерева
        # Сейчас они передаются через сигнал, но сам объект модели не передаётся
        # TODO: передавать в сигнале не только тип и ID, но и сам объект
        
        # ПОКА ИСПОЛЬЗУЕМ ТЕСТОВЫЕ ДАННЫЕ
        # Позже нужно будет получать данные из кэша или по запросу
        
        if item_type == 'complex':
            test_complex = Complex(
                id=item_id,
                name="Фабрика Веретено",
                buildings_count=2
            )
            # Добавляем недостающие поля для теста
            test_complex.address = "ул. Ткацкая, д. 15, Москва"
            test_complex.owner_id = 1
            test_complex.description = "Производственно-офисный комплекс бывшей текстильной фабрики. 4 корпуса, развитая инфраструктура, охраняемая территория."
            test_complex.created_at = "2026-02-10 13:43:05"
            test_complex.updated_at = "2026-02-10 13:43:05"
            self._set_complex_info(test_complex)
            
        elif item_type == 'building':
            test_building = Building(
                id=item_id,
                name="Корпус Б",
                complex_id=1,
                floors_count=2
            )
            test_building.address = "ул. Ткацкая, д. 15, корп. 2, Москва"
            test_building.description = "Административно-офисный корпус с развитой инфраструктурой, 2 этажа, отдельный вход."
            test_building.created_at = "2026-02-10 19:34:06"
            test_building.updated_at = "2026-02-10 19:34:06"
            self._set_building_info(test_building)
            
        elif item_type == 'floor':
            test_floor = Floor(
                id=item_id,
                number=2,
                building_id=4,
                rooms_count=0
            )
            test_floor.description = "Офисный этаж с открытой планировкой и переговорными комнатами"
            test_floor.created_at = "2026-02-10 20:07:58"
            test_floor.updated_at = "2026-02-10 20:07:58"
            self._set_floor_info(test_floor)
            
        elif item_type == 'room':
            test_room = Room(
                id=item_id,
                number="205",
                floor_id=5,
                area=45.5,
                status_code="free"
            )
            test_room.description = "Угловой офис с панорамными окнами, возможна перепланировка"
            test_room.created_at = "2026-02-10 20:15:00"
            test_room.updated_at = "2026-03-04 10:23:00"
            self._set_room_info(test_room)
    
    def clear(self):
        """Очистить панель (сбросить к начальному состоянию)"""
        self.current_type = None
        self.current_id = None
        self.current_data = None
        
        self._clear_info()
        
        # Сбрасываем заглушки вкладок
        self.tab_widget.setTabText(0, "📊 Физика")
        self.tab_widget.setTabText(1, "⚖️ Юрики")
        self.tab_widget.setTabText(2, "🔥 Пожарка")
        
        print("🧹 DetailsPanel: очищена")
    
    def get_current_selection(self):
        """
        Получить текущий выбранный объект
        
        Returns:
            tuple: (item_type, item_id) или (None, None)
        """
        return self.current_type, self.current_id