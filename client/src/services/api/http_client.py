# client/src/services/api/http_client.py
"""
Низкоуровневый HTTP клиент.

Отвечает только за:
- Выполнение HTTP запросов
- Обработку статус кодов
- Преобразование ошибок в нашу иерархию исключений

НЕ отвечает за:
- Формирование URL (это endpoints.py)
- Преобразование JSON в модели (это converters.py)
- Логику повторных попыток (это может быть добавлено позже)
"""

import os
from typing import Optional, Any

import requests

from src.services.api.errors import (
    ApiError, ConnectionError, TimeoutError,
    NotFoundError, ClientError, ServerError
)
from utils.logger import get_logger

log = get_logger(__name__)


class HttpClient:
    """
    Низкоуровневый HTTP клиент с сессией.
    
    Использует requests.Session для переиспользования соединений.
    Все ошибки преобразуются в нашу иерархию исключений.
    
    Атрибуты:
        _base_url: Базовый URL сервера (из переменной окружения или по умолчанию)
        _session: requests.Session для переиспользования соединений
        _default_timeout: Таймаут по умолчанию (секунды)
    """
    
    # Константы по умолчанию
    DEFAULT_BASE_URL = "http://localhost:8000"
    DEFAULT_TIMEOUT = 10
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Инициализирует HTTP клиент.
        
        Args:
            base_url: Базовый URL сервера. Если не указан,
                     берется из переменной окружения API_URL,
                     или используется localhost.
        """
        self._base_url = base_url or os.getenv("API_URL", self.DEFAULT_BASE_URL)
        self._base_url = self._base_url.rstrip('/')
        
        self._default_timeout = self.DEFAULT_TIMEOUT
        
        # Создаём сессию с общими заголовками
        self._session = requests.Session()
        self._session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Markoff-Client/1.0'
        })
        
        log.api(f"HttpClient initialized with base URL: {self._base_url}")
    
    def get(self, path: str, timeout: Optional[int] = None) -> Any:
        """
        Выполняет GET запрос.
        
        Args:
            path: Путь относительно base_url (начинается с /)
            timeout: Таймаут в секундах (если None, используется значение по умолчанию)
            
        Returns:
            Any: JSON ответа (может быть dict, list, None)
            
        Raises:
            ConnectionError: Не удалось соединиться с сервером
            TimeoutError: Таймаут ожидания ответа
            NotFoundError: HTTP 404
            ClientError: HTTP 4xx (кроме 404)
            ServerError: HTTP 5xx
            ApiError: Другие ошибки
        """
        url = f"{self._base_url}{path}"
        timeout_sec = timeout or self._default_timeout
        
        log.debug(f"HTTP GET {url} (timeout={timeout_sec}s)")
        
        try:
            response = self._session.get(url, timeout=timeout_sec)
            
            # Логируем статус ответа
            log.api(f"Response: {response.status_code} {url}")
            
            # Обрабатываем статус коды
            self._handle_status_code(response, url)
            
            # Для 204 No Content возвращаем None
            if response.status_code == 204 or not response.content:
                return None
            
            # Парсим JSON
            try:
                return response.json()
            except ValueError as e:
                log.error(f"Invalid JSON response from {url}: {e}")
                raise ApiError(f"Invalid JSON response: {e}") from e
                
        except requests.exceptions.Timeout as e:
            log.error(f"Timeout connecting to {url}: {e}")
            raise TimeoutError(f"Timeout after {timeout_sec}s: {url}") from e
            
        except requests.exceptions.ConnectionError as e:
            log.error(f"Connection error to {url}: {e}")
            raise ConnectionError(f"Cannot connect to {self._base_url}") from e
            
        except requests.exceptions.RequestException as e:
            log.error(f"Request error: {e}")
            raise ApiError(f"Request failed: {e}") from e
    
    def _handle_status_code(self, response: requests.Response, url: str) -> None:
        """
        Обрабатывает HTTP статус код, преобразуя в соответствующие исключения.
        
        Args:
            response: Ответ requests
            url: URL запроса (для логирования)
            
        Raises:
            Соответствующее исключение в зависимости от статус кода
        """
        status = response.status_code
        
        if status == 404:
            raise NotFoundError(
                f"Resource not found: {url}",
                status_code=status,
                response_body=response.text[:500] if response.text else None
            )
        
        elif 400 <= status < 500:
            raise ClientError(
                f"Client error {status}: {url}",
                status_code=status,
                response_body=response.text[:500] if response.text else None
            )
        
        elif 500 <= status < 600:
            raise ServerError(
                f"Server error {status}: {url}",
                status_code=status,
                response_body=response.text[:500] if response.text else None
            )
        
        # 2xx и 3xx — нормальные статусы, не выбрасываем исключения
    
    def close(self) -> None:
        """Закрывает HTTP сессию."""
        self._session.close()
        log.debug("HttpClient closed")
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрывает сессию при выходе из контекста."""
        self.close()