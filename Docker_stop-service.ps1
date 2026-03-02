# stop-service.ps1
# =============================================================================
# Скрипт для остановки отдельного сервиса
# Использование: .\stop-service.ps1 backend
#              .\stop-service.ps1 client
#              .\stop-service.ps1 all (остановить всё)
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Service
)

Write-Host ""
Write-Host "Остановка сервиса: $Service" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor DarkGray

switch ($Service.ToLower()) {
    "backend" {
        Write-Host "Останавливаем backend..." -ForegroundColor Yellow
        docker-compose stop backend
        docker-compose rm -f backend
        Write-Host "✅ Backend остановлен" -ForegroundColor Green
    }
    "client" {
        Write-Host "Останавливаем client..." -ForegroundColor Yellow
        docker-compose stop client
        docker-compose rm -f client
        Write-Host "✅ Client остановлен" -ForegroundColor Green
    }
    "all" {
        Write-Host "Останавливаем все сервисы..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "✅ Все сервисы остановлены" -ForegroundColor Green
    }
    default {
        Write-Host "❌ Неизвестный сервис: $Service" -ForegroundColor Red
        Write-Host "Доступные сервисы: backend, client, all" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..." -ForegroundColor DarkGray
Pause