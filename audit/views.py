from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AuditLog


@login_required
def audit_log_list(request):
    """Lista de logs de auditoria do usuário."""
    logs = AuditLog.objects.filter(
        organization__owner=request.user
    ).select_related('organization', 'actor')[:100]  # Últimos 100 logs
    
    return render(request, "audit/list.html", {"logs": logs})
