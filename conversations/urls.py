# conversations/urls.py
from django.urls import path
from . import views
from .views import conversation_detail, delete_conversation
urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('conversations/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('<int:conversation_id>/delete/', delete_conversation, name='delete_conversation'),
]
