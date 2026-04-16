# client/src/services/loading/__init__.py
"""
Приватный пакет загрузчиков данных.

ВНИМАНИЕ: Это ПРИВАТНЫЙ пакет. Никто не должен импортировать из него напрямую.
Все публичные методы доступны через DataLoader (services.data_loader).
"""

# Импортируем для удобства внутри services (не для экспорта!)
from src.services.loading.node_loader import NodeLoader
from src.services.loading.dictionary_loader import DictionaryLoader

# Нет __all__ — это приватный пакет
__all__: list[str] = []