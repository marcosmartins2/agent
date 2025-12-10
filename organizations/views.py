from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Padaria, PadariaUser, ApiKey
from audit.models import AuditLog


def get_user_padarias(user):
    """Retorna padarias que o usuário pode acessar."""
    if user.is_superuser:
        return Padaria.objects.all()
    user_padaria_ids = PadariaUser.objects.filter(user=user).values_list('padaria_id', flat=True)
    return Padaria.objects.filter(id__in=user_padaria_ids)


@login_required
def organization_list(request):
    """Lista de padarias do usuário."""
    padarias = get_user_padarias(request.user)
    return render(request, "organizations/list.html", {"organizations": padarias})


@login_required
def organization_detail(request, slug):
    """Detalhe de uma padaria."""
    padarias = get_user_padarias(request.user)
    organization = get_object_or_404(Padaria, slug=slug)
    
    # Verificar acesso
    if not request.user.is_superuser and organization not in padarias:
        messages.error(request, "Você não tem acesso a esta padaria.")
        return redirect("organizations:list")
    
    return render(request, "organizations/detail.html", {"organization": organization})


@login_required
def organization_create(request):
    """Criar nova padaria (apenas admin)."""
    if not request.user.is_superuser:
        messages.error(request, "Apenas administradores podem criar padarias.")
        return redirect("organizations:list")
    
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            org = Padaria.objects.create(name=name, owner=request.user)
            
            # Criar membership como dono
            PadariaUser.objects.create(user=request.user, padaria=org, role='dono')
            
            AuditLog.log(
                action="create",
                entity="Padaria",
                organization=org,
                actor=request.user,
                entity_id=org.id,
                diff={"name": name}
            )
            messages.success(request, f"Padaria '{name}' criada com sucesso!")
            return redirect("organizations:detail", slug=org.slug)
        else:
            messages.error(request, "Nome é obrigatório.")
    
    return render(request, "organizations/form.html")


@login_required
def organization_edit(request, slug):
    """Editar padaria."""
    padarias = get_user_padarias(request.user)
    organization = get_object_or_404(Padaria, slug=slug)
    
    # Verificar acesso
    if not request.user.is_superuser and organization not in padarias:
        messages.error(request, "Você não tem acesso a esta padaria.")
        return redirect("organizations:list")
    
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            old_name = organization.name
            organization.name = name
            organization.save()
            
            AuditLog.log(
                action="update",
                entity="Padaria",
                organization=organization,
                actor=request.user,
                entity_id=organization.id,
                diff={"old_name": old_name, "new_name": name}
            )
            
            messages.success(request, "Padaria atualizada com sucesso!")
            return redirect("organizations:detail", slug=organization.slug)
        else:
            messages.error(request, "Nome é obrigatório.")
    
    return render(request, "organizations/form.html", {"organization": organization})


@login_required
def organization_delete(request, slug):
    """Deletar padaria (apenas admin)."""
    if not request.user.is_superuser:
        messages.error(request, "Apenas administradores podem deletar padarias.")
        return redirect("organizations:list")
    
    organization = get_object_or_404(Padaria, slug=slug)
    
    if request.method == "POST":
        org_name = organization.name
        
        AuditLog.log(
            action="delete",
            entity="Padaria",
            organization=organization,
            actor=request.user,
            entity_id=organization.id,
            diff={"name": org_name, "slug": slug}
        )
        
        organization.delete()
        messages.success(request, f"Padaria '{org_name}' deletada com sucesso!")
        return redirect("organizations:list")
    
    return render(request, "organizations/confirm_delete.html", {"organization": organization})


@login_required
def apikey_list(request):
    """Lista de API keys do usuário."""
    padarias = get_user_padarias(request.user)
    api_keys = ApiKey.objects.filter(padaria__in=padarias)
    return render(request, "organizations/apikey_list.html", {"api_keys": api_keys})


@login_required
def apikey_create(request):
    """Criar nova API key."""
    padarias = get_user_padarias(request.user)
    
    if request.method == "POST":
        org_id = request.POST.get("organization")
        name = request.POST.get("name", "")
        
        organization = get_object_or_404(Padaria, id=org_id)
        
        # Verificar acesso
        if not request.user.is_superuser and organization not in padarias:
            messages.error(request, "Você não tem acesso a esta padaria.")
            return redirect("organizations:apikeys")
        
        api_key = ApiKey.objects.create(
            padaria=organization,
            name=name
        )
        
        AuditLog.log(
            action="create",
            entity="ApiKey",
            organization=organization,
            actor=request.user,
            entity_id=api_key.id,
            diff={"name": name}
        )
        
        messages.success(request, f"API Key criada: {api_key.key}")
        messages.warning(request, "Copie a chave agora! Ela não será exibida novamente.")
        return redirect("organizations:apikeys")
    
    return render(request, "organizations/apikey_form.html", {"organizations": padarias})


@login_required
def apikey_delete(request, pk):
    """Deletar API key."""
    padarias = get_user_padarias(request.user)
    api_key = get_object_or_404(ApiKey, pk=pk)
    
    # Verificar acesso
    if not request.user.is_superuser and api_key.padaria not in padarias:
        messages.error(request, "Você não tem acesso a esta API key.")
        return redirect("organizations:apikeys")
    
    if request.method == "POST":
        organization = api_key.padaria
        key_preview = api_key.key[:12]
        
        AuditLog.log(
            action="delete",
            entity="ApiKey",
            organization=organization,
            actor=request.user,
            entity_id=api_key.id,
            diff={"key_preview": key_preview}
        )
        
        api_key.delete()
        messages.success(request, "API Key deletada com sucesso!")
        return redirect("organizations:apikeys")
    
    return render(request, "organizations/apikey_confirm_delete.html", {"api_key": api_key})
