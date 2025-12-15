#!/bin/bash

# Script de deploy para atualização rápida
# Execute na VPS: bash deploy.sh

echo "🚀 Iniciando deploy..."

# Ir para o diretório do projeto
cd /home/pandia/pandia || exit

# Ativar ambiente virtual
source venv/bin/activate

# Puxar últimas mudanças (se usando Git)
echo "📥 Puxando código..."
git pull origin main

# Instalar/atualizar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Executar migrações
echo "🗄️ Rodando migrações..."
python manage.py migrate

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Reiniciar Gunicorn
echo "🔄 Reiniciando Gunicorn..."
sudo systemctl restart gunicorn

# Verificar status
echo "✅ Verificando status..."
sudo systemctl status gunicorn --no-pager

echo "🎉 Deploy concluído!"
