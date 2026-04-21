Краткое описание слоя
Назначение – обрабатывать пользовательские действия и события, координировать работу сервисов (services) и проекций (projections), управлять состоянием приложения (выбранный узел, раскрытые узлы). Контроллеры не содержат бизнес-логики (она в services) и не работают напрямую с UI (только через события).

Что делает:

Подписывается на события от UI (например, NodeSelected, RefreshRequested)

Управляет состоянием: текущий выбор, раскрытые узлы, статус соединения

Инициирует загрузку данных через DataLoader (сервис)

Преобразует сырые данные в узлы дерева через TreeProjection

Эмитит события для UI (ChildrenLoaded, NodeDetailsLoaded, ExpandedNodesChanged)

Централизованно обрабатывает ошибки и логирует

Что не должен делать:

Импортировать что-либо из ui (теперь это соблюдено)

Содержать логику отображения виджетов

Напрямую обращаться к БД или API (это задача data)

Содержать бизнес-правила, специфичные для предметной области (они в services)

Файловая структура слоя
text
client/src/controllers/
├── __init__.py                    # Публичное API: экспорт всех контроллеров
├── base.py                        # BaseController (подписка/отписка, ошибки)
├── connection_controller.py       # ConnectionController (статус соединения)
├── details_controller.py          # DetailsController (выбор узла, загрузка деталей)
├── refresh_controller.py          # RefreshController (обновление данных: current/visible/full)
└── tree_controller.py             # TreeController (раскрытие узлов, загрузка детей)
Внутренние классы (кратко)
Класс	Файл	Назначение
BaseController	base.py	Абстрактный базовый класс: автоматическая подписка/отписка, централизованная эмиссия ошибок, управление жизненным циклом.
ConnectionController	connection_controller.py	Отслеживает статус соединения с сервером, эмитит ConnectionChanged, хранит текущий статус.
DetailsController	details_controller.py	Хранит текущий выбранный узел (единственный источник правды), эмитит CurrentSelectionChanged, загружает детали через DataLoader и отправляет NodeDetailsLoaded. Не имеет прямой ссылки на UI.
RefreshController	refresh_controller.py	Обрабатывает запросы на обновление (RefreshRequested), поддерживает три режима (current/visible/full), управляет очисткой кэша и сворачиванием дерева.
TreeController	tree_controller.py	Хранит множество раскрытых узлов, загружает детей через DataLoader при раскрытии, эмитит ChildrenLoaded и ExpandedNodesChanged.
Внутренние импорты (только между модулями проекта)
Игнорируем utils.logger и стандартные библиотеки. Перечислены импорты из src.* (внутренние).

Из base.py:

from src.core import EventBus

from src.core.events.definitions import DataError

from src.core.types import EventData, NodeIdentifier

Из connection_controller.py:

from src.core import EventBus

from src.core.events.definitions import ConnectionChanged

from src.controllers.base import BaseController

Из details_controller.py (исправленная версия):

from src.core import EventBus

from src.core.events.definitions import CurrentSelectionChanged, NodeDetailsLoaded, NodeSelected

from src.core.types.nodes import NodeIdentifier

from src.controllers.base import BaseController

from src.services.data_loader import DataLoader

Из refresh_controller.py:

from src.core import EventBus

from src.core.events.definitions import CollapseAllRequested, CurrentSelectionChanged, ExpandedNodesChanged, RefreshRequested

from src.core.types import NodeIdentifier

from src.controllers.base import BaseController

from src.services import DataLoader

Из tree_controller.py:

from src.core import EventBus

from src.core.events.definitions import ChildrenLoaded, CollapseAllRequested, DataLoaded, DataLoadedKind, ExpandedNodesChanged, NodeCollapsed, NodeExpanded, NodeSelected

from src.core.types import NodeIdentifier, NodeType, ROOT_NODE

from src.controllers.base import BaseController

from src.projections.tree import TreeProjection

from src.services import DataLoader

Экспортируемые методы / классы для вышестоящих слоёв (ui)
Через controllers/__init__.py экспортируются:

Классы:

BaseController (для создания собственных контроллеров, если нужно)

TreeController

DetailsController

RefreshController

ConnectionController

Основные публичные методы (используются из ui или bootstrap):

Контроллер	Метод	Назначение
TreeController	load_root_nodes()	Загружает корневые узлы (комплексы) при старте.
ConnectionController	is_online() -> Optional[bool]	Возвращает текущий статус соединения.
ConnectionController	is_initialized() -> bool	Проверяет, получен ли первый статус.
BaseController (у всех)	cleanup()	Отписывается от событий, освобождает ресурсы (вызывается при закрытии).
События, которые эмитят контроллеры (для подписки UI):

ChildrenLoaded (от TreeController)

ExpandedNodesChanged (от TreeController)

CurrentSelectionChanged (от DetailsController)

NodeDetailsLoaded (от DetailsController)

Итоговое заключение: принципы работы со слоем controllers
Импорт только сверху вниз – контроллеры могут импортировать из core, services, projections, но не должны импортировать из ui.
✅ Исправлено: details_controller.py больше не импортирует DetailsPanel. Все контроллеры теперь соответствуют правилу.

Контроллеры не создают UI – они только эмитят события, на которые подписываются UI-обработчики (например, ChildrenLoaded → TreeModel обновляет данные).

Состояние хранится только в контроллерах – _current_selection в DetailsController, _expanded_nodes в TreeController. Это единственные источники правды.

Все контроллеры наследуются от BaseController – это обеспечивает автоматическую отписку при cleanup() и единообразную обработку ошибок через _emit_error().

Загрузка данных всегда через DataLoader – контроллеры никогда не обращаются к репозиториям напрямую. Это позволяет кэшировать и переиспользовать данные.

Проекции используются только для преобразования – TreeProjection.build_children_from_payload() превращает сырые DTO в узлы дерева. Контроллеры не занимаются форматированием.

Жизненный цикл – при создании контроллера он подписывается на нужные события. При завершении приложения вызывается cleanup() для отписки. UI должен явно вызывать cleanup() у всех контроллеров.

Режимы обновления – RefreshController поддерживает три режима, используя состояние от других контроллеров (через события). Это пример координации без прямой связанности.

Текущее состояние: слой controllers полностью соответствует архитектурному принципу «строгая зависимость слоёв только сверху вниз» и не содержит нарушений.