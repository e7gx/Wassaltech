from django.db import models

from accounts.models import Account

# Create your models here.
class Ticket(models.Model):
    
    TICKET_CATEGORYS = (
        ('general', 'General'),
        ('technical', 'Technical'),
        ('billing', 'Billing'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ("feature_request", "Feature Request"),
        ('other', 'Other'),
    )
    class StatusChoices(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        CLOSED = 'closed', 'Closed'
        
    ticket_creator = models.ForeignKey(Account, on_delete=models.CASCADE)
    ticket_category = models.CharField(max_length=255,choices=TICKET_CATEGORYS , default='general')
    ticket_title = models.CharField(max_length=255)
    ticket_description = models.TextField()
    ticket_status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    ticket_created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"{self.ticket_title} - {self.ticket_creator}"
    
    def creator_full_name(self):
        return f"{self.ticket_creator.first_name} {self.ticket_creator.last_name}"


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    comment_creator = models.ForeignKey(Account, on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.comment_creator} on {self.ticket}"