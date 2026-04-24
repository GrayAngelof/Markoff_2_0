# client/src/view_models/details.py
"""
View Models для панели деталей (DetailsPanel).

Единый контракт между бизнес-логикой и UI.
Не содержит бизнес-логики, только данные для отображения.

Соответствует протоколу IDetailsViewModel из core.types.protocols.
"""

# ===== ИМПОРТЫ =====
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ===== VIEW MODELS =====
@dataclass(frozen=True, slots=True)
class HeaderViewModel:
    """Модель заголовка панели деталей."""

    title: str
    subtitle: str
    status_name: Optional[str] = None


@dataclass(frozen=True, slots=True)
class InfoGridItem:
    """Одна запись в сетке InfoGrid."""

    label: str
    value: str


@dataclass(frozen=True, slots=True)
class DetailsViewModel:
    """
    Единая ViewModel для всей панели деталей.

    Соответствует протоколу IDetailsViewModel.
    """

    header: HeaderViewModel
    grid: List[InfoGridItem] = field(default_factory=list)

    # ---- РЕАЛИЗАЦИЯ ПРОТОКОЛА IDetailsViewModel ----
    @property
    def header_title(self) -> str:
        return self.header.title

    @property
    def header_subtitle(self) -> str:
        return self.header.subtitle

    @property
    def header_status_name(self) -> Optional[str]:
        return self.header.status_name

    @property
    def grid_items(self) -> List[Tuple[str, str]]:
        return [(item.label, item.value) for item in self.grid]