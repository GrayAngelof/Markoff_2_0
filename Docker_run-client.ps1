# run-client.ps1
# =============================================================================
# Скрипт для запуска только client-сервиса через docker-compose
# Запускается из корня проекта (E:\Projects\Markoff_2.0)
# =============================================================================

Write-Host ""
Write-Host "Запуск Markoff Desktop Client через Docker Compose" -ForegroundColor Cyan
Write-Host "Образ: markoff-client:dev" -ForegroundColor DarkGray
Write-Host "----------------------------------------" -ForegroundColor DarkGray

# -----------------------------------------------------------------------------
# 1. Проверка наличия образа
# -----------------------------------------------------------------------------
$imageExists = docker images -q markoff-client:dev
if (-not $imageExists) {
    Write-Host "ОШИБКА: Образ markoff-client:dev не найден!" -ForegroundColor Red
    Write-Host "Сначала выполните build-client.ps1" -ForegroundColor Yellow
    Pause
    exit 1
}

# -----------------------------------------------------------------------------
# 2. Проверка VcXsrv
# -----------------------------------------------------------------------------
Write-Host "Проверяем наличие X-сервера (VcXsrv)..." -ForegroundColor Yellow
$vcxsrv = Get-Process | Where-Object {$_.ProcessName -like "*vcxsrv*" -or $_.ProcessName -like "*Xming*"}

if (-not $vcxsrv) {
    Write-Host "⚠️ VcXsrv/Xming не запущен!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Запусти VcXsrv с параметрами:" -ForegroundColor Yellow
    Write-Host '  "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac' -ForegroundColor White
    Write-Host ""
    Write-Host "Или используй XLaunch с настройками:" -ForegroundColor Yellow
    Write-Host "  • Multiple windows" -ForegroundColor White
    Write-Host "  • Display number: -1" -ForegroundColor White
    Write-Host "  • Start no client" -ForegroundColor White
    Write-Host "  • Отключи контроль доступа (Disable access control)" -ForegroundColor White
    Write-Host ""
    Write-Host "Продолжить всё равно? (Y/N)" -ForegroundColor Yellow
    $answer = Read-Host
    if ($answer -ne "Y" -and $answer -ne "y") {
        exit 0
    }
} else {
    Write-Host "✅ X-сервер запущен: $($vcxsrv[0].ProcessName)" -ForegroundColor Green
    
    # Проверяем порт
    $connection = Test-NetConnection -ComputerName localhost -Port 6000 -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($connection) {
        Write-Host "✅ Порт 6000 (X server) доступен" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Порт 6000 не отвечает. Возможно, X-сервер использует другой порт." -ForegroundColor Yellow
    }
}

# -----------------------------------------------------------------------------
# 3. Проверка, не запущен ли уже контейнер клиента
# -----------------------------------------------------------------------------
$running = docker ps --filter "name=markoff-client" --filter "status=running" -q
if ($running) {
    Write-Host "⚠️ Client уже запущен. Останавливаем..." -ForegroundColor Yellow
    docker-compose stop client
    docker-compose rm -f client
}

# -----------------------------------------------------------------------------
# 4. Запуск клиента через docker-compose
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "Запускаем клиент через docker-compose..." -ForegroundColor Yellow
Write-Host "(Для вывода логов в консоль используй -d для фонового режима)" -ForegroundColor DarkGray
Write-Host ""

# Спрашиваем, в каком режиме запускать
Write-Host "Выберите режим запуска:" -ForegroundColor Cyan
Write-Host "  1. Фоновый режим (контейнер работает в фоне)" -ForegroundColor White
Write-Host "  2. Режим с логами (контейнер привязан к консоли, Ctrl+C для остановки)" -ForegroundColor White
$mode = Read-Host "Выберите (1/2)"

if ($mode -eq "1") {
    # Фоновый режим
    Write-Host "Запускаем клиент в фоновом режиме..." -ForegroundColor Yellow
    docker-compose up -d client
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Клиент запущен в фоновом режиме!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Просмотр логов:    docker-compose logs -f client" -ForegroundColor Cyan
        Write-Host "Остановка:         docker-compose stop client" -ForegroundColor Cyan
        Write-Host "Перезапуск:        docker-compose restart client" -ForegroundColor Cyan
    }
} else {
    # Режим с логами (привязанный к консоли)
    Write-Host ""
    Write-Host "Запускаем клиент в режиме отладки (логи в консоли)..." -ForegroundColor Yellow
    Write-Host "Для остановки нажмите Ctrl+C" -ForegroundColor DarkGray
    Write-Host ""
    
    # Важно: не используем -d, чтобы видеть логи в реальном времени
    docker-compose up client
}

# -----------------------------------------------------------------------------
# 5. Проверка результата (только для фонового режима)
# -----------------------------------------------------------------------------
if ($mode -eq "1" -and $LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "УСПЕХ! Клиент запущен." -ForegroundColor Green
} elseif ($mode -eq "1" -and $LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ОШИБКА ЗАПУСКА" -ForegroundColor Red
    Write-Host "Код возврата: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Проверьте логи: docker-compose logs client" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..." -ForegroundColor DarkGray
Pause