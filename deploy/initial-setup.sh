#!/bin/bash

# Script de setup inicial da VPS
# Execute APENAS UMA VEZ na primeira configuração

echo "🚀 Setup inicial da VPS para Pandia"

# Atualizar sistema
echo "📦 Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependências
echo "📥 Instalando dependências..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nginx \
    git \
    postgresql \
    postgresql-contrib \
    supervisor \
    certbot \
    python3-certbot-nginx

# Criar usuário
echo "👤 Criando usuário pandia..."
sudo adduser pandia --disabled-password --gecos ""
sudo usermod -aG sudo pandia

# Configurar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
read -p "Digite a senha para o banco de dados: " DB_PASSWORD

sudo -u postgres psql <<EOF
CREATE DATABASE pandia_db;
CREATE USER pandia_user WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE pandia_user SET client_encoding TO 'utf8';
ALTER ROLE pandia_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pandia_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE pandia_db TO pandia_user;
\q
EOF

# Configurar firewall
echo "🔒 Configurando firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "✅ Setup inicial concluído!"
echo ""
echo "Próximos passos:"
echo "1. sudo su - pandia"
echo "2. Clonar o projeto no diretório /home/pandia/pandia"
echo "3. Seguir o DEPLOY_GUIDE.md a partir do passo 5"
