from django.contrib import admin
from .models import Organization, ApiKey


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "created_at")
    search_fields = ("name", "slug", "owner__username")
    list_filter = ("created_at",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("organization", "key_preview", "is_active", "created_at", "last_used_at")
    search_fields = ("key", "organization__name", "name")
    list_filter = ("is_active", "created_at")
    readonly_fields = ("key", "created_at", "last_used_at")

    def key_preview(self, obj):
        return f"{obj.key[:16]}..."
    key_preview.short_description = "Chave"
