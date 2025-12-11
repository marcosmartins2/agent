from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from agents.models import Agent
from audit.models import AuditLog
from core.utils import require_api_key, rate_limited, get_client_ip


def api_docs(request):
    """
    Página de documentação da API.
    """
    return render(request, "api/docs.html")


@require_http_methods(["GET"])
@require_api_key
def get_agent_config(request, slug):
    """
    Retorna configuração de um agente para o n8n.
    Requer autenticação via API key.
    """
    # Rate limiting
    padaria = request.api_key.padaria
    cache_key = f"api_rate_{padaria.id}_{get_client_ip(request)}"
    
    if not rate_limited(cache_key, limit=60, window_seconds=60):
        return JsonResponse({"error": "Rate limit exceeded"}, status=429)
    
    # Buscar agente
    try:
        agent = Agent.objects.get(slug=slug, padaria=padaria, is_active=True)
    except Agent.DoesNotExist:
        return JsonResponse({
            "error": "Agent not found",
            "details": {
                "slug": slug,
                "padaria": padaria.name,
                "hint": "Verifique se o agente pertence à padaria desta API Key e está ativo"
            }
        }, status=404)
    
    # Verificar se a API Key tem acesso a este agente
    if not request.api_key.has_access_to_agent(agent):
        return JsonResponse({
            "error": "Access denied",
            "details": {
                "message": "Esta API Key não tem permissão para acessar este agente",
                "api_key_agent": request.api_key.agent.name if request.api_key.agent else "Todos",
                "requested_agent": agent.name
            }
        }, status=403)
    
    # Log da requisição
    AuditLog.log(
        action="api_call",
        entity="Agent",
        padaria=padaria,
        entity_id=agent.id,
        diff={
            "endpoint": "get_agent_config",
            "slug": slug
        },
        ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")
    )
    
    # Atualizar last_used_at da API key
    from django.utils import timezone
    request.api_key.last_used_at = timezone.now()
    request.api_key.save(update_fields=["last_used_at"])
    
    # Retornar configuração (sem knowledge_base para manter leve)
    config = {
        "name": agent.name,
        "slug": agent.slug,
        "role": agent.role,
        "sector": agent.sector,
        "language": agent.language,
        "greeting": agent.greeting,
        "tone": agent.tone,
        "personality": agent.personality,
        "style_guidelines": agent.style_guidelines,
        "business_hours": agent.business_hours,
        "fallback_message": agent.fallback_message,
        "escalation_rule": agent.escalation_rule,
        "padaria": {
            "name": padaria.name,
            "slug": padaria.slug,
        },
        "updated_at": agent.updated_at.isoformat(),
    }
    
    return JsonResponse(config)


@require_http_methods(["GET"])
@require_api_key
def get_agent_knowledge(request, slug):
    """
    Retorna apenas a base de conhecimento de um agente.
    Endpoint separado para não sobrecarregar a API principal.
    """
    padaria = request.api_key.padaria
    
    # Buscar agente
    try:
        agent = Agent.objects.get(slug=slug, padaria=padaria, is_active=True)
    except Agent.DoesNotExist:
        return JsonResponse({
            "error": "Agent not found",
            "details": {
                "slug": slug,
                "padaria": padaria.name
            }
        }, status=404)
    
    # Verificar se a API Key tem acesso a este agente
    if not request.api_key.has_access_to_agent(agent):
        return JsonResponse({
            "error": "Access denied",
            "details": {
                "message": "Esta API Key não tem permissão para acessar este agente",
                "api_key_agent": request.api_key.agent.name if request.api_key.agent else "Todos",
                "requested_agent": agent.name
            }
        }, status=403)
    
    # Log da requisição
    AuditLog.log(
        action="api_call",
        entity="Agent",
        padaria=padaria,
        entity_id=agent.id,
        diff={
            "endpoint": "get_agent_knowledge",
            "slug": slug
        },
        ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")
    )
    
    # Retornar conhecimento
    knowledge = {
        "slug": agent.slug,
        "knowledge_base": agent.knowledge_base,
        "has_pdf": bool(agent.knowledge_pdf),
        "pdf_text": agent.knowledge_pdf_text if agent.knowledge_pdf else None,
        "updated_at": agent.updated_at.isoformat(),
    }
    
    return JsonResponse(knowledge)
