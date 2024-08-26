# conversations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.contrib.auth.models import User

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user)
    users = User.objects.exclude(id=request.user.id)  # Exclude the current user from the list
    return render(request, 'conversations/conversation_list.html', {'conversations': conversations, 'users': users})

@login_required
def conversation_detail(request, user_id):
    # Get the selected user
    selected_user = get_object_or_404(User, id=user_id)

    # Find or create a conversation between the current user and the selected user
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=selected_user).distinct()


    # Handle case where no conversation exists
    if not conversation.exists():
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, selected_user)
    else:
        conversation = conversation.first()
    if request.method == 'POST':
        content = request.POST.get('content')
        file = request.FILES.get('file')
        Message.objects.create(conversation=conversation, sender=request.user, content=content, file=file)

    messages = conversation.messages.order_by('timestamp')
    return render(request, 'conversations/conversation_detail.html', {'conversation': conversation})
    
@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    conversation, created = Conversation.objects.get_or_create(participants__in=[request.user, other_user])
    conversation.participants.add(request.user, other_user)
    return redirect('conversation_detail', conversation_id=conversation.id)
