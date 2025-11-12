from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from organizations.models import Organization
from agents.models import Agent
from audit.models import AuditLog


@login_required
def dashboard(request):
    """Dashboard principal."""
    user = request.user
    
    # Buscar organizações do usuário
    organizations = Organization.objects.filter(owner=user)
    
    # Buscar agentes das organizações
    agents = Agent.objects.filter(organization__owner=user)
    
    # Logs recentes
    logs = AuditLog.objects.filter(organization__owner=user).order_by("-created_at")[:10]
    
    context = {
        "organizations": organizations,
        "agents": agents,
        "logs": logs,
    }
    
    return render(request, "ui/dashboard.html", context)
