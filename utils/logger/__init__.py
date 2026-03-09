# utils/logger/__init__.py
"""
Инициализатор пакета логгера.
Экспортирует основной класс Logger и функцию get_logger.
"""
from utils.logger.logger import Logger, get_logger

__all__ = ['Logger', 'get_logger']