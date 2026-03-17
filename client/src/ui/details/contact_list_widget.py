# client/src/ui/details/contact_list_widget.py
"""
Виджет для отображения списка контактных лиц.
Группирует по категориям (юридические, финансовые, технические и т.д.)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel
from PySide6.QtCore import Qt
from typing import Dict, List, Optional

from src.models.responsible_person import ResponsiblePerson
from src.ui.details.field_manager import FieldManager
from utils.logger import get_logger

log = get_logger(__name__)


class ContactListWidget(QWidget):
    """
    Виджет для отображения списка контактных лиц.
    
    Группирует контакты по категориям:
    - Юридические вопросы
    - Финансовые вопросы
    - Технические вопросы
    - Пожарная безопасность
    - Аварийные ситуации
    - Общие вопросы
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(15)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self._groups: Dict[str, QGroupBox] = {}
        
        log.debug("ContactListWidget инициализирован")
    
    def set_contacts(self, persons: List[ResponsiblePerson]) -> None:
        """
        Устанавливает список контактов и группирует их по категориям.
        
        Args:
            persons: Список ответственных лиц
        """
        # Очищаем текущие группы
        self._clear_groups()
        
        if not persons:
            self._show_empty()
            return
        
        # Группируем по категориям
        grouped = FieldManager.format_responsible_persons(persons)
        
        # Создаём группы для каждой категории
        for category, contacts in grouped.items():
            self._create_category_group(category, contacts)
        
        # Добавляем растяжку в конце
        self._layout.addStretch()
        
        log.debug(f"Отображено {len(persons)} контактов в {len(grouped)} категориях")
    
    def _create_category_group(self, category: str, contacts: List[str]) -> None:
        """
        Создаёт группу для категории контактов.
        
        Args:
            category: Название категории
            contacts: Список строк с информацией о контактах
        """
        group = QGroupBox(category)
        group_layout = QVBoxLayout(group)
        
        for contact_info in contacts:
            label = QLabel(contact_info)
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            group_layout.addWidget(label)
        
        group_layout.addStretch()
        self._layout.addWidget(group)
        self._groups[category] = group
    
    def _show_empty(self) -> None:
        """Показывает сообщение об отсутствии контактов."""
        label = QLabel("Нет контактных данных")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #999999; padding: 40px;")
        self._layout.addWidget(label)
        self._layout.addStretch()
    
    def _clear_groups(self) -> None:
        """Очищает все группы."""
        # Удаляем все группы из словаря и из layout
        for key, group in list(self._groups.items()):
            self._layout.removeWidget(group)
            group.deleteLater()
            del self._groups[key]
        
        # Очищаем layout от остальных виджетов
        self._clear_layout()
    
    def _clear_layout(self) -> None:
        """Очищает layout от всех дочерних виджетов."""
        while self._layout.count() > 0:
            item = self._layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    # Проверяем, что это не группа (которую мы уже удалили)
                    if widget not in self._groups.values():
                        widget.deleteLater()