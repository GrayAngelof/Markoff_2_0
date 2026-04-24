# client/src/core/types/protocols.py
"""
Протоколы для типизации объектов в системе.

Определяет структурные типы (Protocol) для проверки наличия
необходимых атрибутов у объектов без явного наследования.
"""

# ===== ИМПОРТЫ =====
from typing import List, Protocol

from .nodes import NodeType


# ===== ПРОТОКОЛЫ =====
class HasNodeType(Protocol):
    """
    Объект, имеющий атрибут NODE_TYPE.

    Используется для статической типизации объектов,
    которые хранят тип узла как атрибут класса.
    """

    NODE_TYPE: NodeType


class IDetailsViewModel(Protocol):
    """
    Протокол для ViewModel панели деталей.

    Определяет минимальный контракт, которому должна соответствовать
    любая ViewModel, передаваемая в NodeDetailsLoaded.

    UI-слой сам решает, какой конкретный тип использовать,
    но ядро гарантирует наличие этих атрибутов.
    """

    @property
    def header_title(self) -> str: ...

    @property
    def header_subtitle(self) -> str: ...

    @property
    def header_status_name(self) -> str | None: ...

    @property
    def grid_items(self) -> List[tuple[str, str]]: ...