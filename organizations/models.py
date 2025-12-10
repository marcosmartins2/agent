import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Padaria(models.Model):
    """
    Padaria (tenant principal do sistema).
    Antiga 'Organization' renomeada para o novo contexto.
    """
    name = models.CharField(max_length=200, verbose_name="Nome da Padaria")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_padarias",
        verbose_name="Dono"
    )
    # Campos de contato
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    cnpj = models.CharField(max_length=18, blank=True, verbose_name="CNPJ")
    address = models.TextField(blank=True, verbose_name="Endereço")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Padaria"
        verbose_name_plural = "Padarias"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            
            # Garantir que o slug seja único
            while Padaria.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_agent(self):
        """Retorna o agente da padaria (limite de 1)."""
        return self.agents.first()
    
    def has_agent(self):
        """Verifica se a padaria já tem um agente."""
        return self.agents.exists()


class PadariaUser(models.Model):
    """
    Relaciona usuários com padarias e seus papéis.
    """
    ROLE_CHOICES = [
        ('dono', 'Dono'),
        ('funcionario', 'Funcionário'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="padaria_memberships",
        verbose_name="Usuário"
    )
    padaria = models.ForeignKey(
        Padaria,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="Padaria"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='funcionario',
        verbose_name="Papel"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Adicionado em")
    
    class Meta:
        verbose_name = "Membro da Padaria"
        verbose_name_plural = "Membros da Padaria"
        unique_together = [("user", "padaria")]
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.user.username} - {self.padaria.name} ({self.get_role_display()})"
    
    def is_dono(self):
        return self.role == 'dono'
    
    def is_funcionario(self):
        return self.role == 'funcionario'


class ApiKey(models.Model):
    """
    Chave de API para autenticação de integrações (n8n).
    Vinculada à Padaria.
    """
    key = models.CharField(max_length=64, unique=True, db_index=True, verbose_name="Chave")
    padaria = models.ForeignKey(
        Padaria,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name="Padaria"
    )
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    name = models.CharField(max_length=100, blank=True, verbose_name="Nome/Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name="Último uso")

    class Meta:
        verbose_name = "Chave de API"
        verbose_name_plural = "Chaves de API"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.padaria.name} - {self.key[:12]}..."

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = f"sk_{secrets.token_urlsafe(32)}"
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Gera uma nova chave única."""
        return f"sk_{secrets.token_urlsafe(32)}"


# Alias para compatibilidade durante migração
Organization = Padaria
