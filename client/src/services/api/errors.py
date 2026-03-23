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

from typing import Optional


class ApiError(Exception):
    """
    Базовое исключение для всех ошибок API слоя.
    
    Атрибуты:
        status_code: HTTP статус код (если применимо)
        response_body: Тело ответа сервера (если есть)
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None,
                 response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
    
    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            return f"[{self.status_code}] {base}"
        return base


class ConnectionError(ApiError):
    """
    Ошибка соединения с сервером.
    
    Возникает когда:
    - Сервер недоступен (не отвечает на пинг)
    - DNS не резолвится
    - Отказано в соединении
    """
    pass


class TimeoutError(ConnectionError):
    """
    Таймаут соединения.
    
    Возникает когда сервер не отвечает в течение установленного времени.
    """
    pass


class NotFoundError(ApiError):
    """
    Ресурс не найден (HTTP 404).
    
    Это не всегда ошибка — например, у комплекса может не быть корпусов.
    Используется для индикации отсутствия запрошенного ресурса.
    """
    pass


class ClientError(ApiError):
    """
    Ошибка клиента (HTTP 4xx, кроме 404).
    
    Возникает при:
    - 400 Bad Request — неверный запрос
    - 401 Unauthorized — требуется авторизация
    - 403 Forbidden — недостаточно прав
    - 422 Unprocessable Entity — ошибка валидации
    """
    pass


class ServerError(ApiError):
    """
    Ошибка сервера (HTTP 5xx).
    
    Возникает при:
    - 500 Internal Server Error — внутренняя ошибка сервера
    - 502 Bad Gateway — прокси не смог передать запрос
    - 503 Service Unavailable — сервер перегружен
    """
    pass