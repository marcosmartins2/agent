# SaaS Agentes de IA - Manicure/Pedicure

Sistema completo em **Django puro** para gerenciar agentes de IA personalizados. O **n8n** busca configurações via API JSON e envia eventos via webhook.

## 🚀 Tecnologias

- **Python 3.11+**
- **Django 5.x**
- **SQLite** (dev e prod)
- **HTML/CSS puro** (sem frameworks JS)
- **Whitenoise** para arquivos estáticos

## 📦 Setup Rápido

### Windows (PowerShell)

```powershell
# 1. Criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 2. Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configurar .env
copy .env.example .env
# Edite .env e troque SECRET_KEY por uma chave aleatória

# 4. Criar projeto Django (se ainda não existe)
django-admin startproject config .

# 5. Criar apps
python manage.py startapp core
python manage.py startapp accounts
python manage.py startapp organizations
python manage.py startapp agents
python manage.py startapp integrations
python manage.py startapp webhooks
python manage.py startapp api
python manage.py startapp ui
python manage.py startapp audit

# 6. Aplicar migrações
python manage.py makemigrations
python manage.py migrate

# 7. Criar superusuário
python manage.py createsuperuser

# 8. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 9. Rodar servidor
python manage.py runserver
```

### Linux/Mac

```bash
# 1. Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configurar .env
cp .env.example .env
# Edite .env e troque SECRET_KEY por uma chave aleatória

# 4. Criar projeto Django (se ainda não existe)
django-admin startproject config .

# 5. Criar apps
python manage.py startapp core
python manage.py startapp accounts
python manage.py startapp organizations
python manage.py startapp agents
python manage.py startapp integrations
python manage.py startapp webhooks
python manage.py startapp api
python manage.py startapp ui
python manage.py startapp audit

# 6. Aplicar migrações
python manage.py makemigrations
python manage.py migrate

# 7. Criar superusuário
python manage.py createsuperuser

# 8. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 9. Rodar servidor
python manage.py runserver
```

## 🔑 Configuração de API Key

### 1. Criar Organização e API Key

1. Acesse: `http://localhost:8000/accounts/login/`
2. Faça login com as credenciais do superusuário
3. Vá para o Dashboard: `http://localhost:8000/`
4. Crie uma organização em: `http://localhost:8000/organizations/`
5. Gere uma API Key em: `http://localhost:8000/organizations/apikeys/`
6. **Copie a API Key gerada** (só será exibida uma vez)

## 📡 Endpoints para n8n

### GET - Buscar Configuração de Agente

```http
GET http://localhost:8000/api/n8n/agents/<slug-do-agente>/config?api_key=<SUA_API_KEY>
```

**Exemplo:**
```bash
curl "http://localhost:8000/api/n8n/agents/atendente-ana/config?api_key=sk_abc123xyz..."
```

**Resposta (JSON):**
```json
{
  "name": "Ana",
  "slug": "atendente-ana",
  "role": "atendente",
  "sector": "manicure/pedicure",
  "language": "pt-BR",
  "greeting": "Olá {{cliente_nome}}! Eu sou {{agente_nome}}...",
  "tone": "objetivo, simpático e claro",
  "style_guidelines": "Use linguagem simples...",
  "business_hours": {"mon": "09:00-18:00", "tue": "09:00-18:00"},
  "knowledge_base": "## Serviços\n...",
  "fallback_message": "Desculpe, não entendi...",
  "escalation_rule": "Se cliente solicitar gerente..."
}
```

### POST - Enviar Evento (Webhook)

```http
POST http://localhost:8000/webhooks/n8n/events?api_key=<SUA_API_KEY>
Content-Type: application/json

{
  "type": "message",
  "agent_slug": "atendente-ana",
  "session_id": "abc123",
  "payload": {
    "text": "Cliente pediu pedicure spa",
    "metadata": {"canal": "whatsapp"}
  }
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8000/webhooks/n8n/events?api_key=sk_abc123xyz..." \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "agent_slug": "atendente-ana",
    "session_id": "session_001",
    "payload": {
      "text": "Cliente quer agendar para amanhã",
      "metadata": {"canal": "whatsapp", "telefone": "+5511999999999"}
    }
  }'
```

**Resposta:**
```json
{"status": "ok"}
```

## 🧪 Roteiro de Teste Rápido

### 1. Acesso Inicial
```bash
# Rodar servidor
python manage.py runserver

# Acessar: http://localhost:8000/accounts/login/
# Login com superusuário criado
```

### 2. Criar Organização e API Key
1. Dashboard → Organizações → Criar nova
2. Nome: "Salão Unhas Fast"
3. API Keys → Gerar nova chave
4. **Copiar a chave exibida**

### 3. Criar Agente
1. Dashboard → Agentes → Criar novo
2. Preencher:
   - Nome: Ana
   - Slug: atendente-ana
   - Setor: manicure/pedicure
   - Usar valores padrão ou customizar
3. Testar no Playground

### 4. Testar API (n8n)
```bash
# Substituir <API_KEY> pela sua chave

# GET - Buscar config do agente
curl "http://localhost:8000/api/n8n/agents/atendente-ana/config?api_key=<API_KEY>"

# POST - Enviar evento
curl -X POST "http://localhost:8000/webhooks/n8n/events?api_key=<API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"type":"message","agent_slug":"atendente-ana","session_id":"test1","payload":{"text":"teste"}}'
```

### 5. Verificar Logs
1. Dashboard → Logs de Auditoria
2. Verificar evento registrado

## 🧩 Estrutura do Projeto

```
saas-agentes/
├─ .env                    # Configurações (não versionar)
├─ requirements.txt        # Dependências Python
├─ manage.py              # CLI Django
├─ config/                # Configurações do projeto
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ core/                  # Utils, middlewares
├─ accounts/              # Auth (login/logout)
├─ organizations/         # Organizações e API Keys
├─ agents/                # CRUD de Agentes + Playground
├─ integrations/          # Configs n8n
├─ api/                   # Endpoints JSON para n8n
├─ webhooks/              # Receber eventos do n8n
├─ ui/                    # Views e templates HTML
├─ audit/                 # Logs de auditoria
├─ templates/             # HTML templates
└─ static/                # CSS/JS/imagens
```

## 🎯 URLs Principais

| URL | Descrição |
|-----|-----------|
| `/` | Dashboard |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |
| `/accounts/register/` | Registro (opcional) |
| `/agents/` | Lista de agentes |
| `/agents/create/` | Criar agente |
| `/agents/<slug>/` | Editar agente |
| `/agents/<slug>/playground/` | Testar agente |
| `/organizations/` | Organizações |
| `/organizations/apikeys/` | Gerenciar API Keys |
| `/api/n8n/agents/<slug>/config` | API: Config do agente |
| `/webhooks/n8n/events` | Webhook: Receber eventos |
| `/admin/` | Django Admin |

## 🔒 Segurança

- **CSRF** habilitado (exceto webhook)
- **API Key** por organização
- **Rate limiting** simples em endpoints públicos
- **Logs de auditoria** para todas as ações

## 🚀 Deploy (Linux)

```bash
# 1. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 2. Rodar com Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Ou usar supervisor/systemd para manter rodando
```

## 🧪 Testes

```bash
# Rodar todos os testes
python manage.py test

# Rodar testes de um app específico
python manage.py test api
python manage.py test webhooks
python manage.py test agents
```

## 📝 Defaults de Domínio (Manicure/Pedicure)

### Greeting Padrão
```
Olá {{cliente_nome}}! Eu sou {{agente_nome}}, atendente da Unhas Fast 💅. Como posso te ajudar hoje?
```

### Tom Padrão
```
objetivo, simpático e claro
```

### Knowledge Base Inicial
```markdown
## Serviços Oferecidos
- Manicure básica (30min)
- Pedicure básica (45min)
- Manicure + Pedicure (1h15min)
- Spa de mãos (45min)
- Spa de pés (1h)
- Alongamento de unhas (1h30min)
- Nail art personalizada (30min adicional)

## Políticas
- Tolerância de atraso: 10 minutos
- Remarcação: até 24h de antecedência sem custo
- Cancelamento com menos de 24h: taxa de 50%

## Cuidados Pós-Atendimento
- Evitar água quente por 2h após esmaltação
- Usar luvas para limpeza pesada
- Hidratar cutículas diariamente
```

## 💡 Dicas

1. **Playground**: Use para testar como o agente responde antes de integrar com n8n
2. **Placeholders**: `{{cliente_nome}}` e `{{agente_nome}}` são substituídos automaticamente
3. **Business Hours**: JSON flexível para diferentes horários por dia
4. **Rate Limit**: Configurado para 60 requisições/minuto por IP

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Logs do Django: console onde rodou `runserver`
2. Logs de auditoria: no dashboard
3. Django Admin: `/admin/` para inspeção direta dos dados

---

**Versão:** 1.0.0  
**Django:** 5.1+  
**Python:** 3.11+
