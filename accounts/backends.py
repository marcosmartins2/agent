from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    """
    Autentica usando email ou username.
    Permite que o usuário faça login com email ou username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Tenta encontrar o usuário por email ou username
            user = User.objects.get(Q(username=username) | Q(email=username))
            
            # Verifica a senha
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Se o usuário não existe, retorna None
            return None
        except User.MultipleObjectsReturned:
            # Se houver múltiplos usuários (improvável), pega o primeiro
            user = User.objects.filter(Q(username=username) | Q(email=username)).first()
            if user and user.check_password(password):
                return user
        
        return None
