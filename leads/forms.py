# leads/forms.py
from django import forms
from .models import Lead
from django.contrib.auth.models import User

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'email', 'phone', 'source', 'status', 'note']

class LeadImportForm(forms.Form):
    csv_file = forms.FileField()



class AssignLeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['assigned_to']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.all()