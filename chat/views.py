from django.shortcuts import render , redirect
from django.http import HttpResponse
from orders.models import Order
from .models import Chat , Message
from accounts.models import Freelancer , Account
from django.http import JsonResponse , HttpResponseBadRequest
import json

# Create your views here.
def chat(request):
    return HttpResponse("Hello, World!")


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
    get_chat = Chat.objects.filter(user = get_user , freelancer = get_freelancer)
    if get_chat:
        return redirect('chat:inbox' )
    save_chat = Chat(user = get_user , freelancer = get_freelancer)
    save_chat.save()
    return redirect('chat:inbox' )

def get_chat(request , chat_id):
    get_chat = Chat.objects.get(pk = chat_id)
    get_message = Message.objects.filter(chat =get_chat ).order_by('create_at')
    all_chat = Chat.objects.filter(user= request.user.account)
    
    return render(request , 'accounts/inbox.html' , {'user_chat': all_chat , 'message':get_message , 'sender_user': get_chat})

def send_message(request, chat_id):
    try:
        # Ensure request body is not empty
        if not request.body:
            return HttpResponseBadRequest('Empty request body')

        data = json.loads(request.body)
        content = data.get('content')

        # Validate content
        if not content:
            return HttpResponseBadRequest('No content provided')

        # Fetch the chat object
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return JsonResponse({'error': 'Chat not found'}, status=404)

        # Create the message
        get_account = Account.objects.get( user = request.user )
        Message.objects.create(chat=chat, sender=get_account, content=content)
        return JsonResponse({'status': 'Message sent'})

    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')