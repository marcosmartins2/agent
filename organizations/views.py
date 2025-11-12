from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organization, ApiKey
from audit.models import AuditLog


@login_required
def organization_list(request):
    """Lista de organizações do usuário."""
    organizations = Organization.objects.filter(owner=request.user)
    return render(request, "organizations/list.html", {"organizations": organizations})


@login_required
def organization_detail(request, slug):
    """Detalhe de uma organização."""
    organization = get_object_or_404(Organization, slug=slug, owner=request.user)
    return render(request, "organizations/detail.html", {"organization": organization})


@login_required
def organization_create(request):
    """Criar nova organização."""
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            org = Organization.objects.create(name=name, owner=request.user)
            AuditLog.log(
                action="create",
                entity="Organization",
                organization=org,
                actor=request.user,
                entity_id=org.id,
                diff={"name": name}
            )
            messages.success(request, f"Organização '{name}' criada com sucesso!")
            return redirect("organizations:detail", slug=org.slug)
        else:
            messages.error(request, "Nome é obrigatório.")
    
    return render(request, "organizations/form.html")


@login_required
def organization_edit(request, slug):
    """Editar organização."""
    organization = get_object_or_404(Organization, slug=slug, owner=request.user)
    
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            old_name = organization.name
            organization.name = name
            organization.save()
            
            AuditLog.log(
                action="update",
                entity="Organization",
                organization=organization,
                actor=request.user,
                entity_id=organization.id,
                diff={"old_name": old_name, "new_name": name}
            )
            
            messages.success(request, "Organização atualizada com sucesso!")
            return redirect("organizations:detail", slug=organization.slug)
        else:
            messages.error(request, "Nome é obrigatório.")
    
    return render(request, "organizations/form.html", {"organization": organization})


@login_required
def apikey_list(request):
    """Lista de API keys do usuário."""
    api_keys = ApiKey.objects.filter(organization__owner=request.user)
    return render(request, "organizations/apikey_list.html", {"api_keys": api_keys})


@login_required
def apikey_create(request):
    """Criar nova API key."""
    if request.method == "POST":
        org_id = request.POST.get("organization")
        name = request.POST.get("name", "")
        
        organization = get_object_or_404(Organization, id=org_id, owner=request.user)
        
        api_key = ApiKey.objects.create(
            organization=organization,
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
    
    organizations = Organization.objects.filter(owner=request.user)
    return render(request, "organizations/apikey_form.html", {"organizations": organizations})


@login_required
def apikey_delete(request, pk):
    """Deletar API key."""
    api_key = get_object_or_404(ApiKey, pk=pk, organization__owner=request.user)
    
    if request.method == "POST":
        organization = api_key.organization
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
