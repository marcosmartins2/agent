from django.test import TestCase
from django.contrib.auth.models import User
from organizations.models import Organization, ApiKey
from agents.models import Agent


class ApiEndpointTest(TestCase):
    """Testes para os endpoints da API."""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.organization = Organization.objects.create(name="Test Org", owner=self.user)
        self.api_key = ApiKey.objects.create(organization=self.organization)
        self.agent = Agent.objects.create(
            organization=self.organization,
            name="Test Agent"
        )
    
    def test_get_agent_config_success(self):
        """Testa busca de configuração com API key válida."""
        response = self.client.get(
            f"/api/n8n/agents/{self.agent.slug}/config",
            HTTP_X_API_KEY=self.api_key.key
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Test Agent")
        self.assertEqual(data["slug"], self.agent.slug)
    
    def test_get_agent_config_no_api_key(self):
        """Testa busca sem API key."""
        response = self.client.get(f"/api/n8n/agents/{self.agent.slug}/config")
        self.assertEqual(response.status_code, 401)
    
    def test_get_agent_config_invalid_api_key(self):
        """Testa busca com API key inválida."""
        response = self.client.get(
            f"/api/n8n/agents/{self.agent.slug}/config",
            HTTP_X_API_KEY="invalid_key"
        )
        self.assertEqual(response.status_code, 401)
    
    def test_get_agent_config_not_found(self):
        """Testa busca de agente inexistente."""
        response = self.client.get(
            "/api/n8n/agents/nonexistent-agent/config",
            HTTP_X_API_KEY=self.api_key.key
        )
        self.assertEqual(response.status_code, 404)
