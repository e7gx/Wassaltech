from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
# Create your views here.
def notifications_create_offer(user):
    
    page_html = render_to_string('email/SendMessage.html')
    
    subject = "A message has been received from Freelancer"
    from_email = settings.EMAIL_HOST_USER
    to_email = user.user.email

    email_message = EmailMultiAlternatives(subject, '', from_email, [to_email])
    email_message.attach_alternative(page_html, "text/html")  
    email_message.send()
    return "done send email"

class NotificationService:

    @staticmethod
    def send_email(subject, template_name, context, recipient_list):
        page_html = render_to_string(template_name , context)
        from_email = settings.EMAIL_HOST_USER
        to_email = recipient_list

        email_message = EmailMultiAlternatives(subject, '', from_email, [to_email])
        email_message.attach_alternative(page_html, "text/html")  
        email_message.send()
        

    @staticmethod
    def notify_new_chat(user , order , freelancer):
        subject = 'New Chat Created'
        template_name = 'email/create_chat.html'
        number_order = order.id 
        description_order = order.issue_description
        name_user = user.user.first_name 
        name_freelancer = freelancer.user.first_name 
        context = {
            'freelancer': name_freelancer,
            'user': name_user,
            'name_order':number_order,
            'description_order':description_order,
        }
        recipient_list =  user.user.email
        NotificationService.send_email(subject, template_name, context, recipient_list)

    @staticmethod
    def notify_new_offer(freelancer, order , price):
        subject = 'New Offer on Your Order'
        template_name = 'email/new_offer.html'
        
        context = {
            'name_customer': order.customer.user.first_name,
            'number_order': order.id,
            'description':order.issue_description,
            'price':price
        }
        recipient_list = order.customer.user.email
        NotificationService.send_email(subject, template_name, context, recipient_list)

    @staticmethod
    def notify_order_accepted(offer, order):
        subject = 'Your Order Has Been Accepted'
        template_name = 'email/order_accepted.html'
        context = {
            'freelancer': offer.freelancer.user.first_name,
            'number_order': order.id,
            'name_customer':order.customer.user.first_name,
            
        }
        recipient_list = offer.freelancer.user.email
        NotificationService.send_email(subject, template_name, context, recipient_list)
'''
    @staticmethod
    def notify_ticket_replied(ticket):
        subject = 'Ticket Replied'
        template_name = 'emails/ticket_replied.html'
        context = {
            'ticket': ticket.id,
            'name_user': ticket.ticket_creator.user.first_name,
            
        }
        recipient_list = [user.email]
        NotificationService.send_email(subject, template_name, context, recipient_list)'''