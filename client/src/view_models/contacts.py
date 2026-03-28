# client/src/view_models/contacts.py
"""
View Models для вкладки "Юрики".

Содержат информацию о контрагентах и контактных лицах для отображения в UI.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass, field
from typing import List, Optional


# ===== VIEW MODELS =====
@dataclass(frozen=True, slots=True)
class ContactPerson:
    """Контактное лицо."""

    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: bool = False


@dataclass(frozen=True, slots=True)
class ContactGroup:
    """Группа контактов по категории."""

    category: str
    contacts: List[ContactPerson] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ContactSummary:
    """Сводка по контрагентам."""

    total_area: float = 0.0      # общая площадь
    rented_area: float = 0.0     # сданная площадь
    occupancy_rate: float = 0.0  # процент занятости
    total_debt: float = 0.0      # общая задолженность


@dataclass(frozen=True, slots=True)
class ContactsVM:
    """
    Контакты для отображения в UI.

    Содержит агрегированные данные и группы контактов.
    """

    total_organizations: int = 0  # всего организаций
    tenants_count: int = 0        # арендаторов
    owners_count: int = 0         # собственников
    debtors_count: int = 0        # должников

    groups: List[ContactGroup] = field(default_factory=list)
    summary: ContactSummary = field(default_factory=ContactSummary)

    @classmethod
    def empty(cls) -> "ContactsVM":
        """Возвращает пустую ViewModel (для fallback)."""
        return cls()