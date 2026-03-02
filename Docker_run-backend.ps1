# run-backend.ps1
# =============================================================================
# Скрипт для запуска только backend-сервиса через docker-compose
# Запускается из корня проекта (E:\Projects\Markoff_2.0)
# =============================================================================

Write-Host ""
Write-Host "Запуск Markoff Backend (FastAPI) через Docker Compose" -ForegroundColor Cyan
Write-Host "Образ: markoff-backend:dev" -ForegroundColor DarkGray
Write-Host "----------------------------------------" -ForegroundColor DarkGray

# -----------------------------------------------------------------------------
# 1. Проверка наличия образа
# -----------------------------------------------------------------------------
$imageExists = docker images -q markoff-backend:dev
if (-not $imageExists) {
    Write-Host "ОШИБКА: Образ markoff-backend:dev не найден!" -ForegroundColor Red
    Write-Host "Сначала выполните build-backend.ps1" -ForegroundColor Yellow
    Pause
    exit 1
}

# -----------------------------------------------------------------------------
# 2. Проверка, не запущен ли уже контейнер
# -----------------------------------------------------------------------------
$running = docker ps --filter "name=markoff-backend" --filter "status=running" -q
if ($running) {
    Write-Host "⚠️ Backend уже запущен. Останавливаем..." -ForegroundColor Yellow
    docker-compose stop backend
    docker-compose rm -f backend
}

# -----------------------------------------------------------------------------
# 3. Запуск backend через docker-compose
# -----------------------------------------------------------------------------
Write-Host "Запускаем backend через docker-compose..." -ForegroundColor Yellow

# Запускаем только backend сервис в фоновом режиме
docker-compose up -d backend

# -----------------------------------------------------------------------------
# 4. Проверка результата и ожидание готовности
# -----------------------------------------------------------------------------
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "УСПЕХ! Backend запускается..." -ForegroundColor Green
    
    # Ждем, пока backend полностью загрузится
    Write-Host "Ожидаем готовности backend..." -ForegroundColor Yellow
    $maxAttempts = 30
    $attempt = 0
    $ready = $false
    
    while ($attempt -lt $maxAttempts -and -not $ready) {
        Start-Sleep -Seconds 1
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 1
            if ($response.StatusCode -eq 200) {
                $ready = $true
                Write-Host "✅ Backend готов к работе!" -ForegroundColor Green
            }
        } catch {
            # Игнорируем ошибки, просто продолжаем ждать
        }
        $attempt++
    }
    
    if (-not $ready) {
        Write-Host "⚠️ Backend запущен, но не отвечает на health check. Проверьте логи:" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Доступные адреса:" -ForegroundColor Cyan
    Write-Host "  • Swagger UI:     http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  • Root:            http://localhost:8000/" -ForegroundColor White
    Write-Host "  • Health:          http://localhost:8000/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Логи в реальном времени: docker-compose logs -f backend" -ForegroundColor DarkGray
    Write-Host "Остановить backend:       docker-compose stop backend" -ForegroundColor DarkGray
    Write-Host "Перезапустить backend:    docker-compose restart backend" -ForegroundColor DarkGray
} else {
    Write-Host ""
    Write-Host "ОШИБКА ЗАПУСКА" -ForegroundColor Red
    Write-Host "Код: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Проверьте логи: docker-compose logs backend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..." -ForegroundColor DarkGray
Pause