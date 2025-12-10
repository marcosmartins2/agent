from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "entity", "entity_id", "padaria")
    search_fields = ("action", "entity", "entity_id", "actor__username", "padaria__name")
    list_filter = ("action", "entity", "created_at")
    readonly_fields = ("padaria", "actor", "action", "entity", "entity_id", "diff", "ip_address", "user_agent", "created_at")
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

