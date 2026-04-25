# client/src/view_models/__init__.py
"""
View Models — контракты данных между бизнес-логикой и UI.

Все View Models иммутабельны (@dataclass(frozen=True, slots=True)).
Никакой бизнес-логики, только данные.
"""

# ===== ИМПОРТЫ =====
from .details import DetailsViewModel, HeaderViewModel, InfoGridItem

# ===== ПУБЛИЧНОЕ API =====
__all__ = [
    # Детали
    "DetailsViewModel",
    "HeaderViewModel",
    "InfoGridItem",
]