from django.test import TestCase
from django.contrib.auth.models import User
from organizations.models import Organization
from .models import Agent


class AgentModelTest(TestCase):
    """Testes para o modelo Agent."""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.organization = Organization.objects.create(name="Test Org", owner=self.user)
    
    def test_create_agent(self):
        """Testa criação de agente."""
        agent = Agent.objects.create(
            organization=self.organization,
            name="Ana"
        )
        self.assertIsNotNone(agent.slug)
        self.assertTrue(agent.is_active)
        self.assertEqual(agent.role, "atendente")
    
    def test_agent_slug_unique(self):
        """Testa que slug é único."""
        Agent.objects.create(organization=self.organization, name="Ana")
        # Segundo agente com mesmo nome deve ter slug diferente ou erro
        with self.assertRaises(Exception):
            Agent.objects.create(organization=self.organization, name="Ana")
    
    def test_render_greeting(self):
        """Testa renderização da saudação."""
        agent = Agent.objects.create(
            organization=self.organization,
            name="Ana",
            greeting="Olá {{cliente_nome}}! Sou {{agente_nome}}."
        )
        rendered = agent.render_greeting(cliente_nome="João")
        self.assertIn("João", rendered)
        self.assertIn("Ana", rendered)
