from django.contrib import admin
from .models import Padaria, PadariaUser, ApiKey


class PadariaUserInline(admin.TabularInline):
    model = PadariaUser
    extra = 1
    autocomplete_fields = ['user']


class ApiKeyInline(admin.TabularInline):
    model = ApiKey
    extra = 0
    readonly_fields = ['key', 'created_at', 'last_used_at']
    fields = ['key', 'name', 'is_active', 'created_at', 'last_used_at']


@admin.register(Padaria)
class PadariaAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'owner__username', 'email']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PadariaUserInline, ApiKeyInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'owner', 'is_active')
        }),
        ('Contato', {
            'fields': ('phone', 'email', 'address'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PadariaUser)
class PadariaUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'padaria', 'role', 'created_at']
    list_filter = ['role', 'padaria']
    search_fields = ['user__username', 'user__email', 'padaria__name']
    autocomplete_fields = ['user', 'padaria']


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ['padaria', 'name', 'key_preview', 'is_active', 'last_used_at']
    list_filter = ['is_active', 'padaria']
    search_fields = ['padaria__name', 'name']
    readonly_fields = ['key', 'created_at', 'last_used_at']
    
    def key_preview(self, obj):
        return f"{obj.key[:12]}..."
    key_preview.short_description = "Chave"
