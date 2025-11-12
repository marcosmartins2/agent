# Script de inicialização rápida para o SaaS Agentes

Write-Host "🤖 SaaS Agentes de IA - Setup Rápido" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

# Ativar venv
Write-Host "✓ Ativando ambiente virtual..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Verificar se o superusuário existe
Write-Host "`n📋 Verificando configuração..." -ForegroundColor Yellow

$dbExists = Test-Path "db.sqlite3"
if (-not $dbExists) {
    Write-Host "❌ Banco de dados não encontrado!" -ForegroundColor Red
    Write-Host "Execute: python manage.py migrate" -ForegroundColor Yellow
    exit
}

Write-Host "✓ Banco de dados OK" -ForegroundColor Green

# Perguntar se quer criar superusuário
Write-Host "`n🔐 Criar superusuário?" -ForegroundColor Cyan
$createUser = Read-Host "Já criou o superusuário? (s/n)"

if ($createUser -eq "n") {
    Write-Host "`n📝 Criando superusuário..." -ForegroundColor Yellow
    python manage.py createsuperuser
}

# Iniciar servidor
Write-Host "`n🚀 Iniciando servidor Django..." -ForegroundColor Green
Write-Host "📍 Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🔑 Login: http://localhost:8000/accounts/login/`n" -ForegroundColor Cyan

python manage.py runserver
