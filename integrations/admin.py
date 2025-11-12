from django.contrib import admin
from .models import N8nConfig


@admin.register(N8nConfig)
class N8nConfigAdmin(admin.ModelAdmin):
    list_display = ("organization", "enabled", "webhook_url", "updated_at")
    search_fields = ("organization__name",)
    list_filter = ("enabled", "created_at")
