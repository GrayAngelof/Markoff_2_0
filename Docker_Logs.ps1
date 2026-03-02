# logs.ps1
# =============================================================================
# Скрипт для просмотра логов сервиса
# Использование: .\logs.ps1 backend
#              .\logs.ps1 client
#              .\logs.ps1 backend -f (следить за логами)
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Service,
    [switch]$f
)

Write-Host ""
Write-Host "Логи сервиса: $Service" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor DarkGray

if ($f) {
    # Режим следования за логами
    docker-compose logs -f $Service
} else {
    # Показать последние логи и выйти
    docker-compose logs --tail=50 $Service
}

# Если не в режиме следования, ждем нажатия клавиши
if (-not $f) {
    Write-Host ""
    Write-Host "Нажмите любую клавишу для выхода..." -ForegroundColor DarkGray
    Pause
}