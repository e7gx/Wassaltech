from django.db import models
from orders.models import Order
from accounts.models import Account
from accounts.models import Freelancer

# Create your models here.




class Chat(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(Freelancer, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chat for Order {self.order} with {self.freelancer}'

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender} in Chat {self.chat}'
