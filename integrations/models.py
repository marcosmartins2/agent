from django.db import models
from organizations.models import Organization


class N8nConfig(models.Model):
    """
    Configuração de integração com n8n por organização.
    """
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name="n8n_config",
        verbose_name="Organização"
    )
    webhook_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="URL do Webhook n8n",
        help_text="URL para onde enviaremos eventos"
    )
    api_token = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Token de API n8n",
        help_text="Token para autenticar chamadas ao n8n"
    )
    enabled = models.BooleanField(
        default=False,
        verbose_name="Habilitado",
        help_text="Ativar/desativar integração"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Configuração n8n"
        verbose_name_plural = "Configurações n8n"

    def __str__(self):
        return f"n8n Config - {self.organization.name}"
