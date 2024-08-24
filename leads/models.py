# leads/models.py
from django.db import models
from django.contrib.auth.models import User

class Lead(models.Model):
    
    STATUS_CHOICES = [
        ('nouveau' , 'Nouveau'),
        ('contacté', 'Contacté'),
        ('converti' , 'Converti'),
        ('perdu', 'Perdu'),
    ]
    SOURCE_CHOICES = (
        ('website', 'Site Web'),
        ('advertisement', 'Publicité'),
        ('referral', 'Référence'),
        ('other', 'Autre'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    #user va etre responsable du lead
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
