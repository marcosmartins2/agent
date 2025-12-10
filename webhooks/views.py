import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from audit.models import AuditLog
from core.utils import require_api_key, get_client_ip


@csrf_exempt
@require_http_methods(["POST"])
@require_api_key
def receive_event(request):
    """
    Recebe eventos do n8n via webhook.
    CSRF exempt pois é chamado externamente.
    Requer autenticação via API key.
    """
    try:
        # Parse JSON body
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    # Validar campos obrigatórios
    event_type = data.get("type")
    agent_slug = data.get("agent_slug")
    session_id = data.get("session_id")
    payload = data.get("payload", {})
    
    if not all([event_type, agent_slug, session_id]):
        return JsonResponse({
            "error": "Missing required fields: type, agent_slug, session_id"
        }, status=400)
    
    # Log do evento
    padaria = request.api_key.padaria
    AuditLog.log(
        action="webhook_received",
        entity="n8n_event",
        organization=padaria,
        entity_id=session_id,
        diff={
            "type": event_type,
            "agent_slug": agent_slug,
            "session_id": session_id,
            "payload": payload
        },
        ip=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")
    )
    
    return JsonResponse({"status": "ok"})
