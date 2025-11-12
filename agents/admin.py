from django.contrib import admin
from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "role", "sector", "is_active", "created_at")
    search_fields = ("name", "slug", "organization__name", "role", "sector")
    list_filter = ("is_active", "role", "sector", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    
    fieldsets = (
        ("Informações Básicas", {
            "fields": ("organization", "name", "slug", "role", "sector", "language", "is_active")
        }),
        ("Comportamento", {
            "fields": ("greeting", "tone", "style_guidelines")
        }),
        ("Conhecimento", {
            "fields": ("knowledge_base", "business_hours")
        }),
        ("Exceções", {
            "fields": ("fallback_message", "escalation_rule")
        }),
    )
