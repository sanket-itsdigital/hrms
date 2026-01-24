from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator

from leads_crm.models import Lead, Proposal, MeetingLog
from accounts.models import User
from projects.models import Project


@login_required
def list_leads(request):
    """List all leads with filtering"""
    user = request.user
    
    # Get user's organization
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    organization = user.organization
    
    # Base queryset
    if user.is_ceo or user.is_bde:
        # CEO/BDE can see all leads
        leads = Lead.objects.filter(
            organization=organization
        ).select_related('assigned_to', 'created_by', 'converted_to_project').order_by('-created_at')
    else:
        # Others see only assigned leads
        leads = Lead.objects.filter(
            organization=organization,
            assigned_to=user
        ).select_related('assigned_to', 'created_by', 'converted_to_project').order_by('-created_at')
    
    # Filtering
    search_query = request.GET.get('search', '')
    stage_filter = request.GET.get('stage', '')
    assigned_filter = request.GET.get('assigned', '')
    
    if search_query:
        leads = leads.filter(
            Q(name__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    if stage_filter:
        leads = leads.filter(stage=stage_filter)
    
    if assigned_filter and (user.is_ceo or user.is_bde):
        leads = leads.filter(assigned_to_id=assigned_filter)
    
    # Pagination
    paginator = Paginator(leads, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get users for filter dropdown (only for CEO/BDE)
    users = None
    if user.is_ceo or user.is_bde:
        users = User.objects.filter(
            organization=organization,
            is_active=True
        ).order_by('first_name', 'last_name')
    
    # Statistics
    total_leads = leads.count()
    new_count = leads.filter(stage='NEW').count()
    contacted_count = leads.filter(stage='CONTACTED').count()
    proposal_sent_count = leads.filter(stage='PROPOSAL_SENT').count()
    negotiation_count = leads.filter(stage='NEGOTIATION').count()
    won_count = leads.filter(stage='CLOSED_WON').count()
    lost_count = leads.filter(stage='CLOSED_LOST').count()
    total_revenue = leads.filter(stage='CLOSED_WON').aggregate(Sum('expected_revenue'))['expected_revenue__sum'] or 0
    pipeline_revenue = leads.filter(stage__in=['NEW', 'CONTACTED', 'PROPOSAL_SENT', 'NEGOTIATION']).aggregate(Sum('expected_revenue'))['expected_revenue__sum'] or 0
    
    context = {
        'page_obj': page_obj,
        'leads': page_obj,
        'users': users,
        'total_leads': total_leads,
        'new_count': new_count,
        'contacted_count': contacted_count,
        'proposal_sent_count': proposal_sent_count,
        'negotiation_count': negotiation_count,
        'won_count': won_count,
        'lost_count': lost_count,
        'total_revenue': total_revenue,
        'pipeline_revenue': pipeline_revenue,
        'search_query': search_query,
        'stage_filter': stage_filter,
        'assigned_filter': assigned_filter,
        'can_edit': user.is_ceo or user.is_bde,
    }
    
    return render(request, 'leads_crm/list.html', context)


@login_required
def create_lead(request):
    """Create a new lead"""
    user = request.user
    
    if not user.organization:
        messages.error(request, 'You are not associated with an organization.')
        return redirect('accounts:dashboard')
    
    # Check permissions
    if not (user.is_ceo or user.is_bde):
        messages.error(request, 'You do not have permission to create leads.')
        return redirect('leads_crm:list')
    
    if request.method == 'POST':
        from leads_crm.forms import LeadForm
        form = LeadForm(request.POST, user=user, organization=user.organization)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.organization = user.organization
            lead.created_by = user
            if not lead.assigned_to:
                lead.assigned_to = user
            lead.save()
            messages.success(request, f'Lead created successfully for {lead.name}!')
            return redirect('leads_crm:list')
    else:
        from leads_crm.forms import LeadForm
        form = LeadForm(user=user, organization=user.organization)
    
    return render(request, 'leads_crm/form.html', {
        'form': form,
        'title': 'Create New Lead'
    })


@login_required
def update_lead(request, id):
    """Update an existing lead"""
    user = request.user
    lead = get_object_or_404(Lead, id=id)
    
    # Check permissions
    if not (user.is_ceo or user.is_bde):
        if lead.assigned_to != user:
            messages.error(request, 'You do not have permission to edit this lead.')
            return redirect('leads_crm:list')
    
    if request.method == 'POST':
        from leads_crm.forms import LeadForm
        form = LeadForm(request.POST, instance=lead, user=user, organization=user.organization)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully!')
            return redirect('leads_crm:list')
    else:
        from leads_crm.forms import LeadForm
        form = LeadForm(instance=lead, user=user, organization=user.organization)
    
    return render(request, 'leads_crm/form.html', {
        'form': form,
        'lead': lead,
        'title': 'Update Lead'
    })


@login_required
def convert_to_project(request, id):
    """Convert lead to project"""
    user = request.user
    
    # Check permissions
    if not user.is_ceo:
        messages.error(request, 'Only CEO can convert leads to projects.')
        return redirect('leads_crm:list')
    
    lead = get_object_or_404(Lead, id=id)
    
    if lead.converted_to_project:
        messages.warning(request, 'This lead has already been converted to a project.')
        return redirect('leads_crm:list')
    
    if request.method == 'POST':
        # Create project from lead
        project = Project.objects.create(
            organization=lead.organization,
            name=f"{lead.company_name} - {lead.name}",
            description=lead.notes or f"Project converted from lead: {lead.name}",
            client_name=lead.name,
            client_company=lead.company_name,
            client_email=lead.email,
            client_phone=lead.phone or '',
            status='NOT_STARTED',
            budget=lead.expected_revenue or 0,
        )
        
        lead.converted_to_project = project
        lead.stage = 'CLOSED_WON'
        lead.save()
        
        messages.success(request, f'Lead converted to project successfully!')
        return redirect('projects:detail', project.id)
    
    return render(request, 'leads_crm/convert_confirm.html', {
        'lead': lead
    })
