# client/src/services/loaders/base.py
"""
Базовый класс для всех загрузчиков.

Содержит обёртку _with_events для единообразной эмиссии событий
DataLoaded/DataError с поддержкой повторных попыток.
"""

# ===== ИМПОРТЫ =====
import time
from typing import Any, Callable, Dict, Optional, Tuple

from src.core.event_bus import EventBus
from src.core.types import NodeType
from src.core.events.definitions import DataError, DataLoaded, DataLoadedKind
from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== КЛАСС =====
class BaseLoader:
    """Базовый загрузчик с поддержкой повторных попыток и эмиссией событий."""

    # ---- ЖИЗНЕННЫЙ ЦИКЛ ----
    def __init__(self, bus: EventBus, retry_count: int = 1) -> None:
        """
        Инициализирует загрузчик.

        Args:
            bus: Шина событий для эмиссии DataLoaded/DataError
            retry_count: Количество повторных попыток при ошибке
        """
        log.system("BaseLoader инициализация")
        self._bus = bus
        self._retry_count = retry_count
        log.system(f"BaseLoader инициализирован: retry_count={retry_count}")

    # ---- ЗАЩИЩЁННЫЕ МЕТОДЫ ----
    def _with_events(
        self,
        node_type: NodeType,
        node_id: int,
        fn: Callable,
        kind: DataLoadedKind,
        fn_args: Tuple = (),
        fn_kwargs: Optional[Dict] = None,
    ) -> Any:
        """
        Обёртка для единообразной эмиссии событий загрузки.

        При успехе эмитит DataLoaded, при ошибке — DataError.
        Поддерживает повторные попытки при временных сбоях.

        Args:
            node_type: Тип узла
            node_id: ID узла
            fn: Функция для выполнения
            kind: Тип загружаемых данных (CHILDREN или DETAILS)
            fn_args: Позиционные аргументы для fn
            fn_kwargs: Именованные аргументы для fn

        Returns:
            Результат вызова fn

        Raises:
            Исключение, вызвавшее последнюю неудачную попытку
        """
        node_display = f"{node_type.value}#{node_id}"
        log.info(f"Загрузка {node_display} ({kind.value})")

        if fn_kwargs is None:
            fn_kwargs = {}

        last_exception = None

        for attempt in range(self._retry_count + 1):
            try:
                result = fn(*fn_args, **fn_kwargs)

                # Определяем количество загруженных элементов
                if isinstance(result, list):
                    count = len(result)
                    log.data(f"Загружено {count} элементов для {node_display}")
                elif result is not None:
                    count = 1
                    log.data(f"Загружен {type(result).__name__} для {node_display}")
                else:
                    count = 0
                    log.data(f"Результат загрузки {node_display}: None")

                self._bus.emit(DataLoaded(
                    node_type=node_type,
                    node_id=node_id,
                    payload=result,
                    count=count,
                    kind=kind,
                ))

                log.success(f"Загрузка {node_display} завершена")
                return result

            except Exception as e:
                last_exception = e
                if attempt < self._retry_count:
                    log.warning(
                        f"Ошибка загрузки {node_display}, "
                        f"повтор {attempt + 1}/{self._retry_count}: {e}"
                    )
                    time.sleep(0.5)
                else:
                    log.error(
                        f"Ошибка загрузки {node_display} "
                        f"после {self._retry_count + 1} попыток: {e}"
                    )

        # Если дошли сюда — все попытки провалились
        if last_exception is None:
            last_exception = RuntimeError(f"Unknown error loading {node_display}")

        self._bus.emit(DataError(
            node_type=node_type.value,
            node_id=node_id,
            error=str(last_exception),
        ))
        raise last_exception