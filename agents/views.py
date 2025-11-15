from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Agent
from .utils import extract_text_from_pdf
from organizations.models import Organization
from audit.models import AuditLog


@login_required
def agent_list(request):
    """Lista de agentes do usuário."""
    agents = Agent.objects.filter(organization__owner=request.user)
    return render(request, "agents/list.html", {"agents": agents})


@login_required
def agent_detail(request, slug):
    """Detalhe de um agente."""
    agent = get_object_or_404(Agent, slug=slug, organization__owner=request.user)
    return render(request, "agents/detail.html", {"agent": agent})


@login_required
def agent_create(request):
    """Criar novo agente."""
    if request.method == "POST":
        org_id = request.POST.get("organization")
        name = request.POST.get("name")
        role = request.POST.get("role", "atendente")
        sector = request.POST.get("sector", "manicure/pedicure")
        
        organization = get_object_or_404(Organization, id=org_id, owner=request.user)
        
        # Criar agente com novos campos
        agent = Agent.objects.create(
            organization=organization,
            name=name,
            role=role,
            sector=sector,
            language=request.POST.get("language", "pt-BR"),
            status=request.POST.get("status", "ativo"),
            personality=request.POST.get("personality", "amigavel"),
            greeting=request.POST.get("greeting", ""),
            out_of_hours_message=request.POST.get("out_of_hours_message", ""),
            transfer_keywords=request.POST.get("transfer_keywords", "falar com humano, atendente, pessoa"),
            max_response_time=int(request.POST.get("max_response_time", 30)),
            tone=request.POST.get("tone", ""),
            style_guidelines=request.POST.get("style_guidelines", ""),
            knowledge_base=request.POST.get("knowledge_base", ""),
            fallback_message=request.POST.get("fallback_message", ""),
            escalation_rule=request.POST.get("escalation_rule", ""),
            n8n_webhook_url=request.POST.get("n8n_webhook_url", ""),
        )
        
        # Processar upload de PDF se houver
        if 'knowledge_pdf' in request.FILES:
            pdf_file = request.FILES['knowledge_pdf']
            agent.knowledge_pdf = pdf_file
            agent.knowledge_pdf_category = request.POST.get("knowledge_pdf_category", "")
            
            try:
                # Extrair texto do PDF automaticamente
                extracted_text = extract_text_from_pdf(pdf_file)
                agent.knowledge_pdf_text = extracted_text
                
                messages.success(request, f"PDF processado com sucesso! {len(extracted_text)} caracteres extraídos.")
            except Exception as e:
                messages.warning(request, f"Erro ao processar PDF: {str(e)}")
            
            agent.save()
        
        AuditLog.log(
            action="create",
            entity="Agent",
            organization=organization,
            actor=request.user,
            entity_id=agent.id,
            diff={"name": name, "slug": agent.slug}
        )
        
        messages.success(request, f"Agente '{name}' criado com sucesso!")
        return redirect("agents:detail", slug=agent.slug)
    
    organizations = Organization.objects.filter(owner=request.user)
    return render(request, "agents/form.html", {"organizations": organizations})


@login_required
def agent_edit(request, slug):
    """Editar agente."""
    agent = get_object_or_404(Agent, slug=slug, organization__owner=request.user)
    
    if request.method == "POST":
        agent.name = request.POST.get("name", agent.name)
        agent.role = request.POST.get("role", agent.role)
        agent.sector = request.POST.get("sector", agent.sector)
        agent.language = request.POST.get("language", agent.language)
        agent.status = request.POST.get("status", agent.status)
        agent.personality = request.POST.get("personality", agent.personality)
        agent.greeting = request.POST.get("greeting", agent.greeting)
        agent.out_of_hours_message = request.POST.get("out_of_hours_message", agent.out_of_hours_message)
        agent.transfer_keywords = request.POST.get("transfer_keywords", agent.transfer_keywords)
        agent.max_response_time = int(request.POST.get("max_response_time", agent.max_response_time))
        agent.tone = request.POST.get("tone", agent.tone)
        agent.style_guidelines = request.POST.get("style_guidelines", agent.style_guidelines)
        agent.knowledge_base = request.POST.get("knowledge_base", agent.knowledge_base)
        agent.fallback_message = request.POST.get("fallback_message", agent.fallback_message)
        agent.escalation_rule = request.POST.get("escalation_rule", agent.escalation_rule)
        agent.n8n_webhook_url = request.POST.get("n8n_webhook_url", agent.n8n_webhook_url)
        agent.is_active = request.POST.get("is_active") == "on"
        
        # Processar upload de PDF se houver
        if 'knowledge_pdf' in request.FILES:
            pdf_file = request.FILES['knowledge_pdf']
            agent.knowledge_pdf = pdf_file
            agent.knowledge_pdf_category = request.POST.get("knowledge_pdf_category", agent.knowledge_pdf_category)
            
            try:
                # Extrair texto do PDF automaticamente
                extracted_text = extract_text_from_pdf(pdf_file)
                agent.knowledge_pdf_text = extracted_text
                    
                messages.success(request, f"PDF processado com sucesso! {len(extracted_text)} caracteres extraídos.")
            except Exception as e:
                messages.warning(request, f"Erro ao processar PDF: {str(e)}")
        
        # Atualizar categoria do PDF sem fazer novo upload
        elif request.POST.get("knowledge_pdf_category"):
            agent.knowledge_pdf_category = request.POST.get("knowledge_pdf_category")
        
        agent.save()
        
        AuditLog.log(
            action="update",
            entity="Agent",
            organization=agent.organization,
            actor=request.user,
            entity_id=agent.id,
            diff={"name": agent.name}
        )
        
        messages.success(request, "Agente atualizado com sucesso!")
        return redirect("agents:detail", slug=agent.slug)
    
    return render(request, "agents/form.html", {"agent": agent})


@login_required
def agent_delete(request, slug):
    """Deletar agente."""
    agent = get_object_or_404(Agent, slug=slug, organization__owner=request.user)
    
    if request.method == "POST":
        organization = agent.organization
        agent_name = agent.name
        
        AuditLog.log(
            action="delete",
            entity="Agent",
            organization=organization,
            actor=request.user,
            entity_id=agent.id,
            diff={"name": agent_name, "slug": slug}
        )
        
        agent.delete()
        messages.success(request, f"Agente '{agent_name}' deletado com sucesso!")
        return redirect("agents:list")
    
    return render(request, "agents/confirm_delete.html", {"agent": agent})


@login_required
def agent_playground(request, slug):
    """Playground para testar agente."""
    agent = get_object_or_404(Agent, slug=slug, organization__owner=request.user)
    
    # Renderizar greeting com valores de exemplo
    cliente_nome = request.POST.get("cliente_nome", "Maria")
    rendered_greeting = agent.render_greeting(cliente_nome=cliente_nome)
    
    context = {
        "agent": agent,
        "rendered_greeting": rendered_greeting,
        "cliente_nome": cliente_nome,
    }
    
    return render(request, "agents/playground.html", context)


@login_required
def agent_delete_pdf(request, slug):
    """Deletar PDF de conhecimento do agente."""
    agent = get_object_or_404(Agent, slug=slug, organization__owner=request.user)
    
    if request.method == "POST":
        if agent.knowledge_pdf:
            # Deletar arquivo físico
            agent.knowledge_pdf.delete(save=False)
            # Limpar campos relacionados
            agent.knowledge_pdf_text = ""
            agent.knowledge_pdf_category = ""
            agent.save()
            
            AuditLog.log(
                action="delete_pdf",
                entity="Agent",
                organization=agent.organization,
                actor=request.user,
                entity_id=agent.id,
                diff={"agent": agent.name, "action": "PDF deletado"}
            )
            
            messages.success(request, "PDF deletado com sucesso!")
        else:
            messages.warning(request, "Este agente não possui PDF.")
        
        return redirect("agents:detail", slug=agent.slug)
    
    return render(request, "agents/confirm_delete_pdf.html", {"agent": agent})

