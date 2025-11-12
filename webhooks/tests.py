import json
from django.test import TestCase
from django.contrib.auth.models import User
from organizations.models import Organization, ApiKey
from audit.models import AuditLog


class WebhookTest(TestCase):
    """Testes para webhooks."""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.organization = Organization.objects.create(name="Test Org", owner=self.user)
        self.api_key = ApiKey.objects.create(organization=self.organization)
    
    def test_receive_event_success(self):
        """Testa recebimento de evento válido."""
        payload = {
            "type": "message",
            "agent_slug": "test-agent",
            "session_id": "session123",
            "payload": {
                "text": "Olá",
                "metadata": {"canal": "whatsapp"}
            }
        }
        
        response = self.client.post(
            "/webhooks/n8n/events",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_API_KEY=self.api_key.key
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        
        # Verificar que foi logado
        log = AuditLog.objects.filter(action="webhook_received").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.diff["session_id"], "session123")
    
    def test_receive_event_no_api_key(self):
        """Testa webhook sem API key."""
        payload = {
            "type": "message",
            "agent_slug": "test-agent",
            "session_id": "session123",
            "payload": {}
        }
        
        response = self.client.post(
            "/webhooks/n8n/events",
            data=json.dumps(payload),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_receive_event_invalid_json(self):
        """Testa webhook com JSON inválido."""
        response = self.client.post(
            "/webhooks/n8n/events",
            data="invalid json",
            content_type="application/json",
            HTTP_X_API_KEY=self.api_key.key
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_receive_event_missing_fields(self):
        """Testa webhook com campos faltando."""
        payload = {"type": "message"}  # Faltam agent_slug e session_id
        
        response = self.client.post(
            "/webhooks/n8n/events",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_API_KEY=self.api_key.key
        )
        
        self.assertEqual(response.status_code, 400)
