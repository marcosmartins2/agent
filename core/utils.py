"""
Utilidades e decorators de segurança para o projeto.
"""
from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from organizations.models import ApiKey


def get_client_ip(request):
    """Obtém o IP do cliente da requisição."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def require_api_key(view_func):
    """
    Decorator que exige autenticação via API key.
    A chave pode vir via query param 'api_key' ou header 'X-API-Key'.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Tentar obter API key da query string ou header
        api_key_value = request.GET.get('api_key') or request.META.get('HTTP_X_API_KEY')
        
        if not api_key_value:
            return JsonResponse({
                "error": "API key required. Provide via 'api_key' query param or 'X-API-Key' header."
            }, status=401)
        
        # Validar API key
        try:
            api_key = ApiKey.objects.select_related('padaria').get(
                key=api_key_value,
                is_active=True
            )
        except ApiKey.DoesNotExist:
            return JsonResponse({"error": "Invalid or inactive API key"}, status=401)
        
        # Anexar API key e padaria ao request
        request.api_key = api_key
        request.padaria = api_key.padaria
        # Alias para compatibilidade
        request.organization = api_key.padaria
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def rate_limited(cache_key, limit=60, window_seconds=60):
    """
    Implementa rate limiting simples usando cache.
    
    Args:
        cache_key: Chave única para identificar o limitador
        limit: Número máximo de requisições permitidas
        window_seconds: Janela de tempo em segundos
    
    Returns:
        bool: True se dentro do limite, False se excedeu
    """
    # Obter contador atual
    count = cache.get(cache_key, 0)
    
    if count >= limit:
        return False
    
    # Incrementar contador
    if count == 0:
        # Primeira requisição na janela
        cache.set(cache_key, 1, window_seconds)
    else:
        # Incrementar existente
        cache.incr(cache_key)
    
    return True


def rate_limit_decorator(limit=60, window_seconds=60, key_func=None):
    """
    Decorator para aplicar rate limiting em views.
    
    Args:
        limit: Número máximo de requisições
        window_seconds: Janela de tempo
        key_func: Função que retorna a chave do cache baseada no request
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Gerar chave do cache
            if key_func:
                cache_key = key_func(request)
            else:
                # Default: usar IP do cliente
                cache_key = f"rate_limit_{get_client_ip(request)}"
            
            # Verificar rate limit
            if not rate_limited(cache_key, limit, window_seconds):
                return JsonResponse({
                    "error": f"Rate limit exceeded. Max {limit} requests per {window_seconds} seconds."
                }, status=429)
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
