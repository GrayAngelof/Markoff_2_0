# client/src/core/api_client.py
"""
Клиент для работы с backend API
Реальные HTTP запросы к FastAPI бекенду
"""
import os
import requests
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

from src.models.complex import Complex

class ApiClient:
    """
    Клиент для взаимодействия с backend
    
    Получает URL backend из переменной окружения API_URL
    или использует localhost по умолчанию (для разработки)
    
    Принципы:
    1. Все методы возвращают готовые модели данных
    2. Ошибки API пробрасываются как исключения
    3. Единый point-of-truth для всех API вызовов
    """
    
    def __init__(self):
        """Инициализация клиента"""
        # Получаем URL из окружения (устанавливается в docker-compose)
        self.base_url = os.getenv("API_URL", "http://localhost:8000")
        # Убираем trailing slash если есть
        self.base_url = self.base_url.rstrip('/')
        
        # Создаём сессию для переиспользования соединений
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Markoff-Client/0.1.0'
        })
        
        print(f"✅ API Client инициализирован с базовым URL: {self.base_url}")
    
    def _make_request(self, method: str, path: str, **kwargs) -> Any:
        """
        Внутренний метод для выполнения HTTP запросов
        
        Args:
            method: HTTP метод (GET, POST, etc.)
            path: путь относительно base_url
            **kwargs: дополнительные параметры для requests
            
        Returns:
            JSON ответ от сервера
            
        Raises:
            Exception: с описанием ошибки
        """
        url = urljoin(self.base_url + '/', path.lstrip('/'))
        
        try:
            print(f"📡 Запрос: {method} {url}")
            response = self.session.request(method, url, **kwargs)
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            # Парсим JSON
            data = response.json()
            print(f"✅ Ответ получен: {len(data)} записей")
            return data
            
        except requests.exceptions.ConnectionError:
            print(f"❌ Ошибка подключения к {url}")
            raise Exception("Не удалось подключиться к серверу. Проверьте, запущен ли backend.")
            
        except requests.exceptions.Timeout:
            print(f"❌ Таймаут при запросе к {url}")
            raise Exception("Сервер не отвечает. Попробуйте позже.")
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP ошибка: {e}")
            if response.status_code == 404:
                raise Exception("Запрошенный ресурс не найден")
            elif response.status_code == 500:
                raise Exception("Внутренняя ошибка сервера")
            else:
                raise Exception(f"Ошибка сервера: {e}")
                
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            raise Exception(f"Ошибка при запросе к серверу: {e}")
    
    def get_complexes(self) -> List[Complex]:
        """
        Получить список всех комплексов
        
        Returns:
            List[Complex]: список комплексов (только id и name)
            
        Эндпоинт: GET /physical/
        
        Согласно ТЗ, сейчас нам нужно только название комплекса,
        поэтому из полного ответа API мы берём только id и name
        """
        try:
            # Делаем запрос к API
            data = self._make_request('GET', '/physical/')
            
            # Преобразуем сырые данные в модели
            complexes = [Complex.from_dict(item) for item in data]
            
            print(f"📦 Загружено комплексов: {len(complexes)}")
            for c in complexes:
                print(f"  - {c.name}")
            
            return complexes
            
        except Exception as e:
            print(f"❌ Ошибка загрузки комплексов: {e}")
            # Пробрасываем исключение дальше, чтобы UI мог показать ошибку
            raise