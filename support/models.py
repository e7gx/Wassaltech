from django.db import models

from accounts.models import Account

# Create your models here.
class Ticket(models.Model):
    
    TICKET_CATEGORYS = (
        ('general', 'General'),
        ('technical', 'Technical'),
        ('billing', 'Billing'),
        ('other', 'Other'),
    )
    class StatusChoices(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'
        
        
    ticket_creator = models.ForeignKey(Account, on_delete=models.CASCADE)
    ticket_title = models.CharField(max_length=255,choices=TICKET_CATEGORYS)
    ticket_description = models.TextField()
    ticket_status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    ticket_created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title