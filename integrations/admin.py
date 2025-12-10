from django.contrib import admin
from .models import N8nConfig


@admin.register(N8nConfig)
class N8nConfigAdmin(admin.ModelAdmin):
    list_display = ("padaria", "enabled", "webhook_url", "updated_at")
    search_fields = ("padaria__name",)
    list_filter = ("enabled", "created_at")

