from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AuditLog


@login_required
def audit_log_list(request):
    """Lista de logs de auditoria do usuario."""
    logs = AuditLog.objects.filter(
        padaria__owner=request.user
    ).select_related('padaria', 'actor')[:100]  # Ultimos 100 logs
    
    return render(request, "audit/list.html", {"logs": logs})

