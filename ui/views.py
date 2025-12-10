from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from organizations.models import Padaria, PadariaUser
from agents.models import Agent
from audit.models import AuditLog


@login_required
def dashboard(request):
    """Dashboard principal."""
    user = request.user
    
    # Buscar padarias do usuário (onde é membro ou dono)
    if user.is_superuser:
        padarias = Padaria.objects.all()
        agents = Agent.objects.all()
        logs = AuditLog.objects.all().order_by("-created_at")[:10]
    else:
        # Padarias onde o usuário é membro
        user_padaria_ids = PadariaUser.objects.filter(user=user).values_list('padaria_id', flat=True)
        padarias = Padaria.objects.filter(id__in=user_padaria_ids)
        
        # Agentes das padarias do usuário
        agents = Agent.objects.filter(padaria__in=padarias)
        
        # Logs recentes das padarias do usuário
        logs = AuditLog.objects.filter(organization__in=padarias).order_by("-created_at")[:10]
    
    context = {
        "organizations": padarias,  # Manter compatibilidade com template existente
        "padarias": padarias,
        "agents": agents,
        "logs": logs,
    }
    
    return render(request, "ui/dashboard.html", context)
