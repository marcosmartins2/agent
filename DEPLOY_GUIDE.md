# 🚀 Guia de Deploy - VPS

## 📋 Pré-requisitos

- VPS com Ubuntu 22.04 LTS ou superior
- Acesso SSH à VPS
- Domínio apontado para o IP da VPS
- Mínimo 1GB RAM recomendado

---

## 1️⃣ Preparar Ambiente Local

### 1.1 Criar arquivo .gitignore
```bash
# Se ainda não tiver
echo "db.sqlite3
*.pyc
__pycache__/
.env
staticfiles/
media/
.venv/" > .gitignore
```

### 1.2 Commitar código (se usando Git)
```bash
git add .
git commit -m "Preparando deploy"
git push origin main
```

---

## 2️⃣ Configurar VPS

### 2.1 Conectar via SSH
```bash
ssh root@SEU_IP_VPS
```

### 2.2 Atualizar sistema
```bash
apt update && apt upgrade -y
```

### 2.3 Instalar dependências
```bash
apt install python3.11 python3.11-venv python3-pip nginx git postgresql postgresql-contrib supervisor -y
```

### 2.4 Criar usuário para a aplicação
```bash
adduser pandia
usermod -aG sudo pandia
su - pandia
```

---

## 3️⃣ Configurar PostgreSQL

### 3.1 Criar banco de dados
```bash
# Voltar para o usuário root primeiro (se estiver como pandia)
exit  # Se estiver como pandia

# Executar do diretório /tmp para evitar permissões
cd /tmp
sudo -u postgres psql
```

No PostgreSQL:
```sql
CREATE DATABASE pandia_db;
CREATE USER pandia_user WITH PASSWORD 'SUA_SENHA_FORTE_AQUI';
ALTER ROLE pandia_user SET client_encoding TO 'utf8';
ALTER ROLE pandia_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pandia_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE pandia_db TO pandia_user;
\q
```

**Alternativa (criar tudo em um comando):**
```bash
sudo -u postgres psql -c "CREATE DATABASE pandia_db;"
sudo -u postgres psql -c "CREATE USER pandia_user WITH PASSWORD 'SUA_SENHA_FORTE_AQUI';"
sudo -u postgres psql -c "ALTER ROLE pandia_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE pandia_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE pandia_user SET timezone TO 'America/Sao_Paulo';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pandia_db TO pandia_user;"
```

---

## 4️⃣ Clonar Projeto

### 4.1 Clonar via Git (recomendado)
```bash
cd /home/pandia
git clone https://github.com/SEU_USUARIO/SEU_REPO.git pandia
cd pandia
```

### 4.2 OU: Transferir via SCP (do seu PC local)
```bash
# No seu PC Windows (PowerShell)
scp -r C:\Users\marco\Documents\Projects\Pandia\agent pandia@SEU_IP_VPS:/home/pandia/pandia
```

---

## 5️⃣ Configurar Ambiente Python

### 5.1 Criar virtual environment
```bash
cd /home/pandia/pandia
python3.11 -m venv venv
source venv/bin/activate
```

### 5.2 Instalar dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install psycopg2-binary  # Driver PostgreSQL
```

---

## 6️⃣ Configurar Variáveis de Ambiente

### 6.1 Criar arquivo .env
```bash
nano /home/pandia/pandia/.env
```

Cole o conteúdo (ajuste os valores):
```env
DEBUG=0
SECRET_KEY=gqclws)y_!6)!)=eh#v(uv-dk-t08##7k7*vf(!(600rm^4%7&
ALLOWED_HOSTS=31.97.95.233
CSRF_TRUSTED_ORIGINS=http://31.97.95.233
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pandia_db
DB_USER=pandia_user
DB_PASSWORD=pandiaadmin
DB_HOST=localhost
DB_PORT=5432
```

### 6.2 Gerar SECRET_KEY
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## 7️⃣ Migrar Banco de Dados

```bash
cd /home/pandia/pandia
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

---

## 8️⃣ Configurar Gunicorn

### 8.1 Testar Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```
Se funcionar, pressione Ctrl+C e continue.

### 8.2 Criar arquivo de serviço systemd
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Cole:
```ini
[Unit]
Description=Gunicorn daemon for Pandia
After=network.target

[Service]
User=pandia
Group=www-data
WorkingDirectory=/home/pandia/pandia
Environment="PATH=/home/pandia/pandia/venv/bin"
ExecStart=/home/pandia/pandia/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/pandia/pandia/gunicorn.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 8.3 Ativar serviço
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

---

## 9️⃣ Configurar Nginx

### 9.1 Criar configuração do site
```bash
sudo nano /etc/nginx/sites-available/pandia
```

Cole:
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/pandia/pandia/staticfiles/;
    }

    location /media/ {
        alias /home/pandia/pandia/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/pandia/pandia/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

### 9.2 Ativar site
```bash
sudo ln -s /etc/nginx/sites-available/pandia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9.3 Ajustar permissões
```bash
sudo usermod -aG pandia www-data
sudo chmod 710 /home/pandia
sudo chmod 755 /home/pandia/pandia
```

---

## 🔟 Configurar SSL (HTTPS com Let's Encrypt)

### 10.1 Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 10.2 Obter certificado
```bash
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

### 10.3 Auto-renovação
```bash
sudo certbot renew --dry-run
```

---

## 1️⃣1️⃣ Verificações Finais

### 11.1 Verificar serviços
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### 11.2 Ver logs
```bash
# Gunicorn
sudo journalctl -u gunicorn -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### 11.3 Testar aplicação
Acesse: `https://seu-dominio.com`

---

## 🔄 Deploy de Atualizações

Quando fizer mudanças no código:

```bash
# Conectar na VPS
ssh pandia@SEU_IP_VPS

# Ir para o diretório
cd /home/pandia/pandia

# Ativar ambiente virtual
source venv/bin/activate

# Puxar código (se usando Git)
git pull origin main

# Instalar novas dependências
pip install -r requirements.txt

# Rodar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Reiniciar Gunicorn
sudo systemctl restart gunicorn

# Verificar status
sudo systemctl status gunicorn
```

---

## 🛠️ Comandos Úteis

### Reiniciar serviços
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Ver logs em tempo real
```bash
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

### Backup do banco de dados
```bash
sudo -u postgres pg_dump pandia_db > backup_$(date +%Y%m%d).sql
```

### Restaurar backup
```bash
sudo -u postgres psql pandia_db < backup_20251215.sql
```

---

## 🔒 Segurança Adicional

### Firewall
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

### Fail2ban (proteção contra brute force)
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## ⚠️ Troubleshooting

### Erro 502 Bad Gateway
- Verificar se Gunicorn está rodando: `sudo systemctl status gunicorn`
- Verificar logs: `sudo journalctl -u gunicorn -f`

### Arquivos estáticos não carregam
- Verificar permissões: `ls -la /home/pandia/pandia/staticfiles/`
- Rodar novamente: `python manage.py collectstatic --noinput`

### Erro de conexão ao banco
- Verificar PostgreSQL: `sudo systemctl status postgresql`
- Verificar credenciais no arquivo `.env`

---

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs do Gunicorn e Nginx
2. Teste manualmente o Gunicorn
3. Verifique as configurações do `.env`
4. Certifique-se que o PostgreSQL está rodando
