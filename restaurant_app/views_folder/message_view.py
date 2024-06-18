from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import json
from django.contrib import messages
from ..models.message import Chat, Message
from ..models.orders import Order
from django.contrib.auth.models import User
from ..forms import MessageForm


@login_required
def inbox(request):
    chats = Chat.objects.filter(participants=request.user)
    return render(request, 'inbox.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    messages_received = chat.messages.all()
    messages_received.filter(read=False).update(read=True)  # Mark all messages as read
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.chat = chat
            message.save()
            return redirect('chat_detail', chat_id=chat.id)
    else:
        form = MessageForm()
    return render(request, 'chat_detail.html', {'chat': chat, 'messages_received': messages_received, 'form': form})

@login_required
def send_message(request, chat_id=None):
    users = User.objects.exclude(username=request.user.username)
    chats = Chat.objects.filter(participants=request.user)
    all_users = User.objects.all()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            if chat_id:
                chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
            else:
                recipient_username = request.POST.get('recipient')
                try:
                    recipient = User.objects.get(username=recipient_username)
                except User.DoesNotExist:
                    messages.error(request, 'Пользователь не найден.')
                    return redirect('send_message')

                chats = Chat.objects.filter(participants=request.user).filter(participants=recipient)
                if chats.exists():
                    chat = chats.first()
                else:
                    chat = Chat.objects.create()
                    chat.participants.add(request.user)
                    chat.participants.add(recipient)

            message.chat = chat
            message.save()
            messages.success(request, 'Сообщение отправлено!')
            return redirect('chat_detail', chat_id=chat.id)
    else:
        form = MessageForm()
    return render(request, 'send_message.html', {'form': form, 'chats': chats, 'users': users, 'all_users': all_users, 'chat_id': chat_id})

@login_required
def chat_with_user(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    chat = Chat.objects.filter(participants=request.user).filter(participants=recipient).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user)
        chat.participants.add(recipient)
    return redirect('chat_detail', chat_id=chat.id)


@login_required
def unread_messages_count(request):
    if request.user.is_authenticated:
        return JsonResponse({'unread_messages_count': Message.unread_count(request.user)})
    return JsonResponse({'unread_messages_count': 0})


@login_required
def delete_selected_messages(request, chat_id):
    if request.method == 'POST':
        message_ids = request.POST.getlist('messages')
        if message_ids:
            Message.objects.filter(id__in=message_ids, chat_id=chat_id, chat__participants=request.user).delete()
    return redirect('chat_detail', chat_id=chat_id)


@login_required
def delete_all_messages(request, chat_id):
    if request.method == 'POST':
        Message.objects.filter(chat_id=chat_id, chat__participants=request.user).delete()
    return redirect('chat_detail', chat_id=chat_id)


@login_required
def send_link_to_paul(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        paul = User.objects.get(username='paul')

        if paul:
            order_url = request.build_absolute_uri(order.get_absolute_url())
            message_body = f"Ссылка на стол: <a href='{order_url}'>{order_url}</a>"
            message = Message.objects.create(
                sender=request.user,
                chat=Chat.objects.filter(participants__in=[request.user, paul]).first(),  # Ensure chat is found or created
                body=message_body
            )
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Пользователь paul не найден'}, status=400)
    else:
        return HttpResponse(status=405)