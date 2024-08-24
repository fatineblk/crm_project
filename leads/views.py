# leads/views.py
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import Lead
from notifications.models import Notification  # Import Notification from the notifications app
from .forms import LeadForm
from .forms import AssignLeadForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import csv
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
#new
from django.db.models import Count
# Access all leads assigned to a specific user
#assigned_leads = user.assigned_leads.all()
from django.shortcuts import render
# Vue basée sur une classe
from django.views.generic import TemplateView

from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
from notifications.models import Notification  # Import the Notification model

@login_required
def lead_list(request):
    # Get status choices from the Lead model
    status_choices = Lead._meta.get_field('status').choices
    
    # Get filters from the request
    status_filter = request.GET.get('status', 'all')
    created_at_filter = request.GET.get('created_at', None)

    # Print the filters to the console for debugging
    print(f'Status filter: {status_filter}')
    print(f'Created at filter: {created_at_filter}')

    # Count leads for each status
    status_counts = {
        'nouveau': Lead.objects.filter(status='nouveau').count(),
        'Contacté': Lead.objects.filter(status='Contacté').count(),
        'Perdu': Lead.objects.filter(status='Perdu').count(),
    }
    
    # Query leads and apply filters
    leads = Lead.objects.all()

    # Apply status filter
    if status_filter != 'all':
        leads = leads.filter(status=status_filter)
        print(f'Leads after status filter: {leads.count()}')

    # Apply date filter
    if created_at_filter:
        try:
            parsed_date = parse_date(created_at_filter)
            if parsed_date:
                # Filtering for all records where created_at date matches the given date
                leads = leads.annotate(date=TruncDate('created_at')).filter(date=parsed_date)
                print(f'Leads after date filter: {leads.count()}')
        except ValueError:
            print('Invalid date format')

    # Query leads that are pending follow-up (not assigned)
    leads_pending_followup = Lead.objects.filter(assigned_to__isnull=True)
    
    # Print the number of pending follow-up leads
    print(f'Leads pending follow-up: {leads_pending_followup.count()}')

    context = {
        'leads': leads,
        'status_choices': status_choices,
        'created_at_filter': created_at_filter,
        'status_counts': status_counts,
        'leads_pending_followup': leads_pending_followup,
    }
    
    return render(request, 'lead_list.html', context)

































def faq(request):
    return render(request, 'faq.html')

def lead_detail(request, lead_id):
    lead = Lead.objects.get(id=lead_id)
    return render(request, 'lead_detail.html', {'lead': lead})


#modification pour les notifications
@login_required
def lead_add(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.save()

            # Create a notification for the new lead
            Notification.objects.create(
                user=request.user,  # Assuming the notification is for the user who added the lead
                message=f'A new lead "{lead.first_name}" has been added.',  # Customize the message as needed
                type='lead'
            )
            return redirect('lead_actions')
    else:
        form = LeadForm()

    return render(request, 'lead_form.html', {'form': form})
def lead_delete(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    if request.method == 'POST':
        lead.delete()
        return redirect('lead_list')  # Redirection vers la liste des leads après suppression réussie
    return render(request, 'lead_confirm_delete.html', {'lead': lead})
def lead_edit(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect('lead_list')  # Redirection vers la liste des leads après modification réussie
    else:
        form = LeadForm(instance=lead)
    return render(request, 'lead_form.html', {'form': form, 'lead': lead})
def lead_import(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
        except UnicodeDecodeError:
            decoded_file = csv_file.read().decode('latin-1').splitlines()
        
        reader = csv.DictReader(decoded_file)
        
        for row in reader:
            Lead.objects.create(
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone=row['phone'],
                source=row['source'],
                status=row['status'],
                note=row.get('note', ''),
            )
        
        messages.success(request, 'Leads importés avec succès.')
        return redirect('lead_list')

    return render(request, 'lead_import.html')

def lead_api_import(request):
    # Code for API integration to import leads automatically
    return HttpResponse("API Integration for lead import")


@login_required
def lead_assign(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    if not lead.assigned_to and request.user.is_authenticated:
        lead.assigned_to = request.user
        lead.save()
    return redirect('lead_actions')







@login_required
def lead_actions(request):
    leads = Lead.objects.all()

    # Récupérer les paramètres de filtrage
    status_filter = request.GET.get('status')
    created_at_filter = request.GET.get('created_at')

    # Appliquer le filtre de statut
    if status_filter and status_filter != 'all':
        leads = leads.filter(status=status_filter)

    # Appliquer le filtre de date de création
    if created_at_filter:
        try:
            parsed_date = parse_date(created_at_filter)
            if parsed_date:
                # Filtering for all records where created_at date matches the given date
                leads = leads.annotate(date=TruncDate('created_at')).filter(date=parsed_date)
        except ValueError:
            print('Invalid date format')

    return render(request, 'lead_actions.html', {'leads': leads, 'status_filter': status_filter, 'created_at_filter': created_at_filter})




















class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


