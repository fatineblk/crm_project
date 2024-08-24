from django.urls import path
from . import views  # This imports views from the leads application
from leads import views as lead_views

urlpatterns = [
    path('leads/list', views.lead_list, name='lead_list'),
    path('<int:lead_id>/', views.lead_detail, name='lead_detail'),
    path('add/', views.lead_add, name='lead_add'),
    path('edit/<int:lead_id>/', views.lead_edit, name='lead_edit'),
    path('delete/<int:lead_id>/', views.lead_delete, name='lead_delete'),
    path('import/', views.lead_import, name='lead_import'),
    path('api/import/', views.lead_api_import, name='lead_api_import'),
    path('assign/<int:lead_id>/', views.lead_assign, name='lead_assign'),
    path('leads/', lead_views.lead_actions, name='lead_actions'),
    path('faq/', views.faq, name='faq'),
]
