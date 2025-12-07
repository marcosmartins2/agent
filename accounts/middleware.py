from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Middleware que força login em todas as páginas, exceto login e register.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs que não precisam de autenticação
        exempt_urls = [
            reverse('accounts:login'),
            reverse('accounts:register'),
            '/admin/',  # Manter acesso ao admin
            '/static/',
            '/api/',    # API usa autenticação via API Key
        ]
        
        # Verifica se a URL atual está nas exceções
        path = request.path_info
        is_exempt = any(path.startswith(url) for url in exempt_urls)
        
        # Se não estiver autenticado e não for uma URL de exceção, redireciona para login
        if not request.user.is_authenticated and not is_exempt:
            return redirect('accounts:login')
        
        response = self.get_response(request)
        return response
