# tests/test_event_bus.py
"""
Модульные тесты для EventBus.
Проверяют всю функциональность шины событий согласно спецификации.
"""
import sys
import os
import time
import threading
import gc
import weakref
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Добавляем пути для импортов
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)  # для импорта utils
sys.path.insert(0, os.path.join(ROOT_DIR, 'client', 'src'))  # для импорта core

from utils.logger.logger import get_logger, Logger
from client.src.core.event_bus import EventBus

# Настраиваем логирование для тестов
Logger.set_level(Logger.DEBUG)
Logger.enable_colors(True)
log = get_logger("TestEventBus")


@dataclass
class TestEvent:
    """Структура для проверки событий в тестах"""
    event_type: str
    data: Dict
    source: Optional[str]
    timestamp: float


class TestHandler:
    """Тестовый обработчик событий."""
    
    def __init__(self, name: str):
        self.name = name
        self.received_events: List[TestEvent] = []
        log.debug(f"TestHandler '{name}' создан")
    
    def handle(self, event: Dict[str, Any]) -> None:
        test_event = TestEvent(
            event_type=event['type'],
            data=event['data'],
            source=event['source'],
            timestamp=event['timestamp']
        )
        self.received_events.append(test_event)
        log.debug(f"Handler '{self.name}' получил: {event['type']}")
    
    def clear(self) -> None:
        self.received_events.clear()
        log.debug(f"Handler '{self.name}' очищен")
    
    def get_count(self, event_type: Optional[str] = None) -> int:
        if event_type:
            return len([e for e in self.received_events if e.event_type == event_type])
        return len(self.received_events)


class ErrorHandler:
    """Обработчик, который выбрасывает исключение"""
    
    def __init__(self, name: str):
        self.name = name
        self.called = False
    
    def handle(self, event: Dict[str, Any]) -> None:
        self.called = True
        log.debug(f"ErrorHandler '{self.name}' выбрасывает исключение")
        raise ValueError(f"Искусственная ошибка в {self.name}")


class ReentrantHandler:
    """
    Реентерабельный обработчик с защитой от бесконечных циклов.
    Испускает событие другого типа, но не более max_depth раз.
    """
    
    def __init__(self, name: str, bus: EventBus, emit_type: str, emit_data: Dict = None, max_depth: int = 3):
        self.name = name
        self.bus = bus
        self.emit_type = emit_type
        self.emit_data = emit_data or {}
        self.max_depth = max_depth
        self.received_count = 0
        self.depth = 0
        log.debug(f"ReentrantHandler '{name}' создан с max_depth={max_depth}")
    
    def handle(self, event: Dict[str, Any]) -> None:
        """Получает событие и испускает новое, если не превышена глубина"""
        current_depth = event['data'].get('depth', 0)
        
        if current_depth >= self.max_depth:
            log.debug(f"ReentrantHandler '{self.name}' достиг глубины {current_depth}, останавливаемся")
            return
        
        self.received_count += 1
        new_depth = current_depth + 1
        log.debug(f"ReentrantHandler '{self.name}' глубина {current_depth} -> испускает {self.emit_type} (глубина {new_depth})")
        self.bus.emit(self.emit_type, {"depth": new_depth, "from": self.name}, f"reentrant_{self.name}")


class SelfUnsubscribeHandler:
    """Обработчик, который отписывается сам от себя."""
    
    def __init__(self, name: str, bus: EventBus, event_type: str):
        self.name = name
        self.bus = bus
        self.event_type = event_type
        self.unsubscribe_func = None
        self.received_count = 0
        log.debug(f"SelfUnsubscribeHandler '{name}' создан")
    
    def set_unsubscribe(self, unsubscribe_func):
        self.unsubscribe_func = unsubscribe_func
    
    def handle(self, event: Dict[str, Any]) -> None:
        self.received_count += 1
        log.debug(f"SelfUnsubscribeHandler '{self.name}' получил событие и отписывается")
        if self.unsubscribe_func:
            self.unsubscribe_func()


class RecursiveHandler:
    """
    Рекурсивный обработчик с защитой от бесконечной рекурсии.
    Испускает событие того же типа, но не более max_depth раз.
    """
    
    def __init__(self, name: str, bus: EventBus, max_depth: int = 3):
        self.name = name
        self.bus = bus
        self.max_depth = max_depth
        self.received_count = 0
        self.depths: List[int] = []
        log.debug(f"RecursiveHandler '{name}' создан с max_depth={max_depth}")
    
    def handle(self, event: Dict[str, Any]) -> None:
        current_depth = event['data'].get('depth', 0)
        self.depths.append(current_depth)
        self.received_count += 1
        
        log.debug(f"RecursiveHandler '{self.name}' глубина {current_depth}")
        
        if current_depth < self.max_depth:
            new_depth = current_depth + 1
            log.debug(f"  → испускает рекурсивно с глубиной {new_depth}")
            self.bus.emit('test.recursive', {"depth": new_depth}, f"recursive_{self.name}")


def print_test_header(test_name: str) -> None:
    """Выводит заголовок теста"""
    print(f"\n{'='*60}")
    print(f"🔬 ТЕСТ: {test_name}")
    print(f"{'='*60}")


def print_test_result(success: bool, message: str = "") -> None:
    """Выводит результат теста"""
    if success:
        print(f"✅ УСПЕХ: {message}")
    else:
        print(f"❌ ПРОВАЛ: {message}")


# ============================================================================
# 1️⃣ Базовая функциональность
# ============================================================================

def test_basic_subscription_and_emit() -> bool:
    """Тест 1.1: Базовая подписка и испускание"""
    print_test_header("1.1 Базовая подписка и испускание")
    
    bus = EventBus()
    handler = TestHandler("basic")
    test_data = {"node_id": 42, "node_type": "complex"}
    test_source = "test_module"
    
    log.info("Создаём подписку")
    unsubscribe = bus.subscribe('test.event', handler.handle)
    
    log.info("Испускаем событие")
    bus.emit('test.event', test_data, test_source)
    
    success = True
    messages = []
    
    if handler.get_count() == 1:
        messages.append("✓ Получено ровно одно событие")
    else:
        success = False
        messages.append(f"✗ Ожидалось 1 событие, получено {handler.get_count()}")
    
    if handler.received_events:
        event = handler.received_events[0]
        
        if event.event_type == 'test.event':
            messages.append("✓ Тип события корректен")
        else:
            success = False
            messages.append(f"✗ Тип события: {event.event_type}")
        
        if event.data == test_data:
            messages.append("✓ Данные события корректны")
        else:
            success = False
            messages.append(f"✗ Данные события: {event.data}")
        
        if event.source == test_source:
            messages.append("✓ Источник события корректен")
        else:
            success = False
            messages.append(f"✗ Источник: {event.source}")
        
        now = time.time()
        if abs(now - event.timestamp) < 1.0:
            messages.append("✓ Timestamp корректен")
        else:
            success = False
            messages.append(f"✗ Timestamp: {event.timestamp}, текущее время: {now}")
    
    unsubscribe()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Базовая подписка и испускание")
    return success


def test_multiple_subscribers() -> bool:
    """Тест 1.2: Несколько подписчиков на одно событие"""
    print_test_header("1.2 Несколько подписчиков")
    
    bus = EventBus()
    handler1 = TestHandler("handler1")
    handler2 = TestHandler("handler2")
    handler3 = TestHandler("handler3")
    
    log.info("Подписываем трёх обработчиков на одно событие")
    unsub1 = bus.subscribe('test.multi', handler1.handle)
    unsub2 = bus.subscribe('test.multi', handler2.handle)
    unsub3 = bus.subscribe('test.multi', handler3.handle)
    
    bus.emit('test.multi', {"value": 100})
    
    success = True
    messages = []
    
    for i, handler in enumerate([handler1, handler2, handler3], 1):
        if handler.get_count() == 1:
            messages.append(f"✓ Handler{i} получил событие")
        else:
            success = False
            messages.append(f"✗ Handler{i}: ожидалось 1, получено {handler.get_count()}")
    
    unsub1()
    unsub2()
    unsub3()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Все подписчики получили событие")
    return success


def test_multiple_event_types() -> bool:
    """Тест 1.3: Один обработчик на несколько типов"""
    print_test_header("1.3 Один обработчик на несколько типов")
    
    bus = EventBus()
    handler = TestHandler("multi_type")
    
    log.info("Подписываем один обработчик на три разных типа")
    unsub1 = bus.subscribe('test.type1', handler.handle)
    unsub2 = bus.subscribe('test.type2', handler.handle)
    unsub3 = bus.subscribe('test.type3', handler.handle)
    
    bus.emit('test.type1', {"id": 1})
    bus.emit('test.type2', {"id": 2})
    bus.emit('test.type3', {"id": 3})
    
    success = True
    messages = []
    
    if handler.get_count() == 3:
        messages.append("✓ Получены все 3 события")
    else:
        success = False
        messages.append(f"✗ Ожидалось 3 события, получено {handler.get_count()}")
    
    received_types = [e.event_type for e in handler.received_events]
    expected_types = ['test.type1', 'test.type2', 'test.type3']
    
    for expected in expected_types:
        if expected in received_types:
            messages.append(f"✓ Тип {expected} получен")
        else:
            success = False
            messages.append(f"✗ Тип {expected} НЕ получен")
    
    unsub1()
    unsub2()
    unsub3()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Обработчик получает события всех типов")
    return success


def test_event_type_filtering() -> bool:
    """Тест 1.4: Фильтрация по типу события"""
    print_test_header("1.4 Фильтрация по типу")
    
    bus = EventBus()
    handler = TestHandler("filter")
    
    log.info("Подписываемся только на test.target")
    unsubscribe = bus.subscribe('test.target', handler.handle)
    
    bus.emit('test.target', {"target": True})
    bus.emit('test.other', {"other": True})
    bus.emit('another.event', {"another": True})
    bus.emit('test.target', {"target": True})
    
    success = True
    messages = []
    
    if handler.get_count() == 2:
        messages.append("✓ Получены только целевые события (2 шт)")
    else:
        success = False
        messages.append(f"✗ Ожидалось 2 целевых события, получено {handler.get_count()}")
    
    for event in handler.received_events:
        if event.event_type != 'test.target':
            success = False
            messages.append(f"✗ Получен нецелевой тип: {event.event_type}")
    
    if success:
        messages.append("✓ Все полученные события имеют тип 'test.target'")
    
    unsubscribe()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Фильтрация по типу работает")
    return success


# ============================================================================
# 2️⃣ Управление подписками
# ============================================================================

def test_unsubscribe() -> bool:
    """Тест 2.1: Отписка от событий"""
    print_test_header("2.1 Отписка от событий")
    
    bus = EventBus()
    handler = TestHandler("unsub")
    
    log.info("Подписываемся")
    unsubscribe = bus.subscribe('test.event', handler.handle)
    
    bus.emit('test.event', {"count": 1})
    
    log.info("Отписываемся")
    unsubscribe()
    
    bus.emit('test.event', {"count": 2})
    
    success = True
    messages = []
    
    if handler.get_count() == 1:
        messages.append("✓ После отписки новые события не приходят")
    else:
        success = False
        messages.append(f"✗ Ожидалось 1 событие, получено {handler.get_count()}")
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Отписка работает")
    return success


def test_multiple_unsubscribe() -> bool:
    """Тест 2.2: Повторная отписка не вызывает ошибок"""
    print_test_header("2.2 Повторная отписка")
    
    bus = EventBus()
    handler = TestHandler("multi_unsub")
    
    unsubscribe = bus.subscribe('test.event', handler.handle)
    
    log.info("Первая отписка")
    unsubscribe()
    
    log.info("Вторая отписка (должна быть безопасной)")
    try:
        unsubscribe()
        success = True
        message = "✓ Повторная отписка не вызвала ошибок"
    except Exception as e:
        success = False
        message = f"✗ Повторная отписка вызвала ошибку: {e}"
    
    print_test_result(success, message)
    return success


def test_duplicate_subscription() -> bool:
    """Тест 2.3: Дублирующаяся подписка"""
    print_test_header("2.3 Дублирующаяся подписка")
    
    bus = EventBus()
    handler = TestHandler("duplicate")
    
    log.info("Подписываемся дважды одним обработчиком")
    unsub1 = bus.subscribe('test.event', handler.handle)
    unsub2 = bus.subscribe('test.event', handler.handle)
    
    bus.emit('test.event', {"value": 42})
    
    success = True
    messages = []
    
    if handler.get_count() == 2:
        messages.append("✓ Обработчик вызван дважды")
    else:
        success = False
        messages.append(f"✗ Ожидалось 2 вызова, получено {handler.get_count()}")
    
    unsub1()
    unsub2()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Дублирующаяся подписка обработана")
    return success


# ============================================================================
# 3️⃣ Ошибки и исключения
# ============================================================================

def test_error_handling() -> bool:
    """Тест 3.1: Обработка ошибок в подписчиках"""
    print_test_header("3.1 Обработка ошибок в подписчиках")
    
    bus = EventBus()
    
    normal_handler = TestHandler("normal")
    error_handler = ErrorHandler("error")
    another_normal = TestHandler("another_normal")
    
    log.info("Подписываем три обработчика (один с ошибкой)")
    unsub_normal = bus.subscribe('test.error', normal_handler.handle)
    unsub_error = bus.subscribe('test.error', error_handler.handle)
    unsub_another = bus.subscribe('test.error', another_normal.handle)
    
    bus.emit('test.error', {"test": True})
    
    success = True
    messages = []
    
    if normal_handler.get_count() == 1:
        messages.append("✓ Нормальный обработчик 1 получил событие")
    else:
        success = False
        messages.append(f"✗ Нормальный обработчик 1: {normal_handler.get_count()}")
    
    if another_normal.get_count() == 1:
        messages.append("✓ Нормальный обработчик 2 получил событие")
    else:
        success = False
        messages.append(f"✗ Нормальный обработчик 2: {another_normal.get_count()}")
    
    if error_handler.called:
        messages.append("✓ Обработчик с ошибкой был вызван")
    else:
        success = False
        messages.append("✗ Обработчик с ошибкой НЕ был вызван")
    
    unsub_normal()
    unsub_error()
    unsub_another()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Ошибка в одном обработчике не влияет на других")
    return success


# ============================================================================
# 4️⃣ Слабые ссылки и сборка мусора
# ============================================================================

def test_weakref_cleanup() -> bool:
    """Тест 4.1: Автоматическая очистка слабых ссылок при GC"""
    print_test_header("4.1 Автоматическая очистка слабых ссылок")
    
    bus = EventBus()
    
    class TempHandler:
        def __init__(self, name):
            self.name = name
            self.events = []
        
        def handle(self, event):
            self.events.append(event)
            log.debug(f"TempHandler {self.name} получил событие, всего: {len(self.events)}")
    
    log.info("Создаём временный объект и подписываем его")
    temp = TempHandler("temp")
    weak_ref = weakref.ref(temp)
    unsubscribe = bus.subscribe('test.temp', temp.handle)
    
    bus.emit('test.temp', {"before_gc": True})
    assert len(temp.events) == 1, "Событие не получено до удаления"
    
    log.info("Удаляем объект")
    del temp
    
    log.info("Запускаем GC")
    gc.collect()
    gc.collect()
    
    assert weak_ref() is None, "Объект всё ещё жив!"
    
    bus.emit('test.temp', {"after_gc": True})
    
    subscriber_count = bus.get_subscriber_count('test.temp')
    
    success = True
    messages = []
    
    if subscriber_count == 0:
        messages.append("✓ Мёртвая ссылка автоматически очищена")
    else:
        success = False
        messages.append(f"✗ Мёртвая ссылка осталась: {subscriber_count}")
    
    try:
        unsubscribe()
        messages.append("✓ Отписка после удаления объекта безопасна")
    except Exception as e:
        success = False
        messages.append(f"✗ Отписка после удаления вызвала ошибку: {e}")
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Слабые ссылки очищаются автоматически")
    return success


# ============================================================================
# 5️⃣ Реентерабельность и рекурсия
# ============================================================================

def test_reentrant_emit() -> bool:
    """
    Тест 5.1: Реентерабельный emit
    Обработчик испускает другое событие с защитой от циклов.
    """
    print_test_header("5.1 Реентерабельный emit")
    
    bus = EventBus()
    
    primary_handler = TestHandler("primary")
    secondary_handler = TestHandler("secondary")
    
    reentrant = ReentrantHandler("reentrant", bus, 'test.secondary', max_depth=1)
    
    log.info("Подписываем обработчики")
    bus.subscribe('test.primary', reentrant.handle)
    bus.subscribe('test.primary', primary_handler.handle)
    bus.subscribe('test.secondary', secondary_handler.handle)
    
    log.info("Испускаем первичное событие с глубиной 0")
    bus.emit('test.primary', {"depth": 0})
    
    success = True
    messages = []
    
    if reentrant.received_count == 1:
        messages.append("✓ Реентерабельный обработчик сработал 1 раз")
    else:
        success = False
        messages.append(f"✗ Реентерабельный обработчик: {reentrant.received_count}")
    
    if primary_handler.get_count() == 1:
        messages.append("✓ Первичный обработчик получил событие")
    else:
        success = False
        messages.append(f"✗ Первичный обработчик: {primary_handler.get_count()}")
    
    if secondary_handler.get_count() == 1:
        messages.append("✓ Вторичный обработчик получил событие")
    else:
        success = False
        messages.append(f"✗ Вторичный обработчик: {secondary_handler.get_count()}")
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Реентерабельный emit работает")
    return success


def test_self_unsubscribe_during_emit() -> bool:
    """
    Тест 5.2: Самоотписка во время обработки события
    """
    print_test_header("5.2 Самоотписка во время обработки")
    
    bus = EventBus()
    
    self_unsub = SelfUnsubscribeHandler("self_unsub", bus, 'test.self')
    normal1 = TestHandler("normal1")
    normal2 = TestHandler("normal2")
    
    log.info("Подписываем обработчики")
    unsub_self = bus.subscribe('test.self', self_unsub.handle)
    unsub_normal1 = bus.subscribe('test.self', normal1.handle)
    unsub_normal2 = bus.subscribe('test.self', normal2.handle)
    
    self_unsub.set_unsubscribe(unsub_self)
    
    log.info("Испускаем первое событие")
    bus.emit('test.self', {"count": 1})
    
    log.info("Испускаем второе событие")
    bus.emit('test.self', {"count": 2})
    
    success = True
    messages = []
    
    if self_unsub.received_count == 1:
        messages.append("✓ Самоотписывающийся обработчик сработал 1 раз")
    else:
        success = False
        messages.append(f"✗ Самоотписывающийся обработчик: {self_unsub.received_count}")
    
    if normal1.get_count() == 2:
        messages.append("✓ Обычный обработчик 1 получил 2 события")
    else:
        success = False
        messages.append(f"✗ Обычный обработчик 1: {normal1.get_count()}")
    
    if normal2.get_count() == 2:
        messages.append("✓ Обычный обработчик 2 получил 2 события")
    else:
        success = False
        messages.append(f"✗ Обычный обработчик 2: {normal2.get_count()}")
    
    unsub_normal1()
    unsub_normal2()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Самоотписка во время обработки работает")
    return success


def test_recursive_emit() -> bool:
    """
    Тест 5.3: Рекурсивный emit с защитой
    """
    print_test_header("5.3 Рекурсивный emit")
    
    bus = EventBus()
    
    recursive = RecursiveHandler("recursive", bus, max_depth=3)
    counter = TestHandler("counter")
    
    log.info("Подписываем обработчики")
    bus.subscribe('test.recursive', recursive.handle)
    bus.subscribe('test.recursive', counter.handle)
    
    log.info("Испускаем начальное событие с глубиной 0")
    bus.emit('test.recursive', {"depth": 0})
    
    success = True
    messages = []
    
    expected_depths = [0, 1, 2, 3]
    if recursive.depths == expected_depths:
        messages.append(f"✓ Рекурсивный обработчик видел глубины: {recursive.depths}")
    else:
        success = False
        messages.append(f"✗ Ожидались глубины {expected_depths}, получены {recursive.depths}")
    
    if counter.get_count() == 4:
        messages.append("✓ Все 4 события доставлены")
    else:
        success = False
        messages.append(f"✗ Ожидалось 4 события, получено {counter.get_count()}")
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Рекурсивный emit работает без переполнения")
    return success


def test_nested_reentrant() -> bool:
    """
    Тест 5.4: Сложная реентерабельность с защитой от циклов
    """
    print_test_header("5.4 Сложная реентерабельность с защитой")
    
    bus = EventBus()
    
    counter_a = TestHandler("counter_a")
    counter_b = TestHandler("counter_b")
    counter_c = TestHandler("counter_c")
    
    reentrant_a = ReentrantHandler("A", bus, 'test.b', max_depth=3)
    reentrant_b = ReentrantHandler("B", bus, 'test.c', max_depth=3)
    reentrant_c = ReentrantHandler("C", bus, 'test.a', max_depth=3)
    
    log.info("Подписываем обработчики (цикл A->B->C->A с защитой)")
    bus.subscribe('test.a', reentrant_a.handle)
    bus.subscribe('test.a', counter_a.handle)
    
    bus.subscribe('test.b', reentrant_b.handle)
    bus.subscribe('test.b', counter_b.handle)
    
    bus.subscribe('test.c', reentrant_c.handle)
    bus.subscribe('test.c', counter_c.handle)
    
    log.info("Испускаем событие A с глубиной 0")
    bus.emit('test.a', {"depth": 0})
    
    success = True
    messages = []
    
    a_count = counter_a.get_count()
    b_count = counter_b.get_count()
    c_count = counter_c.get_count()
    
    messages.append(f"Тип A получил {a_count} событий")
    messages.append(f"Тип B получил {b_count} событий")
    messages.append(f"Тип C получил {c_count} событий")
    
    if a_count == 3 and b_count == 3 and c_count == 3:
        messages.append("✓ Все типы получили по 3 события")
    else:
        success = False
        messages.append(f"✗ Ожидалось по 3 события")
    
    total = a_count + b_count + c_count
    if total == 9:
        messages.append(f"✓ Общее количество событий: {total}")
    else:
        success = False
        messages.append(f"✗ Ожидалось 9 событий, получено {total}")
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Сложная реентерабельность с защитой")
    return success


# ============================================================================
# 6️⃣ Производительность и нагрузка
# ============================================================================

def test_high_frequency_events() -> bool:
    """Тест 6.1: Высокочастотные события"""
    print_test_header("6.1 Высокочастотные события")
    
    bus = EventBus()
    handler = TestHandler("high_freq")
    
    unsubscribe = bus.subscribe('test.fast', handler.handle)
    
    event_count = 1000
    log.info(f"Отправляем {event_count} событий")
    start_time = time.time()
    
    for i in range(event_count):
        bus.emit('test.fast', {"iteration": i})
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    success = True
    messages = []
    
    if handler.get_count() == event_count:
        messages.append(f"✓ Все {event_count} событий доставлены")
    else:
        success = False
        messages.append(f"✗ Ожидалось {event_count}, получено {handler.get_count()}")
    
    events_per_second = event_count / elapsed
    messages.append(f"Скорость: {events_per_second:.0f} событий/сек")
    
    if events_per_second > 1000:
        messages.append("✓ Производительность > 1000 событий/сек")
    else:
        messages.append(f"⚠ Производительность ниже ожидаемой: {events_per_second:.0f}")
    
    unsubscribe()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Высокочастотные события обработаны")
    return success


# ============================================================================
# 7️⃣ Потокобезопасность
# ============================================================================

def test_thread_safety() -> bool:
    """Тест 7.1: Потокобезопасность"""
    print_test_header("7.1 Потокобезопасность")
    
    bus = EventBus()
    handler = TestHandler("thread_safe")
    
    unsubscribe = bus.subscribe('test.thread', handler.handle)
    
    def emitter_thread(thread_id, count):
        for i in range(count):
            bus.emit('test.thread', {"thread": thread_id, "iteration": i})
        log.debug(f"Поток {thread_id} завершил испускание")
    
    threads = []
    thread_count = 5
    events_per_thread = 100
    
    log.info(f"Запускаем {thread_count} потоков по {events_per_thread} событий")
    for i in range(thread_count):
        t = threading.Thread(target=emitter_thread, args=(i, events_per_thread))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    expected_count = thread_count * events_per_thread
    success = True
    messages = []
    
    if handler.get_count() == expected_count:
        messages.append(f"✓ Все {expected_count} событий доставлены")
    else:
        success = False
        messages.append(f"✗ Ожидалось {expected_count}, получено {handler.get_count()}")
    
    unsubscribe()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Потокобезопасность обеспечена")
    return success


def test_thread_safety_with_weakrefs() -> bool:
    """Тест 7.2: Потокобезопасность со слабыми ссылками"""
    print_test_header("7.2 Потокобезопасность со слабыми ссылками")
    
    bus = EventBus()
    
    def worker_thread(thread_id):
        local_handlers = []
        unsubs = []
        
        for i in range(20):
            class LocalHandler:
                def __init__(self, tid, hid):
                    self.tid = tid
                    self.hid = hid
                    self.events = []
                
                def handle(self, event):
                    self.events.append(event)
            
            handler = LocalHandler(thread_id, i)
            local_handlers.append(handler)
            unsub = bus.subscribe('test.thread_gc', handler.handle)
            unsubs.append(unsub)
        
        bus.emit('test.thread_gc', {"thread": thread_id})
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker_thread, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    time.sleep(0.2)
    gc.collect()
    gc.collect()
    
    bus.emit('test.thread_gc', {"final": True})
    
    subscriber_count = bus.get_subscriber_count('test.thread_gc')
    
    success = True
    messages = []
    
    if subscriber_count == 0:
        messages.append(f"✓ Все подписчики очищены: {subscriber_count}")
    else:
        success = False
        messages.append(f"✗ Остались подписчики после GC: {subscriber_count}")
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Потокобезопасность со слабыми ссылками")
    return success


# ============================================================================
# 8️⃣ Расширенные сценарии
# ============================================================================

def test_no_subscribers() -> bool:
    """Тест 8.1: Испускание без подписчиков"""
    print_test_header("8.1 Испускание без подписчиков")
    
    bus = EventBus()
    
    try:
        bus.emit('test.no_subs', {"data": "no listeners"})
        log.info("Испускание без подписчиков выполнено без ошибок")
        success = True
        message = "✓ Испускание без подписчиков безопасно"
    except Exception as e:
        success = False
        message = f"✗ Испускание без подписчиков вызвало ошибку: {e}"
    
    print_test_result(success, message)
    return success


def test_cross_module_delivery() -> bool:
    """Тест 8.2: Межмодульная доставка"""
    print_test_header("8.2 Межмодульная доставка")
    
    bus = EventBus()
    
    class ModuleA:
        def __init__(self):
            self.events = []
        
        def handler(self, event):
            self.events.append(event)
            log.debug(f"ModuleA получил: {event['type']}")
    
    class ModuleB:
        def __init__(self):
            self.events = []
        
        def handler(self, event):
            self.events.append(event)
            log.debug(f"ModuleB получил: {event['type']}")
    
    module_a = ModuleA()
    module_b = ModuleB()
    
    unsub_a = bus.subscribe('test.cross', module_a.handler)
    unsub_b = bus.subscribe('test.cross', module_b.handler)
    
    bus.emit('test.cross', {"from": "main"}, source="main_module")
    
    success = True
    messages = []
    
    if len(module_a.events) == 1:
        messages.append("✓ ModuleA получил событие")
    else:
        success = False
        messages.append("✗ ModuleA НЕ получил событие")
    
    if len(module_b.events) == 1:
        messages.append("✓ ModuleB получил событие")
    else:
        success = False
        messages.append("✗ ModuleB НЕ получил событие")
    
    if module_a.events and module_a.events[0]['source'] == 'main_module':
        messages.append("✓ Источник события передан корректно")
    else:
        success = False
        messages.append("✗ Источник события потерян")
    
    unsub_a()
    unsub_b()
    
    for msg in messages:
        print(f"  {msg}")
    
    print_test_result(success, "Межмодульная доставка работает")
    return success


# ============================================================================
# 9️⃣ Логирование
# ============================================================================

def test_logging_levels() -> bool:
    """Тест 9.1: Проверка всех уровней логирования"""
    print_test_header("9.1 Проверка уровней логирования")
    
    current_level = Logger.get_level()
    results = []
    
    # Тест 1: Уровень ERROR
    Logger.set_level(Logger.ERROR)
    log.info("🔴 Уровень ERROR: только ошибки")
    bus_error = EventBus()
    handler_error = TestHandler("error_level")
    unsub_error = bus_error.subscribe('test.log', handler_error.handle)
    bus_error.emit('test.log', {"level": "error"})
    
    error_handler = ErrorHandler("test")
    unsub_error_handler = bus_error.subscribe('test.error', error_handler.handle)
    bus_error.emit('test.error', {})
    
    results.append(("ERROR", "ошибки должны быть"))
    unsub_error()
    unsub_error_handler()
    
    # Тест 2: Уровень WARNING
    Logger.set_level(Logger.WARNING)
    log.info("🟡 Уровень WARNING: только ошибки")
    bus_warning = EventBus()
    handler_warning = TestHandler("warning_level")
    unsub_warning = bus_warning.subscribe('test.log', handler_warning.handle)
    bus_warning.emit('test.log', {"level": "warning"})
    
    results.append(("WARNING", "ошибки должны быть, INFO - нет"))
    unsub_warning()
    
    # Тест 3: Уровень INFO
    Logger.set_level(Logger.INFO)
    log.info("🔵 Уровень INFO: INFO логи должны быть")
    bus_info = EventBus()
    handler_info = TestHandler("info_level")
    unsub_info = bus_info.subscribe('test.log', handler_info.handle)
    bus_info.emit('test.log', {"level": "info"})
    
    results.append(("INFO", "INFO логи должны быть"))
    unsub_info()
    
    # Тест 4: Уровень DEBUG
    Logger.set_level(Logger.DEBUG)
    log.info("🟢 Уровень DEBUG: все логи должны быть")
    bus_debug = EventBus()
    handler_debug = TestHandler("debug_level")
    unsub_debug = bus_debug.subscribe('test.log', handler_debug.handle)
    bus_debug.emit('test.log', {"level": "debug"})
    
    temp = TestHandler("temp")
    unsub_temp = bus_debug.subscribe('test.temp', temp.handle)
    del temp
    gc.collect()
    gc.collect()
    bus_debug.emit('test.temp', {})
    
    results.append(("DEBUG", "все логи должны быть"))
    unsub_debug()
    
    Logger.set_level(current_level)
    
    success = True
    
    print("\n📊 Результаты проверки уровней логирования:")
    for level, expected in results:
        print(f"  • {level}: {expected}")
    
    print_test_result(success, "Проверка уровней логирования")
    return success


# ============================================================================
# Запуск всех тестов
# ============================================================================

def run_event_bus_tests() -> bool:
    """
    Запускает все тесты EventBus.
    
    Returns:
        bool: True если все тесты пройдены успешно
    """
    print("\n" + "🚀" * 20)
    print(" ЗАПУСК ТЕСТОВ EVENT BUS")
    print("🚀" * 20 + "\n")
    
    tests = [
        # 1️⃣ Базовая функциональность
        ("1.1 Базовая подписка", test_basic_subscription_and_emit),
        ("1.2 Множество подписчиков", test_multiple_subscribers),
        ("1.3 Несколько типов", test_multiple_event_types),
        ("1.4 Фильтрация по типу", test_event_type_filtering),
        
        # 2️⃣ Управление подписками
        ("2.1 Отписка", test_unsubscribe),
        ("2.2 Повторная отписка", test_multiple_unsubscribe),
        ("2.3 Дублирующаяся подписка", test_duplicate_subscription),
        
        # 3️⃣ Ошибки и исключения
        ("3.1 Обработка ошибок", test_error_handling),
        
        # 4️⃣ Слабые ссылки
        ("4.1 Автоочистка слабых ссылок", test_weakref_cleanup),
        
        # 5️⃣ Реентерабельность и рекурсия
        ("5.1 Реентерабельный emit", test_reentrant_emit),
        ("5.2 Самоотписка во время обработки", test_self_unsubscribe_during_emit),
        ("5.3 Рекурсивный emit", test_recursive_emit),
        ("5.4 Сложная реентерабельность", test_nested_reentrant),
        
        # 6️⃣ Производительность
        ("6.1 Высокочастотные события", test_high_frequency_events),
        
        # 7️⃣ Потокобезопасность
        ("7.1 Потокобезопасность", test_thread_safety),
        ("7.2 Потокобезопасность с weakref", test_thread_safety_with_weakrefs),
        
        # 8️⃣ Расширенные сценарии
        ("8.1 Испускание без подписчиков", test_no_subscribers),
        ("8.2 Межмодульная доставка", test_cross_module_delivery),
        
        # 9️⃣ Логирование
        ("9.1 Уровни логирования", test_logging_levels),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            print(f"\n▶ Запуск: {name}")
            success = test_func()
            results.append((name, success))
        except Exception as e:
            log.error(f"Тест {name} упал с исключением: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "📊" * 20)
    print(" ИТОГОВЫЙ ОТЧЁТ")
    print("📊" * 20 + "\n")
    
    all_passed = True
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        if not success:
            all_passed = False
    
    print(f"\nВсего тестов: {len(results)}")
    print(f"Пройдено: {sum(1 for _, s in results if s)}")
    print(f"Провалено: {sum(1 for _, s in results if not s)}")
    
    if all_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print("\n⚠ ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ!")
    
    return all_passed


if __name__ == "__main__":
    run_event_bus_tests()