# test_import.py
"""Проверка всех импортов"""

print("1. Импорт dataclass...")
from dataclasses import dataclass
print("✓ OK")

print("\n2. Импорт core.models...")
from utils.Tester.core.models import TestFunction, TestNode
print("✓ OK")

print("\n3. Импорт core.discovery...")
from utils.Tester.core.discovery import TestDiscovery
print("✓ OK")

print("\n4. Импорт core.runner...")
from utils.Tester.core.runner import TestRunner, TestResult
print("✓ OK")

print("\n5. Импорт core.executor...")
from utils.Tester.core.executor import TestExecutor, ProgressInfo
print("✓ OK")

print("\n6. Импорт ui.reporter...")
from utils.Tester.ui.reporter import TestReporter
print("✓ OK")

print("\n7. Импорт ui.menu...")
from utils.Tester.ui.menu import TestMenu
print("✓ OK")

print("\n8. Импорт utils.isolation...")
from utils.Tester.utils.isolation import reset_environment
print("✓ OK")

print("\n9. Импорт utils.helpers...")
from utils.Tester.utils.helpers import get_version
print("✓ OK")

print(f"\n✅ Все импорты работают! Версия: {get_version()}")