#!/usr/bin/env python3
"""
Вспомогательный скрипт для ручного тестирования прерываний.
Запускает тесты и отправляет сигнал через указанное время.
"""

import subprocess
import time
import signal
import sys
import os


def run_tests_with_interrupt(delay=2):
    """
    Запускает тесты и отправляет SIGINT через delay секунд.
    """
    print(f"🚀 Запуск тестов с прерыванием через {delay}с...")
    
    # Запускаем тесты в отдельном процессе
    cmd = [sys.executable, "run_tests.py", "--headless", "--pattern", "test_control*"]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Ждем указанное время
    print(f"⏳ Ожидание {delay}с перед отправкой сигнала...")
    time.sleep(delay)
    
    # Отправляем SIGINT (Ctrl+C)
    print(f"📢 Отправка сигнала SIGINT процессу {process.pid}")
    if os.name == 'nt':  # Windows
        process.terminate()  # На Windows Ctrl+C сложнее
    else:  # Unix
        process.send_signal(signal.SIGINT)
    
    # Ждем завершения
    stdout, stderr = process.communicate(timeout=5)
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ТЕСТА С ПРЕРЫВАНИЕМ")
    print("="*60)
    print(stdout)
    if stderr:
        print("ОШИБКИ:")
        print(stderr)
    
    print(f"\nКод возврата: {process.returncode}")
    
    return process.returncode


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=2.0,
                       help="Задержка перед отправкой сигнала (секунды)")
    args = parser.parse_args()
    
    sys.exit(run_tests_with_interrupt(args.delay))