from django.shortcuts import render, redirect
from django.http import HttpResponse
from orders.models import Order
from .models import Chat, Message
from notifications.views import NotificationService as sendemail
from accounts.models import Freelancer, Account
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.core.paginator import Paginator
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
def chat(request):
    return HttpResponse("Hello, World!")

def get_chat_messages(request, chat_id):
    
    messages = Message.objects.filter(chat_id=chat_id).values('content','sender')

    
    messages_list = list(messages)
    
    return JsonResponse(messages_list, safe=False)

def inbox(request):
    if request.user.account.user_type == 'Customer':
        get_chat = Chat.objects.filter(user= request.user.account)
    elif request.user.account.user_type == 'Freelancer':
        get_chat = Chat.objects.filter(freelancer= request.user.freelancer)
    return render(request, 'accounts/inbox.html' , {'user_chat': get_chat})

def create_chat(request , id_order):
    get_order = Order.objects.get(pk = id_order)
    get_user = Account.objects.get(pk = get_order.customer.id)
    get_freelancer = Freelancer.objects.get(user = request.user)
    try:
        get_chat = Chat.objects.get(user = get_user , freelancer = get_freelancer)
    except:
        get_chat = None
    if get_chat:
        return redirect(reverse('chat:get_chat', kwargs={'chat_id': get_chat.id}) )
    
    get_chat = Chat(user = get_user , freelancer = get_freelancer)
    get_chat.save()
    sendemail.notify_new_chat(get_user , get_order , get_freelancer)
    
    return redirect(reverse('chat:get_chat', kwargs={'chat_id': get_chat.id}) )

def get_chat(request , chat_id):
    get_chat = Chat.objects.get(pk = chat_id)
    get_message = Message.objects.filter(chat =get_chat ).order_by('create_at')
    if request.user.account.user_type == 'Customer':
        all_chat = Chat.objects.filter(user= request.user.account)
    elif request.user.account.user_type == 'Freelancer':
        all_chat = Chat.objects.filter(freelancer= request.user.freelancer)
    
    return render(request , 'accounts/inbox.html' , {'user_chat': all_chat , 'message':get_message , 'sender_user': get_chat})

def send_message(request, chat_id):
    data = json.loads(request.body)
    content = data.get('content')
    chat = Chat.objects.get(id=chat_id)
    Message.objects.create(chat=chat, sender=request.user.account, content=content)
    return JsonResponse({'status': 'Message sent'})

@login_required
def chat_list(request):
    if request.user.account.user_type == 'Customer':
        chats = Chat.objects.filter(user=request.user.account)
    elif request.user.account.user_type == 'Freelancer':
        chats = Chat.objects.filter(freelancer=request.user.freelancer)
    else:
        chats = []
    page_number = request.GET.get('page', 1)
    get_chats = Paginator(chats , 6)
    ChatList = get_chats.get_page(page_number)
    
    return render(request, 'chat/chat_list.html', {'chats': ChatList})
