# conversations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.contrib.auth.models import User

from .models import Conversation, Message
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http import HttpResponseForbidden
@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(participants=request.user).prefetch_related('messages')
    users = User.objects.exclude(id=request.user.id)  # Exclude the current user from the list
    return render(request, 'conversations/conversation_list.html', {'conversations': conversations, 'users': users})

from django.shortcuts import redirect

@login_required
def conversation_detail(request, conversation_id):
    
    # Retrieve the conversation by its ID
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        file = request.FILES.get('file')

        # Create a new message if content or file is provided
        if content or file:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content,
                file=file
            )

        # Redirect to the same conversation detail page
        return redirect('conversation_detail', conversation_id=conversation.id)

    # Fetch messages in chronological order
    messages = conversation.messages.order_by('timestamp')
    
    # Render the conversation detail template with context
    return render(request, 'conversations/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages
    })

@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    conversation, created = Conversation.objects.get_or_create(participants__in=[request.user, other_user])
    conversation.participants.add(request.user, other_user)
    return redirect('conversation_detail', conversation_id=conversation.id)
    
@login_required
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Check if the current user is a participant in the conversation
    if request.user not in conversation.participants.all():
        return HttpResponseForbidden("You are not authorized to delete this conversation.")

    if request.method == 'POST':
        # Delete the conversation and its related messages
        conversation.delete()
        return redirect('conversation_list')  # Redirect to the conversation list after successful deletion

    return render(request, 'conversations/conversation_confirm_delete.html', {'conversation':conversation})
