# client/src/services/api/errors.py
"""
Иерархия исключений API слоя.

Все ошибки API наследуются от ApiError, что позволяет ловить их
единым блоком except, но при необходимости обрабатывать конкретные
типы ошибок отдельно.

Иерархия:
    ApiError
    ├── ConnectionError      # Ошибка сети (не достучаться до сервера)
    │   └── TimeoutError     # Таймаут соединения
    ├── NotFoundError        # 404 Not Found
    ├── ClientError          # 4xx ошибки (кроме 404)
    └── ServerError          # 5xx ошибки

Важно: все исключения сохраняют traceback через 'from e',
что позволяет при отладке видеть полную цепочку вызовов.
"""

# ===== ИМПОРТЫ =====
from typing import Optional

from utils.logger import get_logger


# ===== КОНСТАНТЫ =====
log = get_logger(__name__)


# ===== ИСКЛЮЧЕНИЯ =====
class ApiError(Exception):
    """Базовое исключение для всех ошибок API слоя."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self._log_creation()

    def _log_creation(self) -> None:
        """Логирует создание исключения (для отладки)."""
        if self.status_code:
            log.api(f"Создано исключение {self.__class__.__name__}: [{self.status_code}] {str(self)}")
        else:
            log.api(f"Создано исключение {self.__class__.__name__}: {str(self)}")

    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            return f"[{self.status_code}] {base}"
        return base


class ConnectionError(ApiError):
    """
    Ошибка соединения с сервером.

    Возникает когда сервер недоступен, DNS не резолвится или отказано в соединении.
    """
    pass


class TimeoutError(ConnectionError):
    """Таймаут соединения — сервер не ответил в установленное время."""
    pass


class NotFoundError(ApiError):
    """Ресурс не найден (HTTP 404)."""
    pass


class ClientError(ApiError):
    """
    Ошибка клиента (HTTP 4xx, кроме 404).

    Возникает при: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 422 Unprocessable Entity.
    """
    pass


class ServerError(ApiError):
    """
    Ошибка сервера (HTTP 5xx).

    Возникает при: 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable.
    """
    pass