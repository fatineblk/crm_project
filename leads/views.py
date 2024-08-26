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
from django.utils.dateparse import parse_date
from notifications.models import Notification  # Import the Notification model
from django.http import JsonResponse
from .api_integration import fetch_google_ads_data
@login_required
def lead_list(request):
    # Récupération des filtres de statut et date
    status_filter = request.GET.get('status', '')
    created_at_filter = request.GET.get('created_at', None)

    # Comptage des leads pour chaque statut
    status_counts = {
        'nouveau': Lead.objects.filter(status='nouveau').count(),
        'contacté': Lead.objects.filter(status='contacté').count(),
        'converti': Lead.objects.filter(status='converti').count(),
        'perdu': Lead.objects.filter(status='perdu').count(),
    }

    # Filtrage des leads
    leads_query = Lead.objects.all()
    if status_filter:
        leads_query = leads_query.filter(status=status_filter)
    if created_at_filter:
        try:
            parsed_date = parse_date(created_at_filter)
            if parsed_date:
                leads_query = leads_query.filter(created_at__date=parsed_date)
        except ValueError:
            pass  # Ignore invalid dates

    # Limiter à 4 leads ajoutés aujourd'hui pour l'affichage
    today = timezone.now().date()
    leads_today = leads_query.filter(created_at__date=today).order_by('-created_at')[:4]

    # Nombre total de leads pour la section 'Voir plus'
    total_leads_today = leads_query.filter(created_at__date=today).count()

    # Leads en attente de suivi
    leads_pending_followup = Lead.objects.filter(assigned_to__isnull=True)

    context = {
        'leads': leads_today,
        'status_choices': Lead._meta.get_field('status').choices,
        'status_counts': status_counts,
        'created_at_filter': created_at_filter,
        'leads_pending_followup': leads_pending_followup,
        'total_leads_today': total_leads_today,
    }
    return render(request, 'lead_list.html', context)

   
def faq(request):
    return render(request, 'faq.html')
from django.views.generic import TemplateView

class SupportGuideView(TemplateView):
    template_name = 'support_guide.html'

def lead_detail(request, lead_id):
    lead = Lead.objects.get(id=lead_id)
    return render(request, 'lead_detail.html', {'lead': lead})
from .models import Lead, Interaction
from django.shortcuts import render, redirect
from .models import Lead, Interaction
from .forms import InteractionForm


from django.shortcuts import render, get_object_or_404, redirect
from .models import Lead, Interaction
from .forms import AppelForm, InteractionForm

def interaction_view(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    
    # Récupérer toutes les interactions existantes pour le lead
    interactions_telephonique = Interaction.objects.filter(lead=lead, type='Téléphone')
    interactions_email = Interaction.objects.filter(lead=lead, type='Email')

    # Définir les formulaires à utiliser
    appel_form = None
    interaction_form = None

    if request.method == 'POST':
        if 'appel_form' in request.POST:
            appel_form = AppelForm(request.POST)
            if appel_form.is_valid():
                interaction = appel_form.save(commit=False)
                interaction.lead = lead
                interaction.type = 'Téléphone'  # Assurez-vous que le type est défini
                interaction.save()
                return redirect('interaction_view', lead_id=lead.id)
        else:
            interaction_form = InteractionForm(request.POST)
            if interaction_form.is_valid():
                interaction = interaction_form.save(commit=False)
                interaction.lead = lead
                interaction.save()
                return redirect('interaction_view', lead_id=lead.id)
    else:
        appel_form = AppelForm()
        interaction_form = InteractionForm()

    return render(request, 'lead_interactions.html', {
        'lead': lead,
        'appel_form': appel_form,
        'interaction_form': interaction_form,
        'interactions_telephonique': interactions_telephonique,
        'interactions_email': interactions_email,
    })


#modification pour les notifications
@login_required
def lead_add(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.save()

            # Crée une notification pour le nouveau lead
            Notification.objects.create(
                user=request.user,  # Supposons que la notification est pour l'utilisateur qui a ajouté le lead
                message=f'Un nouveau lead "{lead.Prénom}" a été ajouté.',
                type='lead'
            )
            return redirect('lead_actions')
        else:
            print(form.errors)  # Affiche les erreurs du formulaire pour le débogage
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
    # Récupérer le lead basé sur l'ID
    lead = get_object_or_404(Lead, id=lead_id)

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            # Redirection vers la liste des leads après modification réussie
            return redirect('lead_actions')  # Vous pouvez changer 'lead_actions' si nécessaire
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
    Prénom=row['Prénom'],
    Nom=row['Nom'],
    Email=row['Email'],
    Télephone=row['Télephone'],
    source=row['source'],
    status=row['statut'],
    notes=row.get('notes', ''),
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
    return redirect('lead_list')


def lead_actions(request):
    # Fetch leads or perform any necessary logic here
    leads = Lead.objects.all()  # Adjust the query as needed
    return render(request, 'lead_actions.html', {'leads': leads})


# Access all leads assigned to a specific user
#assigned_leads = user.assigned_leads.all()
from django.shortcuts import render
# Vue basée sur une classe
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


from django.shortcuts import render
from .models import Lead

def dashboard(request):
    # Filtrer les leads non pris en charge et les ordonner par date de création
    leads_pending_followup = Lead.objects.filter(assigned_to__isnull=True).order_by('created_at')[:3]
    context = {
        'leads_pending_followup': leads_pending_followup,
    }
    return render(request, 'dashboard.html', context)

def import_google_ads_leads(request):
    access_token = 'YOUR_GOOGLE_ACCESS_TOKEN'
    data = fetch_google_ads_data(access_token)

    # Exemple d'importation des données
    for item in data.get('results', []):
        Lead.objects.create(
            nom=item.get('ad_group_ad', {}).get('ad', {}).get('name', ''),
            prenom='',
            email='',
            telephone='',
            source='Google Ads',
            status='Nouveau',
            note='',
            # Ajoute les autres champs nécessaires
        )

    return JsonResponse({'status': 'success', 'data': data})

from django.http import JsonResponse
from .models import Lead

def get_lead_statistics(request):
    tasks_accomplished = Lead.objects.filter(contacted=True).count()
    tasks_not_accomplished = Lead.objects.filter(contacted=False).count()
    
    # Ajoutez des statistiques supplémentaires si nécessaire
    data = {
        'tasks_accomplished': tasks_accomplished,
        'tasks_not_accomplished': tasks_not_accomplished,
        'meetings_upcoming': 5,  # Exemple statique, remplacez par des données réelles
        'emails_pending': 8  # Exemple statique, remplacez par des données réelles
    }
    
    return JsonResponse(data)
