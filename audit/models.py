from django.db import models
from django.contrib.auth.models import User
from organizations.models import Organization


class AuditLog(models.Model):
    """
    Log de auditoria para rastrear ações no sistema.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        verbose_name="Organização",
        null=True,
        blank=True
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Usuário"
    )
    action = models.CharField(
        max_length=100,
        verbose_name="Ação",
        help_text="Tipo de ação (create, update, delete, api_call, webhook, etc)"
    )
    entity = models.CharField(
        max_length=100,
        verbose_name="Entidade",
        help_text="Nome da entidade afetada (Agent, ApiKey, etc)"
    )
    entity_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ID da Entidade",
        help_text="Identificador único da entidade"
    )
    diff = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Diferenças",
        help_text="Dados da mudança ou payload do evento"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em", db_index=True)

    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["organization", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        actor_name = self.actor.username if self.actor else "Sistema"
        return f"{actor_name} - {self.action} - {self.entity} ({self.created_at})"

    @classmethod
    def log(cls, action, entity, organization=None, actor=None, entity_id=None, diff=None, ip=None, user_agent=None):
        """Helper para criar log de forma simplificada."""
        return cls.objects.create(
            organization=organization,
            actor=actor,
            action=action,
            entity=entity,
            entity_id=str(entity_id) if entity_id else "",
            diff=diff or {},
            ip_address=ip,
            user_agent=user_agent or ""
        )
